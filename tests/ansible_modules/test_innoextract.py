import pytest
import shutil

from pathlib import Path

from helpers import (
    AnsibleExitJson,
    AnsibleFailJson,
    mock_ansible_module,
    set_module_args,
)

from acme.library import (
    innoextract,
)

DEST_PATH = Path("~/yag/tmp/test/innoextract").expanduser()
INSTALLER = Path("tests/data/innosetup-6.0.3.exe")
CREATES_PATH = DEST_PATH / "app" / "ISCC.exe"


def test_invalid_arg(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({
            'installer': INSTALLER,
            'dest': DEST_PATH,
            'fooooooooooooo': True
        })
        innoextract.main()


def test_required_arg_missing(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({})
        innoextract.main()


def test_extract(mock_ansible_module):
    shutil.rmtree(DEST_PATH, ignore_errors=True)
    assert (not DEST_PATH.exists())

    assert(INSTALLER.exists())

    set_module_args({
        'installer': INSTALLER,
        'dest': DEST_PATH,
        'creates': CREATES_PATH
    })
    with pytest.raises(AnsibleExitJson) as result:
        innoextract.main()
    result = result.value.args[0]
    assert (result['changed'])
    assert (CREATES_PATH.exists())

    with pytest.raises(AnsibleExitJson) as result:
        innoextract.main()
    result = result.value.args[0]
    assert (not result['changed'])
    assert (CREATES_PATH.exists())
