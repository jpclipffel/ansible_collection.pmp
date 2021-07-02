# Ansible collection for Password Manager Pro (PMP)

This Ansible collection contains the following resources:

| Resource                | Type          | Description       |
|-------------------------|---------------|-------------------|
| `plugins/lookup/pmp.py` | Lookup plugin | PMP lookup plugin |

## Usage

### Lookup plugin

The lookup plugin `jpclipffel.pmp.password` takes 3 parameters:

| Parameter          | Type     | Values             | Description                         |
|--------------------|----------|--------------------|-------------------------------------|
| #1 - Mode          | `string` | `regex` or `exact` | Password search mode                |
| #2 - Resource name | `string` | -                  | Resource name or regular expression |
| #3 - Account name  | `string` | -                  | Resource's account name to use      |

Example usage:

```yaml
- name: Gather ESX information
    community.vmware.vmware_local_user_info:
    hostname: "{{ inventory_hostname }}"
    username: "{{ vcenter_username }}"
    password: "{{ lookup('jpclipffel.pmp.password', 'regex', '.*' + inventory_hostname, vcenter_username) }}"
    delegate_to: localhost
```

The plugin requires two environments variables:

| Variable        | Description                          | Example                                |
|-----------------|--------------------------------------|----------------------------------------|
| `PMP_URL`       | PMP url without the trailing `/`     | `https://pmp.tld`                      |
| `PMP_AUTHTOKEN` | PMP authentication token for Ansible | `00000000-0000-0000-0000-000000000000` |

### Ansible Tower / AWX credential

In Ansible Tower / AWX, you may create a custom credential type as follow.

Input configuration:

```yaml
fields:
  - id: url
    type: string
    label: URL
  - id: token
    type: string
    label: Token
    secret: true
required:
  - url
  - token
```

Injector configuration:

```yaml
env:
  PMP_URL: '{{ url }}'
  PMP_AUTHTOKEN: '{{ token }}'
```

## Installation

## Development

### Build and publish

* `ansible-galaxy collection build jpclipffel/pmp`
* `ansible-galaxy collection publish jpclipffel-pmp-*.tar.gz`
