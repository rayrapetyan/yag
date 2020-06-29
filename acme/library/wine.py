#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import hashlib
import os
import json
import shutil
import time

import acme.library.utils.pyrandr as randr

from _collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from typing import Dict

from ansible.module_utils.basic import AnsibleModule

DEFAULT_OS_VER = "win7"


def gen_win_reg_file(registry):
    file = '/tmp/patch.reg'
    with open(file, 'w+t') as f:
        f.write("Windows Registry Editor Version 5.00\n\n")
        for k, v in registry.items():
            f.write(f"[{k}]\n")
            for sv in v:
                (subkey, val), = sv.items()
                f.write(f'"{subkey}"="{val}"\n')
            f.write("\n")
    return file


def upd_reg(module: AnsibleModule, prefix: Path, registry):
    reg_file = gen_win_reg_file(registry)
    exec_cmd(module, prefix, f"regedit {reg_file}")


def win_path_to_wine_nix(prefix: Path, win_path: str):
    return Path(prefix / "dosdevices" / win_path.lower().replace("\\", "/"))


def str_in_file(module: AnsibleModule, file_path: Path, line: str) -> bool:
    rc, out, err = module.run_command(f"grep -Fq '{line}' {file_path}")
    return rc == 0


def add_cdrom(module: AnsibleModule, prefix: Path, letter: str, target: Path, replace=True) -> None:
    s = f'"{letter}:"="cdrom"'
    sysreg_path = prefix / "system.reg"
    if not str_in_file(module, sysreg_path, s):
        upd_reg(module, prefix, {
            f"HKEY_LOCAL_MACHINE\\Software\\Wine\\Drives": [{str(letter + ":"): "cdrom"}]
        })
        while not str_in_file(module, sysreg_path, s):
            time.sleep(1)
    drive_path = prefix / "dosdevices" / str(letter + ":")
    if drive_path.exists():
        if not replace:
            raise Exception(f"drive {drive_path} already exist")
        if not drive_path.is_symlink():
            raise Exception(f"drive {drive_path} is not a symlink")
        drive_path.unlink()
    drive_path.symlink_to(target)


def get_overrides_env(module: AnsibleModule, overrides: Dict[str, str]) -> str:
    """
    Output a string of dll overrides usable with WINEDLLOVERRIDES
    See: https://wiki.winehq.org/Wine_User%27s_Guide#WINEDLLOVERRIDES.3DDLL_Overrides
    """
    if not overrides:
        return ""
    override_buckets = OrderedDict(
        [("n,b", []), ("b,n", []), ("b", []), ("n", []), ("d", []), ("", [])]
    )
    for dll, value in overrides.items():
        if not value:
            value = ""
        value = value.replace(" ", "")
        value = value.replace("builtin", "b")
        value = value.replace("native", "n")
        value = value.replace("disabled", "")
        try:
            override_buckets[value].append(dll)
        except KeyError:
            module.warn(f"invalid override value {value}")
            continue

    override_strings = []
    for value, dlls in override_buckets.items():
        if not dlls:
            continue
        override_strings.append("{}={}".format(",".join(sorted(dlls)), value))
    return ";".join(override_strings)


def create_bottle(module: AnsibleModule, prefix: Path, os_ver: str, arch: str = "win32",
                  dll_overrides: Dict[str, str] = {}, install_gecko: bool = False, install_mono: bool = False) -> None:
    if not install_gecko:
        dll_overrides["mshtml"] = "d"
    if not install_mono:
        dll_overrides["mscoree"] = "d"

    binary = module.get_bin_path("wineboot", None)
    if not binary:
        module.fail_json(msg="can't find wine binary, please install wine first")

    prefix.parent.mkdir(parents=True, exist_ok=True)

    wine_env = {
        "WINEARCH": arch,
        "WINEPREFIX": str(prefix),
        "WINEDLLOVERRIDES": get_overrides_env(module, dll_overrides),
    }
    rc, out, err = module.run_command(binary, environ_update=wine_env)
    if rc != 0:
        module.fail_json(msg=f"failed to create a wine bottle: {rc, out, err}")

    system_reg_path = Path(prefix) / "system.reg"
    for loop_index in range(50):
        if system_reg_path.exists():
            break
        if loop_index == 20:
            module.warn("wine prefix creation is taking longer than expected...")
        time.sleep(0.25)
    if not system_reg_path.exists():
        module.warn("no system.reg found after prefix creation. Prefix might be invalid")
        return

    if os_ver != DEFAULT_OS_VER:
        binary = module.get_bin_path("winetricks", None)
        if not binary:
            module.fail_json(msg="can't find winetricks binary, please install winetricks first")
        module.run_command([binary, os_ver], environ_update=wine_env)


