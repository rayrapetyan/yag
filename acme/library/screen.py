#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule

try:
    import ansible.module_utils.pyrandr as randr
except ImportError:  # unit test
    import acme.library.utils.pyrandr as randr

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            resolution=dict(type='list', required=False),
            brightness=dict(type='int', required=False)
        ),
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json()

    result = {
        "changed": False
    }

    resolution = module.params["resolution"]
    brightness = module.params["brightness"]

    screen = randr.main_screen()
    if screen is None:
        result["changes"] = False
        module.exit_json(**result)

    if resolution or brightness:
        if resolution:
            screen.set_resolution(tuple([int(x) for x in resolution]))
        if brightness:
            screen.set_brightness(brightness)
        screen.apply_settings()
        result["changes"] = True

    height = screen.curr_mode.height
    width = screen.curr_mode.width
    result["resolution"] = (width, height)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
