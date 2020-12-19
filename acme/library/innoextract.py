#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from pathlib import Path

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            installer=dict(type='path', required=True),
            dest=dict(type='path', required=True),
            creates=dict(type='path', required=True),
            gog=dict(type=bool, required=False, default=False)
        ),
        supports_check_mode=True
    )
    result = {
        "changed": False
    }
    if module.check_mode:
        module.exit_json(**result)

    if Path(module.params["creates"]).exists():
        module.exit_json(**result)

    binary = module.get_bin_path("innoextract", None)
    if not binary:
        module.fail_json(msg="can't find binary, please install it first")

    dest = Path(module.params["dest"])
    dest.mkdir(parents=True, exist_ok=True)

    installer = Path(module.params["installer"])
    if not installer.exists():
        module.fail_json(msg="can't find installer")

    cmd_args = [binary, "--extract"]
    if module.params["gog"]:
        cmd_args += ["--exclude-temp", "--gog"]
    cmd_args += ["--output-dir", str(dest)]
    cmd_args.append(str(installer))
    rc, out, err = module.run_command(cmd_args)
    if rc != 0:
        module.fail_json(msg=f"failed to extract: {rc, out, err}")

    if not Path(module.params["creates"]).exists():
        module.fail_json(msg=f"extracted archive doesn't contain expected file: {module.params['creates']}, installer might be corrupted")

    result["changed"] = True

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
