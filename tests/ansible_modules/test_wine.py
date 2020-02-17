import os
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
    wine,
)

WINE_BODEGA = Path("~/yag/tmp/test/bodega").expanduser()
WINE_BOTTLE_PREFIX = WINE_BODEGA / "e81a9e38d879fff0993b2ff6c2b032b8"
WINE_RECIPE = {
    'foo': "bar"
}

os.environ["WINE_BODEGA"] = str(WINE_BODEGA)


def test_invalid_arg(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({
            'recipe': WINE_RECIPE,
            'fooooooooooooo': True
        })
        wine.main()


def test_present(mock_ansible_module):
    shutil.rmtree(WINE_BOTTLE_PREFIX, ignore_errors=True)
    assert (not WINE_BOTTLE_PREFIX.exists())

    set_module_args({
        'recipe': WINE_RECIPE,
        'state': 'present'
    })
    with pytest.raises(AnsibleExitJson) as result:
        wine.main()
    result = result.value.args[0]
    assert (result['changed'])
    assert (result["prefix"] == str(WINE_BOTTLE_PREFIX))
    assert ((WINE_BOTTLE_PREFIX / "system.reg").exists())

    with pytest.raises(AnsibleExitJson) as result:
        wine.main()
    result = result.value.args[0]
    assert (not result['changed'])
    assert (result["prefix"] == str(WINE_BOTTLE_PREFIX))
    assert (WINE_BOTTLE_PREFIX.exists())


def test_absent(mock_ansible_module):
    shutil.rmtree(WINE_BOTTLE_PREFIX, ignore_errors=True)
    assert (not WINE_BOTTLE_PREFIX.exists())

    set_module_args({
        'recipe': WINE_RECIPE,
        'state': 'absent'
    })
    with pytest.raises(AnsibleExitJson) as result:
        wine.main()
    result = result.value.args[0]
    assert (not result['changed'])
    assert (result["prefix"] == str(WINE_BOTTLE_PREFIX))
    assert (not WINE_BOTTLE_PREFIX.exists())

    WINE_BOTTLE_PREFIX.mkdir(parents=True)
    assert (WINE_BOTTLE_PREFIX.exists())

    with pytest.raises(AnsibleExitJson) as result:
        wine.main()
    result = result.value.args[0]
    assert (result['changed'])
    assert (result["prefix"] == str(WINE_BOTTLE_PREFIX))
    assert (not WINE_BOTTLE_PREFIX.exists())