def exec_cmd(module: AnsibleModule, prefix: Path, exec_cmd_line: str, virtual_desktop: str = None):
    wine_binary = module.get_bin_path("wine", None)
    if not wine_binary:
        module.fail_json(msg="can't find wine binary, please install it first")
    wine_env = {
        "WINEPREFIX": str(prefix)
    }
    exec_cmd_arr = exec_cmd_line.split(" ")
    exec_path = Path(exec_cmd_arr[0])
    exec_folder = str(exec_path.parent)
    exec_file = str(exec_path.name)
    cmd_line = [wine_binary]
    if virtual_desktop:
        cmd_line.append("explorer")
        cmd_line.append(f"/desktop=mydesktop,{virtual_desktop}")
    cmd_line.append(exec_file)
    cmd_line += exec_cmd_arr[1:]
    rc, out, err = module.run_command(cmd_line, environ_update=wine_env, cwd=exec_folder)
    return rc, out, err


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            recipe=dict(type='dict', required=False, default={}),
            exec=dict(type='raw', required=False, default=None),
            virtual_desktop=dict(type='str', required=False, default=None),
            cdrom=dict(type='dict', required=False, default=None),
            registry=dict(type='dict', required=False, default=None),
            state=dict(type='str', required=False, choices=["present", "absent"], default="present")
        ),
        supports_check_mode=True
    )

    """
    bodega=dict(type='path', required=True),
    arch=dict(type='str', required=False, default="win32"),
    dll_overrides=dict(type='dict', required=False, default={}),
    install_gecko=dict(type='bool', required=False, default=False),
    install_mono=dict(type='bool', required=False, default=False),
    os_ver=dict(type='str', required=False, default="win7"),
    virtual_desktop=dict(type='str', required=False, default=None),
    """

    result = {
        "changed": False,
        "prefix": ""
    }
    if module.check_mode:
        module.exit_json(**result)

    bottle_recipe = deepcopy(module.params['recipe'])
    bodega = bottle_recipe.get("bodega", os.getenv("WINE_BODEGA", default=str(Path.home() / "wine_bodega")))
    os_ver = bottle_recipe.get("os_ver", DEFAULT_OS_VER)
    if "os_ver" not in bottle_recipe:
        bottle_recipe["os_ver"] = os_ver

    hash = hashlib.md5((bodega + json.dumps(bottle_recipe, sort_keys=True)).encode()).hexdigest()
    prefix = Path(bodega) / hash
    result["prefix"] = str(prefix)
    if prefix.exists():
        if module.params["state"] == "absent":
            shutil.rmtree(prefix)
            result["changed"] = True
    else:
        if module.params["state"] == "present":
            create_bottle(module, prefix, os_ver)
            result["changed"] = True

    int_apps_folder = bottle_recipe.get("int_apps_folder", os.getenv("WINE_APPS_FOLDER"))
    ext_apps_folder = bottle_recipe.get("ext_apps_folder", os.getenv("APPS_FOLDER"))
    if int_apps_folder and ext_apps_folder:
        wine_nix_path = win_path_to_wine_nix(prefix, int_apps_folder)
        if not wine_nix_path.exists():
            wine_nix_path.symlink_to(ext_apps_folder, target_is_directory=True)

    cdrom = module.params["cdrom"]
    if cdrom:
        add_cdrom(module, prefix, cdrom["letter"], Path(cdrom["target"]))

    registry = module.params["registry"]
    if registry:
        upd_reg(module, prefix, registry)

    if module.params["exec"]:
        virtual_desktop = module.params.get("virtual_desktop")
        if virtual_desktop:
            screen = randr.connected_screens()[0]
            screen.set_resolution(tuple([int(x) for x in virtual_desktop.split("x")]))
            screen.apply_settings()

        cmd_line = module.params["exec"]
        if isinstance(cmd_line, str):
            cmd_line = [cmd_line]
        for cl in cmd_line:
            rc, out, err = exec_cmd(module, prefix, cl, virtual_desktop)
            #if rc != 0:
                #module.fail_json(msg=f"failed to run: {rc, out, err}")

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
