#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
import json
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ws_1password_cli
short_description: Setup 1password CLI
version_added: "1.0.0"
description: Module to configure and sign in to 1password CLI.

options:
    address:
        description: The URL to authenticate to (e.g. https://example.1password.com).
        required: true
        type: str
    email:
        description: The email for the account.
        required: true
        type: str
    password:
        description: The password for the account.
        required: true
        type: str
    secret_key:
        description: The secret key for the account.
        required: true
        type: str

author:
    - Eugenio Depalo (@eugeniodepalo)
'''

RETURN = """
  token:
    description: The token for the account.
    type: str
"""

EXAMPLES = r'''
# Authenticate to 1password.com
- name: Configure 1password CLI
  eugeniodepalo.workstation.ws_1password_cli:
    address: https://example.1password.com
    email: user@example.com
    password: 123456
    secret_key: 123456789
'''


def run_module():
    module_args = dict(
        address=dict(type='str', required=True),
        email=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        secret_key=dict(type='str', required=True, no_log=True)
    )

    result = dict(changed=False)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    params = module.params
    account = get_account(module, params['address'], params['email'])

    if not account:
        result['changed'] = True

        if module.check_mode:
            module.exit_json(**result)

        module.run_command(['op', 'account', 'add',
                            '--email', params['email'],
                            '--address', params['address'],
                            '--secret-key', params['secret_key']], check_rc=True, data=params['password'])

        account = get_account(module, params['address'], params['email'])

    if module.check_mode:
        module.exit_json(**result)

    (_, token, _) = module.run_command(
        ['op', 'signin', '--raw', '--account', account['account_uuid']], check_rc=True, data=params['password'])

    result['token'] = token.strip()
    module.exit_json(**result)


def get_account(module, address, email):
    (_, accounts, _) = module.run_command(
        ['op', 'account', 'list', '--format', 'json'], check_rc=True
    )

    accounts = json.loads(accounts)

    return next(
        (a for a in accounts if a['email'] == email and a['url'] == address),
        None
    )


def main():
    run_module()


if __name__ == '__main__':
    main()
