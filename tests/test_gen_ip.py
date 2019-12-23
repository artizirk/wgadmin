from unittest import TestCase
from ipaddress import ip_address, ip_network

from wgadmin.utils import gen_ip


# Test Cases from wg-ip test_gen_ip
# https://github.com/chmduquesne/wg-ip/blob/1a0ac39a511d67a078f0e2bb17776fe090f46720/wg-ip#L462
DATA = [
    ("foo", "fd1a:6126:2887::/48", "fd1a:6126:2887:f9b1:d61e:21e7:96d7:8dcc"),
    ("bar", "fd1a:6126:2887::/48", "fd1a:6126:2887:6691:8c98:63af:ca94:2d0f"),
    ("foo", "fd1a:6126:2887::/49", "fd1a:6126:2887:79b1:d61e:21e7:96d7:8dcc"),
    ("bar", "fd1a:6126:2887::/49", "fd1a:6126:2887:6691:8c98:63af:ca94:2d0f"),
    ("foo", "2001:db8::/64",        "2001:db8::d61e:21e7:96d7:8dcc"),
    ("bar", "2001:db8::/64",        "2001:db8::8c98:63af:ca94:2d0f"),
    ("foo", "10.0.0.0/8",           "10.187.157.128"),
    ("bar", "10.0.0.0/8",           "10.134.94.149"),
    ("foo", "10.0.0.0/9",           "10.59.157.128"),
    ("bar", "10.0.0.0/9",           "10.6.94.149"),
    ("foo", "172.16.0.0/12",        "172.27.157.128"),
    ("bar", "172.16.0.0/12",        "172.22.94.149")
]


class TestGenIp(TestCase):
    def test_gen_ip(self):
        for case in DATA:
            pubkey = case[0]
            network = ip_network(case[1])
            expected_result = ip_address(case[2])
            with self.subTest():
                self.assertEqual(gen_ip(pubkey, network), expected_result)
