import os
import pytest
import tempfile

from pathlib import Path

from helpers import (
    set_module_args,
)

from tests.conftest import (
    AnsibleExitJson,
    AnsibleFailJson,
)

from acme.library import (
    innoextract,
)

BASE_PATH = Path(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
INSTALLER = BASE_PATH / "data" / "innosetup-6.0.3.exe"


def test_invalid_arg(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({
            'installer': INSTALLER,
            'dest': '/',
            'fooooooooooooo': True
        })
        innoextract.main()


def test_required_arg_missing(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({})
        innoextract.main()


def test_extract(mock_ansible_module):
    with tempfile.TemporaryDirectory() as dest:
        dest_path = Path(dest)
        creates_path = dest_path / "app" / "ISCC.exe"

        assert(INSTALLER.exists())

        set_module_args({
            'installer': INSTALLER,
            'dest': dest_path,
            'creates': creates_path
        })
        with pytest.raises(AnsibleExitJson) as result:
            innoextract.main()
        result = result.value.args[0]
        assert (result['changed'])
        assert (creates_path.exists())

        with pytest.raises(AnsibleExitJson) as result:
            innoextract.main()
        result = result.value.args[0]
        assert (not result['changed'])
        assert (creates_path.exists())
