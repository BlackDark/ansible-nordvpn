#!/usr/bin/python

# Copyright: (c) 2022, Igor Kanyuka <ifelmail@gmail.com>
# MIT License
from __future__ import absolute_import, division, print_function
from typing import Any, Dict, List

__metaclass__ = type

import subprocess
import re

DOCUMENTATION = r"""
---
module: nordvpn_info

short_description: Collects NordVPN settings

version_added: "1.0.0"

description: Collects settings, connection and account infos

options:

author:
    - Igor Kanyuka (@ifel)
"""

EXAMPLES = r"""
# Pass in a message
- name: Collect nordvpn info
  register: testout
"""

RETURN = r"""
# These are examples of possible return values, and in general should use other names for return values.
account:
    description: The parsed output of the `nordvpn account`
    type: dict
    returned: always
    sample: {
        "email": "ifelmail@gmail.com",
        "service": "Active (Expires on Apr 21st, 2022)"
    }
status:
    description: The parsed output of the `nordvpn status`
    type: str
    returned: always
    sample: {
        "city": "San Francisco",
        "country": " United States",
        "current_protocol": "UDP",
        "current_server": "us1111.nordvpn.com",
        "current_technology": "NORDLYNX",
        "server_ip": "11.22.33.44",
        "status": "Connected",
        "transfer": "4.75 GiB received, 1.89 GiB sent",
        "uptime": "13 hours 16 minutes"
    }
settings:
    description: The parsed output of the `nordvpn settings`
    type: dict
    returned: always
    sample: {
        "auto_connect": true,
        "cyber_sec": false,
        "dns": "disabled",
        "firewall": true,
        "ipv6": false,
        "kill_switch": true,
        "notify": false,
        "technology": "NORDLYNX",
        "whitelisted_ports": [
            22,
            80,
            443
        ],
        "whitelisted_subnets": [
            "17.1.2.0/24"
        ]
    }
"""

from ansible.module_utils.basic import AnsibleModule


class NotLogged(Exception):
    pass


def _parse_output(cmd: str, regexp: str, groups: List[str]) -> Dict[str, Any]:
    ret = {}
    res = subprocess.run(["/usr/bin/nordvpn", cmd], stdout=subprocess.PIPE)
    output = res.stdout.decode("utf-8")

    m = re.match(
        regexp,
        output,
        flags=re.MULTILINE,
    )
    if not m:
        if re.match(r".*You are not logged in.", output, re.M):
            raise NotLogged()
        raise RuntimeError(f"Could not parse the {output} output")

    for group_name in groups:
        ret[group_name] = m.group(group_name)

    return ret

def _parse_output_account(cmd: str, regexp: str, groups: List[str]) -> Dict[str, Any]:
    ret = {}
    res = subprocess.run(["/usr/bin/nordvpn", cmd], stdout=subprocess.PIPE)
    output = res.stdout.decode("utf-8")

    for group in groups:
        ret[group] = None
    
    for line in output.splitlines():
        if len(line.strip()) > 0 and line.find(":") != -1:
            split = line.split(":")
            
            if len(split) != 2:
                continue

            key = split[0].strip().lower()
            value = split[1].strip()
            
            if key == "email address":
                key = "email"
            elif key == "vpn service":
                key = "service"
            ret[key] = value
    return ret

def _parse_output_status(cmd: str, regexp: str, groups: List[str]) -> Dict[str, Any]:
    ret = {}
    res = subprocess.run(["/usr/bin/nordvpn", cmd], stdout=subprocess.PIPE)
    output = res.stdout.decode("utf-8")

    for group in groups:
        ret[group] = None
    
    for line in output.splitlines():
        if len(line.strip()) > 0 and line.find(":") != -1:
            split = line.split(":")
            
            if len(split) != 2:
                continue

            key = split[0].strip().lower()
            value = split[1].strip()
            
            if key == "current protocol":
                key = "current_protocol"
            elif key == "current server":
                key = "current_server"
            elif key == "server ip":
                key = "server_ip"
            ret[key] = value
    return ret

