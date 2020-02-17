import json
import pytest

from pathlib import Path

from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes

class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args}, cls=JsonEncoder)
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


@pytest.fixture
def mock_ansible_module(monkeypatch):
    def exit_json(*args, **kwargs):
        if 'changed' not in kwargs:
            kwargs['changed'] = False
        raise AnsibleExitJson(kwargs)

    def fail_json(*args, **kwargs):
        kwargs['failed'] = True
        raise AnsibleFailJson(kwargs)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)
