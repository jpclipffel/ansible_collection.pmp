from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection

from ansible.module_utils.pmp import *


ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: resource

short_description: Manage PMP resources

version_added: "3.0"

description:
    - "Manage PMP resources"

options:
    method:
        description:
            - HTTP method (e.g. 'GET', 'POST', etc.)
        required: true
        type: str
    path:
        description:
            - API path (defaults to API v1.0, e.g. '/api/1.0/<path>')
        required: true
        type: str
    data:
        description:
            - Request payload (will be merged in formData or query)
        required: false
        type: dict

author:
    - Jean-Philippe Clipffel (@jpclipffel)
'''

EXAMPLES = '''
- name: Query resource
  device42_api:
    meth: GET
    path: devices
'''

RETURN = '''
msg:
    description: The 'msg' field from Device42 response
    type: str
    returned: always
code:
    description: The 'code' fields from Device42 response
    type: int
    returned: always
data:
    description: The full Device42 response
    type: complex
    returned: always
'''


def run_module():
    """Ansible module entry point.
    """

    # Modules arguments
    module_args = {
        'meth': {'type': str,  'required': True},
        'path': {'type': str,  'required': True},
        'data': {'type': dict, 'required': False, 'default': {}},
    }
    # Initializes module, connection and API helper
    module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=False)
    connection = Connection(module._socket_path)
    # ---
    try:
        # Run module
        status_code, data = connection.send_request(
            data=module.params['data'],
            path=module.params['path'],
            method=module.params['meth']
        )
        # Setup callback and terminate
        cback = status_code in [200,] and module.exit_json or module.fail_json
        cback(**{
            'msg': data.get('msg', None),
            'code': data.get('code', -1),
            'data': data
        })
    except Exception as error:
        module.fail_json(**{
            'msg': str(error),
            'code': -1,
            'data': {}
        })


def main():
    run_module()


if __name__ == '__main__':
    main()
