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
    wine,
)

WINE_RECIPE = {
    'foo': 'bar',
}
WINE_RECIPE_HASH = wine.recipe_hash(WINE_RECIPE)


def test_invalid_arg(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({
            'recipe': WINE_RECIPE,
            'fooooooooooooo': True
        })
        wine.main()


def test_present(mock_ansible_module):
    with tempfile.TemporaryDirectory() as wine_bodega:
        os.environ["WINE_BODEGA"] = wine_bodega
        wine_bodega_path = Path(wine_bodega)
        wine_bottle_prefix = wine_bodega_path / WINE_RECIPE_HASH

        set_module_args({
            'recipe': WINE_RECIPE,
            'state': 'present'
        })
        with pytest.raises(AnsibleExitJson) as result:
            wine.main()
        result = result.value.args[0]
        assert (result['changed'])
        assert (result["prefix"] == str(wine_bottle_prefix))
        assert ((wine_bottle_prefix / "system.reg").exists())

        with pytest.raises(AnsibleExitJson) as result:
            wine.main()
        result = result.value.args[0]
        assert (not result['changed'])
        assert (result["prefix"] == str(wine_bottle_prefix))
        assert (wine_bottle_prefix.exists())


def test_absent(mock_ansible_module):
    with tempfile.TemporaryDirectory() as wine_bodega:
        os.environ["WINE_BODEGA"] = wine_bodega
        wine_bodega_path = Path(wine_bodega)
        wine_bottle_prefix = wine_bodega_path / WINE_RECIPE_HASH

        set_module_args({
            'recipe': WINE_RECIPE,
            'state': 'absent'
        })
        with pytest.raises(AnsibleExitJson) as result:
            wine.main()
        result = result.value.args[0]
        assert (not result['changed'])
        assert (result["prefix"] == str(wine_bottle_prefix))
        assert (not wine_bottle_prefix.exists())

        wine_bottle_prefix.mkdir(parents=True)
        assert (wine_bottle_prefix.exists())

        with pytest.raises(AnsibleExitJson) as result:
            wine.main()
        result = result.value.args[0]
        assert (result['changed'])
        assert (result["prefix"] == str(wine_bottle_prefix))
        assert (not wine_bottle_prefix.exists())
