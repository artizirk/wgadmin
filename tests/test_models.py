import os
from itertools import islice
from flask_testing import TestCase

from wgadmin import create_app, db, init_db
from wgadmin.models import Interface, IpAddress, Peer

INTERFACES = {
    "master": "gSIp9rl2sStEzurSbMFGTDPwz5mx5/xmkd9VA68+8yI=",
    "a": "onjhmO9zcd7hVJLhwNiKGl5qlz9qTXcGgmuFp4pvu0k=",
    "b": "gwU9CStMW6SIzPn3kZ3LVhEgEJjeMwORfyPD4xxX/kA=",
    "c": "n7DW48WJAUoWKHcBmTB7U+02eBzixnKfkg0h4yisRiI=",
    "d": "sd/Jg8QA2UHEox5uXj9IuxyrZ5yY+Fo7mpan2nmo0Ao=",
}


class TestPeers(TestCase):

    def create_app(self):
        self.app = create_app({
            "TESTING": True
        })
        return self.app

    def setUp(self) -> None:

        init_db()
        for name, key in INTERFACES.items():
            i = Interface()
            i.name = name
            i.public_key = key
            db.session.add(i)
        db.session.commit()

    def tearDown(self) -> None:
        db.session.remove()
        #db.drop_all()

    def test_one_peer_half_linked(self):
        ifm = Interface.query.filter_by(name="master").one()
        ifa = Interface.query.filter_by(name="a").one()
        p = Peer()
        p.master = ifm
        p.slave = ifa
        db.session.add(p)
        db.session.commit()

        self.assertIn(p, ifm.slaves)
        self.assertNotIn(p, ifm.masters)

        self.assertIn(p, ifa.masters)
        self.assertNotIn(p, ifa.slaves)

        self.assertNotIn(p, ifm.fully_linked_peers)
        self.assertIn(p, ifm.outgoing_peers)
        self.assertNotIn(p, ifm.incoming_peers)

        self.assertIn(p, ifa.incoming_peers)
        self.assertNotIn(p, ifa.outgoing_peers)

    def test_many_peers_half_linked(self):
        ifm = Interface.query.filter_by(name="master").one()
        for i, (name, key) in enumerate(islice(INTERFACES.items(), 1, None), 1):
            with self.subTest(i=i):
                ifx = Interface.query.filter_by(name=name).one()
                p = Peer()
                p.master = ifm
                p.slave = ifx
                db.session.add(p)
                db.session.commit()

                self.assertIn(p, ifm.outgoing_peers.all())
                self.assertIn(p, ifx.incoming_peers.all())
                self.assertEqual(len(ifm.slaves), i)
                self.assertEqual(ifm.outgoing_peers.count(), i)
                self.assertEqual(ifx.incoming_peers.count(), 1)
