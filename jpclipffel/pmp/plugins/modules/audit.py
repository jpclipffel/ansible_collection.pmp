from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection


ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: resource

short_description: Get PMP audit events

version_added: "3.0"

description:
    - "Get PMP audit events"

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
    # https://localhost:<Port>/restapi/json/v1/audit?AUDITTYPE=Resource&STARTINDEX=1&LIMIT=2&DURATION=YESTERDAY

    # Modules arguments
    module_args = {
        'type':     {'type': str,   'required': True},
        'start':    {'type': int,   'required': False,  'default': 1},
        'limit':    {'type': int,   'required': False,  'default': 2},
        'duration': {'type': str,   'required': False,  'default': 'TODAY'}
    }
    # Initializes module, connection and API helper
    module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=False)
    connection = Connection(module._socket_path)
    # ---
    try:

        # Build path
        # path = '/restapi/json/v1/resources'
        path = (
            f'''/restapi/json/v1/audit'''
            f'''?AUDITTYPE={module.params['type']}'''
            f'''&STARTINDEX={module.params['start']}'''
            f'''&LIMIT={module.params['limit']}'''
            f'''&DURATION={module.params['duration'].upper()}'''
        )
        # Run module
        status_code, data = connection.send_request(
            data={},
            path=path,
            method='get'
        )
        # Setup callback and terminate
        cback = status_code in [200,] and module.exit_json or module.fail_json
        cback(**{
            'msg': data,
            'code': status_code,
        })
    except Exception as error:
        # module.fail_json(**{
        #     'msg': str(error),
        #     'code': -1,
        #     'data': {}
        # })
        module.fail_json(msg='end-error')


def main():
    run_module()


if __name__ == '__main__':
    main()
