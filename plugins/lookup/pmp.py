# (c) 2015, Jonathan Davila <jonathan(at)davila.io>
# (c) 2017 Ansible Project
# (c) 2020 Jean-Philippe Clipffel


from __future__ import (absolute_import, division, print_function)


EXAMPLES = """
  - name: Get the password for the extact resource name
    debug:
      msg: "{{ lookup('pmp', 'exact' 'resource_name', 'account_name') }}"
  - name: Get the password for the matching resource name
    debug:
      msg: "{{ lookup('pmp', 'regex', '.*resource_name.*', 'account_name') }}"
"""


RETURN = """
  _raw:
    description:
      - Search and return a resource password from PMP
"""


import os
import re
import json
import urllib.parse

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.urls import open_url


# Set PMP URL from environment
if os.getenv('PMP_URL') is not None:
    PMP_URL = os.environ['PMP_URL']
else:
    raise AnsibleError("PMP error: PMP_URL environment variable is not set")


# Set PMP token from environment
if os.getenv('PMP_AUTHTOKEN') is not None:
    PMP_AUTHTOKEN = os.environ['PMP_AUTHTOKEN']
else:
    raise AnsibleError("PMP error: PMP_AUTHTOKEN environment variable is not set")


class LookupModule(LookupBase):
    """PMP lookup plugin implementation.
    """

    def _get(self, query: str,
                headers: dict = {'Content-Type': 'application/json'},
                method: str = 'GET', validate_certs: bool = False) -> tuple:
        """Queries PMP.

        :param query:               PMP API path with arguments
        :param headers:             Custom headers
        :param method:              Custom method
        :param validated_certs:     Validate SSL certificate
        """
        # Query PMP
        response = open_url(
            f'{PMP_URL}/{query}',
            method='GET',
            headers=headers,
            validate_certs=validate_certs
        )
        # Parse response
        message = json.loads(response.read().decode('utf-8'))
        # Return operation, result and details
        return (
            message.get('operation', None),
            message.get('operation', {}).get('result'),
            message.get('operation', {}).get('Details'),
        )

    def _get_resource_password(self, resource_id: str, account_id: str) -> str:
        """Fetches a resource's password.

        :param resource_id: Resource ID
        :param account_id:  Account ID
        """
        # Prepare query URL
        url = (
            'restapi/json/v1/resources/getResourceAccountDetails'
            f'?APP_AUTHTOKEN={PMP_AUTHTOKEN}'
            f'&APP_NAME=ANSIBLE'
            f'&RESOURCEID={resource_id}'
            f'&ACCOUNTID={account_id}'
        )
        # Query PMP
        operation, result, details = self._get(url)
        # Process response
        if details:
            account_details = json.loads(details.get("ACCOUNTDETAILS"))
            if 'PASSWORD_REASON' in account_details:
                raise AnsibleError(f'PMP error: {account_details.get("PASSWORD_REASON")}')
            else:
                return account_details['PASSWORD']
        else:
            raise AnsibleError(f'PMP error: {result.get("message")}')

    def _get_resource_ids(self, resource_name: str, account_name: str) -> tuple:
        """Fetches a resource's name and account IDs.

        :param resource_name:   Resource name
        :param account_name:    Resource's account name
        """
        url = (
            'restapi/json/v1/resources/getResourceIdAccountId'
            f'?APP_AUTHTOKEN={PMP_AUTHTOKEN}'
            f'&APP_NAME=Ansible'
            f'&RESOURCENAME={urllib.parse.quote(resource_name)}'
            f'&ACCOUNTNAME={urllib.parse.quote(account_name)}'
        )
        # Query PMP
        operation, result, details = self._get(url)
        # Process response
        if not details:
            raise AnsibleError(f'PMP error: {str(result)}')
        return details['RESOURCEID'], details['ACCOUNTID']

    def _search_resource_ids(self, resource_name: str, account_name: str) -> tuple:
        """Fetches all resources and search for the given resource name.
        """
        rex = re.compile(resource_name)
        url = (
            'restapi/json/v1/resources'
            f'?APP_AUTHTOKEN={PMP_AUTHTOKEN}'
            f'&APP_NAME=Ansible'
        )
        # Query PMP
        operation, result, details = self._get(url)
        # raise AnsibleError(len(details))
        for resource in details:
            if rex.match(resource.get('RESOURCE NAME')):
                return self._get_resource_ids(
                    resource['RESOURCE NAME'],
                    account_name
                )
        return ()

    def run(self, terms, **kwargs):
        """Lookup entry point.

        :param terms: Resource name & account name
        """
        # Set lookup mode, resource name and account name from parameters
        mode, resource_name, account_name = terms

        if mode == 'exact':
            return [self._get_resource_password(
                *self._get_resource_ids(resource_name, account_name)
            ),]
        elif mode == 'regex':
            return [self._get_resource_password(
                *self._search_resource_ids(resource_name, account_name)
            ),]
