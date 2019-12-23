from hashlib import sha256
from ipaddress import ip_network


def gen_ip(pubkey, subnet=ip_network('fe80::/64')):
    """Generate wg-ip compatible addresses from WireGuard public key"""
    prefix_bytes = subnet.network_address.packed

    suffix_bytes = sha256(pubkey.encode('ascii')+b'\n').digest()

    return


if __name__ == '__main__':
    pubkey = "foo"
    subnet = ip_network("fd1a:6126:2887::/48")
    result = "fd1a:6126:2887:f9b1:d61e:21e7:96d7:8dcc"
    print(gen_ip(pubkey, subnet))
