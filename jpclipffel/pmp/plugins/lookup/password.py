# (c) 2015, Jonathan Davila <jonathan(at)davila.io>
# (c) 2017 Ansible Project
# (c) 2020 Jean-Philippe Clipffel


from __future__ import (absolute_import, division, print_function)

import os
import re
import json
import shelve
import fcntl
import urllib.parse

from ansible.errors import AnsibleError, AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.urls import open_url


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


# Set PMP URL from environment
if os.getenv('PMP_URL') is not None:
    PMP_URL = os.environ['PMP_URL'].rstrip('/')
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
        try:
            response = open_url(
                f'{PMP_URL}/{query}',
                method=method,
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
        except Exception as error:
            raise AnsibleLookupError((
                'PMP error: '
                f'query="{query}", method="{method}", error="{str(error)}"'
            ))

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

    def _search_resource_ids(self, resource_name: str,
            account_name: str) -> tuple:
        """Fetches all resources and search for the given resource name.

        :param resource_name:   The resource's name (support regex)
        :param account_name:    The resource's account name
        """
        # PRepare regex
        rex = re.compile(resource_name)
        # Prepare URL
        url = (
            'restapi/json/v1/resources'
            f'?APP_AUTHTOKEN={PMP_AUTHTOKEN}'
            f'&APP_NAME=Ansible'
        )
        # Query PMP
        operation, result, details = self._get(url)
        # Search resource
        for resource in details:
            if rex.match(resource.get('RESOURCE NAME')):
                return self._get_resource_ids(
                    resource['RESOURCE NAME'],
                    account_name
                )
        raise AnsibleLookupError((
            'Failed to lookup resource in PMP: '
            f'resource="{resource_name}", account="{account_name}"'
        ))

    def run(self, terms: tuple, **kwargs) -> tuple:
        """Lookup entry point.

        :param terms: Search mode, resource name, account name
        """
        # self._shelve = shelve.open('pmp')
        # self._lock   = open('pmp_lock')
        # Set lookup mode, resource name and account name
        mode, resource_name, account_name = terms
        # Run lookup
        if mode == 'exact':
            result = (self._get_resource_password(
                *self._get_resource_ids(resource_name, account_name)
            ),)
        elif mode == 'regex':
            result = (self._get_resource_password(
                *self._search_resource_ids(resource_name, account_name)
            ),)
        # Close shelve and return
        # self._shelve.close()
        return result
