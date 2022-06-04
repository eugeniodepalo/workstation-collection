#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
from email.policy import default
import json
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ws_1password_cli_get
short_description: Get credentials from 1password CLI
version_added: "1.0.0"
description: Module to get credentials from 1password CLI.

options:
    token:
        description: The token for the account.
        required: true
        type: str
    name:
        description: The name of the item to get.
        required: true
        type: str
    fields:
        description: The fields to get.
        required: true
        type: list
        items: str
        default: ['username', 'password']

author:
    - Eugenio Depalo (@eugeniodepalo)
'''

RETURN = """
  fields:
    description: The fields returned by the 1password CLI.
    type: dict
    elements: str
"""

EXAMPLES = r'''
# Get username from 1password.com
- name: Get credentials from 1password.com
  eugeniodepalo.workstation.ws_1password_cli_get:
    token: 123456789
    name: My 1Password item
    fields: ['username', 'password']
'''


def run_module():
    module_args = dict(
        token=dict(type='str', required=True),
        name=dict(type='str', required=True),
        fields=dict(type='list', elements='str',
                    default=['username', 'password'])
    )

    result = dict(changed=False)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    (_, item, _) = module.run_command(
        ['op', 'item', 'get', module.params['name'], '--format', 'json', '--session', module.params['token']], check_rc=True)

    item = json.loads(item)

    values = ((f.get('label'), f.get('value')) for f in item['fields']
              if f.get('value') and f.get('label') in module.params['fields'])

    result['fields'] = dict(values)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
