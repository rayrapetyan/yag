#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Robert Ayrapetyan <robert.ayrapetyan@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import shutil
import tempfile

from pathlib import Path
from shlex import quote

from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
author:
- Robert Ayrapetyan (@rayrapetyan)
module: image_extract
short_description: Extract files from a CD image
description:
- This module supports following image formats:
- ISO: 7zip is used for unpack
- NRG, MDF, PDI, CDI, BIN, CUE, B5I: iat is used for ISO conversion
version_added: '2.3'
requirements:
- Either 7z (from I(7zip) or I(p7zip) package)
- iat from iat package
options:
  image:
    description:
    - The CD image to extract files from.
    type: path
    required: yes
    aliases: [ path, src ]
  dest:
    description:
    - The destination directory to extract files to.
    type: path
    required: yes
  files:
    description:
    - A list of files\directories to extract from the image.
    type: list
    required: no
  force:
    description:
    - If C(yes), which will replace the remote file when contents are different than the source.
    - If C(no), the file will only be extracted and copied if the destination does not already exist.
    type: bool
    default: yes
    version_added: '2.4'
'''

EXAMPLES = r'''
- name: Extract kernel and ramdisk from a LiveCD
  image_extract:
    image: /tmp/rear-test.iso
    dest: /tmp/virt-rear/
    files:
    - isolinux/kernel
    - isolinux/initrd.cgz
'''

RETURN = r'''
#
'''

def run_7z(module, src, dest, extract_files=None):
    file_names = ' '.join([quote(f) for f in extract_files]) if extract_files else ''
    bin = module.get_bin_path('7z', None)
    cmd = f'{bin} x "{src}" -o"{dest}" -y {file_names}'
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        result = dict(
            cmd=cmd,
            rc=rc,
            stderr=err,
            stdout=out,
            changed=False
        )
        shutil.rmtree(dest)
        module.fail_json(msg=f"Failed to extract from ISO image '{src}' to '{dest}'", **result)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            image=dict(type='path', required=True, aliases=['path', 'src']),
            dest=dict(type='path', required=True),
            files=dict(type='list', required=False, default=[]),
            force=dict(type='bool', default=True, aliases=['thirsty']),
        ),
        supports_check_mode=True,
    )
    image = Path(module.params['image'])
    dest = Path(module.params['dest'])
    files = module.params['files']
    force = module.params['force']

    result = dict(
        changed=False,
        dest=dest,
        image=image,
    )

    if not Path(image).exists():
        module.fail_json(msg=f"image '{image}' does not exist")

    if not Path(dest).exists():
        Path(dest).mkdir(parents=True, exist_ok=True)

    result['files'] = []
    extract_files = list(files)
    if not force:
        # Check if we have to process any files based on existence
        for f in files:
            dest_file = dest / f
            if dest_file.exists():
                result['files'].append(dict(
                    checksum=None,
                    dest=dest_file,
                    src=f,
                ))
                extract_files.remove(f)
    if files and not extract_files:
        module.exit_json(**result)

    image_format = image.suffix.lower()

    if image_format == ".iso":
        run_7z(module, image, dest, extract_files)
    elif image_format in ['.nrg', '.mdf', '.pdi', '.cdi', '.bin', '.cue', '.b5i']:
        # create intermediate ISO
        with tempfile.TemporaryDirectory() as td:
            iso_image = Path(td) / "tmp.iso"
            bin = module.get_bin_path('iat', None)
            cmd = f'{bin} -i {image} -o {iso_image} --iso'
            rc, out, err =  module.run_command(cmd)
            if rc != 0:
                result.update(dict(
                    cmd=cmd,
                    rc=rc,
                    stderr=err,
                    stdout=out,
                ))
                module.fail_json(msg=f"Failed to convert image '{image}' to ISO", **result)
            run_7z(module, iso_image, dest, extract_files)
    else:
        module.fail_json(msg=f"Unrecognized image format: {image_format}")

    result['changed'] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()
