import os
import json

from typing import Tuple

from ansible.errors import AnsibleError, AnsibleLookupError
from ansible.module_utils.urls import open_url


def pmp_envinfo() -> dict:
    """Returns information from environment.
    """
    info = {}
    # Get PMP URL from environment
    if os.getenv('PMP_URL') is not None:
        info['url'] = os.environ['PMP_URL'].rstrip('/')
    else:
        raise AnsibleError("PMP error: PMP_URL environment variable is not set")
    # Get PMP token from environment
    if os.getenv('PMP_AUTHTOKEN') is not None:
        info['authtoken'] = os.environ['PMP_AUTHTOKEN']
    else:
        raise AnsibleError("PMP error: PMP_AUTHTOKEN environment variable is not set")
    # Done
    return info


def pmp_parse_response(response: bytes) -> tuple:
    """Parses a PMP API response.

    :param response:     Raw PMP response
    """
    # Parse response
    message = json.loads(
        isinstance(response, bytes) and response.decode('utf-8')
        or response
    )
    # Return operation, result and details
    return (
        message.get('operation', None),
        message.get('operation', {}).get('result'),
        message.get('operation', {}).get('Details'),
    )
