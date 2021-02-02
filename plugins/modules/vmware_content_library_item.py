#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Ansible Project
# Copyright: (c) 2021, VMware Inc.
# Copyright: (c) 2021, Joe Zollo <jzollo@vmware.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: vmware_content_library_item
short_description: Create a library item from a virtual machine.
description:
  - Creates a library item in content library from a virtual machine or
    virtual appliance (vApp).
  - Content Library feature is introduced in vSphere 6.0 version, so this
    module is not supported in the earlier versions of vSphere.
  - All variables and VMware object names are case sensitive.
author: Joe Zollo (@zollo)
notes:
  - Tested on vSphere 6.7, 7.0
requirements:
  - python >= 2.6
  - PyVmomi
  - vSphere Automation SDK
options:
    moid:
      description:
        - Managed object reference ID of the virtual machine or
          virtual appliance (vApp).
      type: str
      required: true
    type:
      description:
        - Defines the OVF source type.
      choices: [ VirtualMachine, VirtualApp ]
      default: VirtualMachine
      type: str
      required: true
    library_id:
      description:
        - Defines the destination content library ID.
      type: str
      required: true
extends_documentation_fragment:
  - community.vmware.vmware_rest_client.documentation
'''

EXAMPLES = r'''
- name: Publish VM to Content Library
  community.vmware.vmware_content_library_item:
    hostname: '{{ vcenter_hostname }}'
    username: '{{ vcenter_username }}'
    password: '{{ vcenter_password }}'
    moid: vm-1289
    type: VirtualMachine
    library_id: 13b0f060-f4d3-4f84-b61f-0fe1b0c0a5a8
  delegate_to: localhost
'''

RETURN = r'''
library_item_details:
  description: Details on the library item that was created or updated
  returned: on success
  type: dict
  sample:
    {
        "library_item_name": "thename",
        "library_item_content_version": "",
        "library_item_library_id": "",
        "library_item_creation_time": "2019-07-02T11:50:52.242000",
        "library_item_description": "new description",
        "library_item_id": "13b0f060-f4d3-4f84-b61f-0fe1b0c0a5a8",
        "library_item_last_modified_time": "2019-07-02T11:50:52.242000",
        "library_item_last_sync_time": "2019-07-02T11:50:52.242000",
        "library_item_metadata_version": "3",
        "library_item_cached": true,
        "library_item_size": 218379182371,
        "library_item_type": "LOCAL",
        "library_item_version": "3",
        "library_item_source_id": ""
      }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.vmware.plugins.module_utils.vmware_rest_client import VmwareRestClient


class VmwareContentLibItem(VmwareRestClient):
    def __init__(self, module):
        """Constructor."""
        super(VmwareContentLibItem, self).__init__(module)
        self.client = self.api_client
        self.library_item_details = []

    def get_content_lib_item_model(self, library_item):
        """Method to generate a dict containing library item details."""
        model = dict(
            library_id="",
            library_item_id="",
            library_item_content_version="",
            library_item_creation_time="",
            library_item_description="",
            library_item_last_modified_time="",
            library_item_last_sync_time="",
            library_item_metadata_version="",
            library_item_name="",
            library_item_cached="",
            library_item_size="",
            library_item_type="",
            library_item_version="",
            library_item_source_id=""
        )

        self.module.exit_json(exists=False,
                              changed=False,
                              library_item_details=get_content_lib_item_model())
        return model

    def get_content_lib_item_details(self, library_item_id):
        """Method to retreive detais on a specific library item."""
        return self.client.content.library_client.get(library_item_id)

    def get_content_lib_items(self, library_id):
        """Method to retreive list of items in a specific content library."""
        return self.client.content.library_client.list(library_id)




    def create_content_lib_item(self, src_vmid, library_id, description=""):
        """Method to create a new library item in the specified content library."""

        # build spec
        spec = self.client.vcenter.vm_template_client.LibraryItems.CreateSpec(
          source_vm=None,
          name=None,
          description=description,
          library=library_id
        )


        x = self.client.vcenter.ovf_client.create(spec)

        try:
            if update:
                self.library_service.update(library_id, spec)
                action = "updated"
            else:
                library_id = self.library_service.create(
                    create_spec=spec,
                    client_token=str(uuid.uuid4())
                )
                action = "created"
        except ResourceInaccessible as e:
            message = ("vCenter Failed to make connection to %s with exception: %s "
                        "If using HTTPS, check that the SSL thumbprint is valid" % (self.subscription_url, str(e)))
            self.module.fail_json(msg=message)

  
        try:
            lib_details = self.item_service.content.LocalLibrary.get(library_id)
        except Exception as e:
            self.module.fail_json(exists=False, msg="%s" % self.get_error_message(e))


def main():
    argument_spec = VmwareRestClient.vmware_client_argument_spec()
    argument_spec.update(
        moid=dict(type='str', required=True),
        type=dict(type='str', required=False, choices=list('VirtualMachine', 'VirtualApp')),
        library_id=dict(type='str', required=True)
    )
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    vmware_content_lib_item = VmwareContentLibItem(module)

    # payload = {
    #   "source": {
    #       "id": "obj-103",
    #       "type": "VirtualMachine"
    #   },
    #   "target": {
    #       "library_id": "obj-103",
    #       "library_item_id": "obj-103"
    #   }
    # }

    # if module.params.get('dest_library_id'):
    #     vmware_contentlib_info.get_content_lib_details(module.params['library_id'])
    # else:
    #     vmware_contentlib_info.get_all_content_libs()


if __name__ == '__main__':
    main()