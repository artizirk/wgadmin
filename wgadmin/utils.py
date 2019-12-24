from typing import Union
from hashlib import sha256
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from ipaddress import ip_address, ip_network


def gen_ip(
    pubkey: Union[bytes, str],
    subnet: Union[IPv4Network, IPv6Network] = ip_network('fe80::/64')
) -> Union[IPv4Address, IPv6Address]:
    """Generate wg-ip compatible addresses from WireGuard public key"""

    prefix_bytes = subnet.network_address.packed
    mask_bytes = subnet.netmask.packed
    if type(pubkey) != "bytes":
        pubkey = pubkey.encode('ascii')  # only bytes can be sha256sumed
    suffix_bytes = sha256(pubkey+b'\n').digest()

    address = b''
    for prefix, suffix, mask in zip(prefix_bytes, suffix_bytes, mask_bytes):
        address += (
            (prefix & mask) | (suffix & (mask^255))
        ).to_bytes(1, byteorder='big')  # In network byte order

    return ip_address(address)


if __name__ == '__main__':
    pubkey = "foo"
    subnet = ip_network("fd1a:6126:2887::/48")
    #subnet = ip_network("10.0.0.0/8")
    exp_result = ip_address("fd1a:6126:2887:f9b1:d61e:21e7:96d7:8dcc")
    real_result = gen_ip(pubkey, subnet)
    print(exp_result, real_result, exp_result == real_result)
