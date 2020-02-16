#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import os

from ansible.module_utils.basic import AnsibleModule


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            config=dict(type='path', required=False, default=os.getenv("SCUMMVM_CONF_PATH", default="~/scummvm.ini")),
            game=dict(type='str', required=True),
            path=dict(type='path', required=False, default=os.getenv("APP_FOLDER")),
            savepath=dict(type='path', required=False, default=os.getenv("DATA_FOLDER"))
        ),
        supports_check_mode=True
    )
    if module.check_mode:
        module.exit_json()

    binary = module.get_bin_path("scummvm", None)
    if not binary:
        module.fail_json(msg="can't find binary, please install it first")

    cmd = [
        binary,
        f"--config={module.params['config']}",
        f"--game={module.params['game']}",
        f"--path={module.params['path']}",
        f"--savepath={module.params['savepath']}",
        "--auto-detect"
    ]

    module.debug(f"running: {str(cmd)}")
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg=f"failed to run scummvm: {rc, out, err}")

    module.exit_json()


def main():
    run_module()


if __name__ == '__main__':
    main()
