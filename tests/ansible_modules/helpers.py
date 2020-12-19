import json

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
