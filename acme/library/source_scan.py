#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

from pathlib import Path

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


try:
    from ansible.module_utils.source import (
        get,
        Image,
        Installer,
    )
except ImportError:  # unit test
    from acme.library.utils.source import (
        get,
        Image,
        Installer,
    )


def conv_vals_to_str(dct):
    for k, v in dct.items():
        if isinstance(v, dict):
            dct[k] = conv_vals_to_str(v)
        elif isinstance(v, list):
            dct[k] = [str(x) for x in v]
        elif not isinstance(v, str):
            dct[k] = str(v)
    return dct


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='raw', required=True)
        ),
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json()

    result = {
        "changed": False
    }

    path = module.params["path"]
    path = [Path(x) for x in path] if isinstance(path, list) else Path(path)
    source_inst = get(path)
    if isinstance(source_inst, Installer):
        result["installer"] = conv_vals_to_str(vars(source_inst))
    elif isinstance(source_inst, Image):
        result["image"] = conv_vals_to_str(vars(source_inst))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
