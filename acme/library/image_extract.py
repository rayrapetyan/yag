#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Robert Ayrapetyan <robert.ayrapetyan@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from pathlib import Path

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
version_added: '2.3'
requirements:
- Either 7z (from I(7zip) or I(p7zip) package)
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
  executable:
    description:
    - The path to the executable to use for extracting files from the image.
    type: path
    default: 'depends on image format'
    version_added: '2.4'
notes:
- Only the file checksum (content) is taken into account when extracting files
  from the image. If C(force=no), only checks the presence of the file.
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

import os.path
import shutil

from pathlib import Path
from shlex import quote

from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            image=dict(type='path', required=True, aliases=['path', 'src']),
            dest=dict(type='path', required=True),
            files=dict(type='list', required=False, default=[]),
            force=dict(type='bool', default=True, aliases=['thirsty']),
            executable=dict(type='path'),  # No default on purpose
        ),
        supports_check_mode=True,
    )
    image = module.params['image']
    dest = module.params['dest']
    files = module.params['files']
    force = module.params['force']
    executable = module.params['executable']

    result = dict(
        changed=False,
        dest=dest,
        image=image,
    )

    if Path(image).suffix.lower() == ".iso":

        # We want to know if the user provided it or not, so we set default here
        if executable is None:
            executable = '7z'

        binary = module.get_bin_path(executable, None)

        # When executable was provided and binary not found, warn user !
        if module.params['executable'] is not None and not binary:
            module.warn("Executable '%s' is not found on the system, trying to mount ISO instead." % executable)

        if not os.path.exists(os.path.dirname(image)):
            module.fail_json(msg="ISO image '%s' does not exist" % image)

        if not os.path.exists(dest):
            Path(dest).mkdir(parents=True, exist_ok=True)

        result['files'] = []
        extract_files = list(files)
        if not force:
            # Check if we have to process any files based on existence
            for f in files:
                dest_file = os.path.join(dest, os.path.basename(f))
                if os.path.exists(dest_file):
                    result['files'].append(dict(
                        checksum=None,
                        dest=dest_file,
                        src=f,
                    ))
                    extract_files.remove(f)
        if files and not extract_files:
            module.exit_json(**result)

        file_names = ' '.join([quote(f) for f in extract_files]) if extract_files else ''
        cmd = '%s x "%s" -o"%s" -y %s' % (binary, image, dest, file_names)

    else:
        module.fail_json(msg="Unrecognized image format")

    rc, out, err = module.run_command(cmd)
    if rc != 0:
        result.update(dict(
            cmd=cmd,
            rc=rc,
            stderr=err,
            stdout=out,
        ))
        shutil.rmtree(dest)
        if binary:
            module.fail_json(msg="Failed to extract from ISO image '%s' to '%s'" % (image, dest), **result)

    result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
