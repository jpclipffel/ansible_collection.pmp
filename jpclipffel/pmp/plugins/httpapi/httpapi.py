import json

from ansible.errors import AnsibleConnectionFailure
from ansible.plugins.httpapi import HttpApiBase

from ansible_collections.jpclipffel.pmp.plugins.module_utils.pmp import (
    pmp_envinfo,
    pmp_parse_response
)


DOCUMENTATION = '''
---
author:
    - Jean-Philippe Clipffel (@jpclipffel)
httpapi : PasswordManagerPro (PMP)
short_description: Httpapi plugin for Password Manager Pro (PMP)
description:
  - This httpapi plugin provides methods to connect to PMP via its REST API
version_added: "3.0"
'''


class HttpApi(HttpApiBase):
    """Ansible's HTTPAPI plugin for PMP API.

    :ivar headers:  Default request headers
    """

    def __init__(self, connection):
        super(HttpApi, self).__init__(connection)
        # Get PMP info
        self.pmp_info = pmp_envinfo()
        self.pmp_url = self.pmp_info['url']
        self.pmp_authtoken = self.pmp_info['authtoken']
        # Setup headers
        self.headers = {
            'Content-Type': 'application/json',
            'AUTHTOKEN': self.pmp_authtoken
        }

    def send_request(self, data: dict, path: str, method: str) -> dict:
        """Handles PMP API requests and responses.

        :param data:        Request data
        :param path:        API path
        :param method:      HTTP method

        :return:    Tuple as `(status_code: int, content: dict)`
        """
        try:
            # Prepare query URL
            # path = (
            #     f'{path}'
            #     f'&APP_AUTHTOKEN={self.pmp_authtoken}'
            #     f'&APP_NAME=ANSIBLE'
            # )
            # Forge and send request
            response, response_data = self.connection.send(
                path,
                data,
                method=method,
                headers=self.headers
            )
            # Decode response and returns
            # return response.getcode(), response_data
            return response.getcode(), response_data.read()
        # # Raised when `data` cannot be JSON-encoded
        # except TypeError as error:
        #     raise Exception(f'Failed to encode Device42 request: {str(error)}')
        # # Raised when Device42 response cannot be decoded to a `dict`
        # except json.JSONDecodeError as error:
        #     raise Exception(f'Failed to decode Device42 response: {str(error)}: {response_data.getvalue()}')
        # Raised when Ansible failed to connect to Device42
        except AnsibleConnectionFailure as error:
            raise Exception(f'Connection error: {str(error)}')
        # Unknown error
        except Exception as error:
            raise Exception(f'Error: {str(error)}')
