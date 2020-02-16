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
    wine_bottle,
)

WINE_BODEGA = Path("~/yag/tmp/test/bodega").expanduser()
WINE_BOTTLE_PREFIX = WINE_BODEGA / "8043a2d0213fc8a7a13d686af60b6b43"


def test_invalid_arg(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({
            'recipe': {
                'bodega': WINE_BODEGA,
                'fooooooooooooo': True
            }
        })
        wine_bottle.main()


def test_required_arg_missing(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({})
        wine_bottle.main()


def test_present(mock_ansible_module):
    shutil.rmtree(WINE_BOTTLE_PREFIX, ignore_errors=True)
    assert (not WINE_BOTTLE_PREFIX.exists())

    set_module_args({
        'recipe': {
            'bodega': WINE_BODEGA,
            'state': 'present'
        }
    })
    with pytest.raises(AnsibleExitJson) as result:
        wine_bottle.main()
    result = result.value.args[0]
    assert (result['changed'])
    assert (result["prefix"] == str(WINE_BOTTLE_PREFIX))
    assert ((WINE_BOTTLE_PREFIX / "system.reg").exists())

    with pytest.raises(AnsibleExitJson) as result:
        wine_bottle.main()
    result = result.value.args[0]
    assert (not result['changed'])
    assert (result["prefix"] == str(WINE_BOTTLE_PREFIX))
    assert (WINE_BOTTLE_PREFIX.exists())


def test_absent(mock_ansible_module):
    shutil.rmtree(WINE_BOTTLE_PREFIX, ignore_errors=True)
    assert (not WINE_BOTTLE_PREFIX.exists())

    set_module_args({
        'recipe': {
            'bodega': WINE_BODEGA,
            'state': 'absent'
        }
    })
    with pytest.raises(AnsibleExitJson) as result:
        wine_bottle.main()
    result = result.value.args[0]
    assert (not result['changed'])
    assert (result["prefix"] == str(WINE_BOTTLE_PREFIX))
    assert (not WINE_BOTTLE_PREFIX.exists())

    WINE_BOTTLE_PREFIX.mkdir(parents=True)
    assert (WINE_BOTTLE_PREFIX.exists())

    with pytest.raises(AnsibleExitJson) as result:
        wine_bottle.main()
    result = result.value.args[0]
    assert (result['changed'])
    assert (result["prefix"] == str(WINE_BOTTLE_PREFIX))
    assert (not WINE_BOTTLE_PREFIX.exists())
