"""
Gathers internal and external IP address, as well as MAC address and
posts information to Slack channel, via a webhook.
"""

import socket
import fcntl
import struct
import requests
from config import IF_NAME, SLACK_WEBHOOK

def get_ip_address(ifname):
    """ Return IP address """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        sock.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def get_hw_address(ifname):
    """ Return HW address """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(sock.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])

def get_ext_ip():
    """ Returns the external IP address """
    headers = {'Accept': 'application/json'}
    resp = requests.get('http://ifconfig.co', headers=headers)
    return resp.json()['ip']

def post_to_slack(ip_info):
    """ Posts IP info to Slack webhook """
    url = SLACK_WEBHOOK
    mesg = """MA Bastion is alive!
Here are my stats:
```
Internal IP address: %s
Extermal IP address: %s
        MAC Address: %s
```
"""
    headers = {'Content-Type': 'application/json'}
    payload = {
        'channel': '#alerts',
        'username': 'ma-bastion',
        'text': mesg % (ip_info['int_ip'], ip_info['ext_ip'], ip_info['hw_addr']),
        'icon_emoji': ':ghost:'
    }

    requests.post(url, json=payload, headers=headers)


IP_INFO = {}
IP_INFO['int_ip'] = get_ip_address(IF_NAME)
IP_INFO['hw_addr'] = get_hw_address(IF_NAME)
IP_INFO['ext_ip'] = get_ext_ip()

post_to_slack(IP_INFO)
