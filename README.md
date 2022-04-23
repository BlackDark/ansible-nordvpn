NordVPN
=========

Setup and configures NordVPN client

Requirements
------------

You need to have an active NordVPN subscription

Role Variables
--------------

| Variable            | Type    | Choices           | Default  | Comment                                                                        |
| ------------------- | ------- | ----------------- | -------- | ------------------------------------------------------------------------------ |
| auto_connect        | boolean | true, false       | false    | Whether VPN needs to be connected on boot                                      |
| auto_connect_host   | string  |                   |          | A host, the VPN connects to on boot                                            |
| cyber_sec           | boolean | true, false       | false    | Enable or disable [CyberSec](https://bit.ly/3EHRy1a)                           |
| dns                 | string  |                   | disabled | Set custom DNS (you can set up a single DNS or two space delimited DNS servers |
| firewall            | boolean | true, false       | false    | Enable or disable firewall                                                     |
| ipv6                | boolean | true, false       | false    | Enable or disable ipv6                                                         |
| kill_switch         | boolean | true, false       | false    | Enable or disable [Kill Switch](https://bit.ly/3v5CxmT)                        |
| notifications       | boolean | true, false       | false    | Enable or disable notifications                                                |
| technology          | string  | OPENVPN, NORDLYNX | OPENVPN  | Set connection technology (OpenVPN or [NordLynx](https://bit.ly/3K2YTtq))      |
| protocol            | string  | UDP, TCP          | UDP      | Switch between [UDP and TCP protocols](https://bit.ly/38fNSYu)                 |
| whitelisted_ports   | list    |                   | [22]     | List of ports that should be accessible when VPN is up                         |
| whitelisted_subnets | list    |                   | []       | List of subnets whitelisted. You may want to add your local subnet             |
| login               | boolean | true, false       | true     | Login into the account automatically                                           |
| username            | string  |                   | foo      | Account username                                                               |
| password            | string  |                   | bar      | Account password                                                               |
| connect             | boolean | true, false       | false    | Automatically connect VPN once it's configured                                 |
| server              | string  |                   |          | Connect to the specific server                                                 |

For more details on NordVPN settings check the NordVPN Linux [manual page](https://bit.ly/3Ka98fm).

Dependencies
------------

No dependencies

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: nordvpn_clients
      roles:
         - role: ifel.nordvpn
           vars:
             auto_connect: true
             auto_connect_host: "us8830"
             firewall: true
             kill_switch: true
             technology: "NORDLYNX"
             username: my@email.com
             password: "my passwd, preferable encrypted, see https://bit.ly/3rOIlz3"
            server: "us8830"
            whitelisted_ports: [22, 80]
            whitelisted_subnets: ["192.168.0.0/16"]

License
-------

MIT

Author Information
------------------

<https://github.com/ifel/>