def _parse_output_settings(cmd: str, regexp: str, groups: List[str]) -> Dict[str, Any]:
    ret = {}
    res = subprocess.run(["/usr/bin/nordvpn", cmd], stdout=subprocess.PIPE)
    output = res.stdout.decode("utf-8")

    for group in groups:
        ret[group] = None
    
    ret["whitelisted_ports"] = []
    ret["whitelisted_subnets"] = []

    whitelist_ports_loop = False
    whitelist_subnet_loop = False
    whitelisted_ports = []
    whitelisted_subnets = []
    
    for line in output.splitlines():
        if line.find(":") == -1:
            if whitelist_ports_loop:
                split = line.strip().split(" ")
                whitelisted_ports.append(int(split[0]))
                continue

            if whitelist_subnet_loop:
                whitelisted_subnets.append(line.strip())
                continue

        if len(line.strip()) > 0 and line.find(":") != -1:
            if whitelist_ports_loop:
                ret["whitelisted_ports"] = whitelisted_ports
                whitelist_ports_loop = False

            if whitelist_subnet_loop:
                ret["whitelisted_subnets"] = whitelisted_subnets
                whitelist_subnet_loop = False

            split = line.split(":")
            key = split[0].strip().lower()
            value = split[1].strip()
            
            if key == "auto-connect":
                key = "auto_connect"
            elif key == "kill switch":
                key = "kill_switch"
            elif key == "threat protection lite":
                key = "threat_protection_lite"
            elif key == "whitelisted ports":
                whitelist_ports_loop = True
                continue
            elif key == "whitelisted subnets":
                whitelist_subnet_loop = True
                continue
            ret[key] = value

    if whitelist_subnet_loop:
        ret["whitelisted_subnets"] = whitelisted_subnets
        whitelist_subnet_loop = False

    return ret

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict()

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        account={},
        status={},
        settings={},
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    # Read account info
    try:
        result["account"].update(
            _parse_output_account(
                "account",
                r".*Account Information:\n(Email Address: (?P<email>.*)\n)?(VPN Service: (?P<service>.*))?",
                ["email", "service"],
            )
        )
    except NotLogged:
        result["account"].update({"email": "", "service": "You are not logged in."})

    # Read status
    result["status"].update(
        _parse_output_status(
            "status",
            r".*Status: (?P<status>.*)\n(Current server: (?P<current_server>.*)\n)?(Country:(?P<country>.*)\n)?(City: (?P<city>.*)\n)?(Server IP: (?P<server_ip>.*)\n)?(Current technology: (?P<current_technology>.*)\n)?(Current protocol: (?P<current_protocol>.*)\n)?(Transfer: (?P<transfer>.*)\n)?(Uptime: (?P<uptime>.*))?",
            [
                "status",
                "current_server",
                "country",
                "city",
                "server_ip",
                "current_technology",
                "current_protocol",
                "transfer",
                "uptime",
            ],
        )
    )

    # Read settings:
    settings = _parse_output_settings(
        "settings",
        r".*Technology: (?P<technology>.*)\n(Protocol: (?P<protocol>.*)\n)?(Firewall: (?P<firewall>.*)\n)?(Kill Switch: (?P<kill_switch>.*)\n)?(CyberSec: (?P<cyber_sec>.*)\n)?(Obfuscate: (?P<obfuscate>.*)\n)?(Notify: (?P<notify>.*)\n)?(Auto-connect: (?P<auto_connect>.*)\n)?(IPv6: (?P<ipv6>.*)\n)?(DNS: (?P<dns>.*)\n)?(Whitelisted ports:\n(?P<whitelisted_ports>(\s+.+\n?)*))?(Whitelisted subnets:\n(?P<whitelisted_subnets>(\s+.+\n?)*))?",
        [
            "technology",
            "protocol",
            "firewall",
            "kill_switch",
            "cyber_sec",
            "notify",
            "auto_connect",
            "ipv6",
            "dns",
            "whitelisted_ports",
            "whitelisted_subnets",
        ],
    )
    for k, v in settings.items():
        if v == "enabled":
            settings[k] = True
        elif v == "disabled" and k != "dns":
            settings[k] = False

    result["settings"] = settings
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
