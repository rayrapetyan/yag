#!/usr/bin/python

import os

from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            config=dict(type='path', required=False, default=os.getenv("DOSBOX_CONF_PATH", default="~/dosbox.conf")),
            exec=dict(type='str', required=True),
            mount=dict(type='list', required=False)
        ),
        supports_check_mode=True
    )
    if module.check_mode:
        module.exit_json()

    binary = module.get_bin_path("dosbox", None)
    if not binary:
        module.fail_json(msg="can't find binary, please install dosbox first")

    cmd = [
        binary,
        f"{module.params['exec']}",
        f"-conf={module.params['config']}",
        "-fullscreen",
        "-exit",
    ]

    mounts = module.params["mount"]
    if mounts:
        cmd.append("-c")
        mount_cmd = ["MOUNT D"]
        for m in mounts:
            mount_cmd.append(m)
        mount_cmd.append("-t cdrom")
        cmd.append(" ".join(mount_cmd))  # cmd with spaces should be appended as a whole string

    module.debug(f"running: {str(cmd)}")
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg=f"failed to run dosbox: {rc, out, err}")

    module.exit_json()


def main():
    run_module()


if __name__ == '__main__':
    main()
