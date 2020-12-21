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
    image_extract,
)

BASE_PATH = Path(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

ISO_IMAGE_PATH = BASE_PATH / "data" / "fdbootcd.iso"
ISO_IMAGE_FILES = ['[BOOT]', 'boot.catalog', 'fdos2040.img']
BIN_IMAGE_PATH = BASE_PATH / "data" / "fdbootcd.bin"
BIN_IMAGE_FILES = ISO_IMAGE_FILES


def test_invalid_arg(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({
            'image': ISO_IMAGE_PATH,
            'dest': '/',
            'fooooooooooooo': True
        })
        image_extract.main()


def test_required_arg_missing(mock_ansible_module):
    with pytest.raises(AnsibleFailJson):
        set_module_args({})
        image_extract.main()


def test_extract_iso_all_files(mock_ansible_module):
    with tempfile.TemporaryDirectory() as dest:
        dest_path = Path(dest)
        assert(ISO_IMAGE_PATH.exists())

        set_module_args({
            'image': ISO_IMAGE_PATH,
            'dest': dest_path,
        })

        with pytest.raises(AnsibleExitJson) as result:
            image_extract.main()
        result = result.value.args[0]
        assert (result['changed'])
        for f in ISO_IMAGE_FILES:
            assert ((dest_path / f).exists())

        set_module_args({
            'image': ISO_IMAGE_PATH,
            'dest': dest_path,
            'files': ISO_IMAGE_FILES,
            'force': False,
        })

        with pytest.raises(AnsibleExitJson) as result:
            image_extract.main()
        result = result.value.args[0]
        assert (not result['changed'])
        assert (dest_path.exists())


def test_extract_iso_custom_files(mock_ansible_module):
    with tempfile.TemporaryDirectory() as dest:
        dest_path = Path(dest)
        assert(ISO_IMAGE_PATH.exists())

        set_module_args({
            'image': ISO_IMAGE_PATH,
            'dest': dest_path,
            'files': ISO_IMAGE_FILES[:2],
        })

        with pytest.raises(AnsibleExitJson) as result:
            image_extract.main()
        result = result.value.args[0]
        assert (result['changed'])
        assert ((dest_path / ISO_IMAGE_FILES[0]).exists())
        assert ((dest_path / ISO_IMAGE_FILES[1]).exists())
        assert (not (dest_path / ISO_IMAGE_FILES[2]).exists())


def test_extract_bin_image(mock_ansible_module):
    with tempfile.TemporaryDirectory() as dest:
        dest_path = Path(dest)
        assert(BIN_IMAGE_PATH.exists())

        set_module_args({
            'image': BIN_IMAGE_PATH,
            'dest': dest_path,
        })

        with pytest.raises(AnsibleExitJson) as result:
            image_extract.main()
        result = result.value.args[0]
        assert (result['changed'])
        for f in BIN_IMAGE_FILES:
            assert ((dest_path / f).exists())

        set_module_args({
            'image': BIN_IMAGE_PATH,
            'dest': dest_path,
            'files': BIN_IMAGE_FILES,
            'force': False,
        })

        with pytest.raises(AnsibleExitJson) as result:
            image_extract.main()
        result = result.value.args[0]
        assert (not result['changed'])
        assert (dest_path.exists())
