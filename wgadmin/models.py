import ipaddress

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from . import db


class Peer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    master_id = db.Column(db.Integer, db.ForeignKey('interface.id'), nullable=False)
    slave_id = db.Column(db.Integer, db.ForeignKey('interface.id'), nullable=False)
    allowed_ips = db.relationship("IpAddress")

    __table_args__ = (db.UniqueConstraint('master_id', 'slave_id'),)

    # Peer.query.filter(Peer.master_id==1, Peer.slave_id==2).join(slave_alias, Peer.master_id==slave_alias.slave_id).count()

    #@hybrid_property
    #def has_backlink(self):
    #    self.__ta

    # @hybrid_property
    # def has_backlink(self):
    #     for peer in self.slave.slaves:
    #         if self.master == peer.slave:
    #             return True
    #     return False

    #@has_backlink.expression
    #def has_backlink(cls):
    #    return db.and_(Peer.slave_id==cls.master_id, Peer.master_id==cls.slave_id)

    def __repr__(self):
        return '<Peer {} {} -> {}>'.format(self.id, self.master, self.slave)


class Interface(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(128))
    public_key = db.Column(db.String(256), unique=True, nullable=False)
    listen_port = db.Column(db.Integer)
    name = db.Column(db.String(16), nullable=False)
    description = db.Column(db.String(256))
    address = db.relationship("IpAddress", cascade="delete")
    masters = db.relationship("Peer",  # List of interfaces that im slave to
                              primaryjoin=Peer.slave_id==id,
                              backref="slave",
                              cascade="delete")
    slaves = db.relationship("Peer",  # List of interfaces im master of
                             primaryjoin=Peer.master_id==id,
                             backref="master",
                             cascade="delete")

    @property
    def fully_linked_peers(self):
        # TODO: SLOW AF
        a_peer = db.aliased(Peer)
        b_peer = db.aliased(Peer)
        return db.object_session(self).query(a_peer).\
            filter(a_peer.slave_id.in_(
                db.object_session(self).query(b_peer.master_id).\
                    filter(b_peer.slave_id==self.id).subquery()),
                a_peer.master_id==self.id
            )

    @property
    def outgoing_peers(self):
        """Not fully linked peers waiting on a backlink"""
        a_peer = db.aliased(Peer)
        b_peer = db.aliased(Peer)
        f_peer = db.aliased(Peer)
        qa = db.object_session(self).query(a_peer.master_id).\
            filter(a_peer.slave_id == self.id)
        qb = db.object_session(self).query(b_peer.slave_id).\
            filter(b_peer.master_id == self.id)
        qfa = qb.except_(qa)
        # print("++++",qfa.all())
        qfb = qa.except_(qb)
        # print("++++",qfb.all())
        # return db.object_session(self).query(f_peer).\
        #    filter(f_peer.master_id==qfa)
        return db.object_session(self).query(f_peer).\
            filter(f_peer.slave_id.in_(qfa), f_peer.master_id == self.id)

    @property
    def incoming_peers(self):
        """Not fully linked peers that want to link with me"""
        a_peer = db.aliased(Peer)
        b_peer = db.aliased(Peer)
        f_peer = db.aliased(Peer)
        qa = db.object_session(self).query(a_peer.master_id).\
            filter(a_peer.slave_id == self.id)
        qb = db.object_session(self).query(b_peer.slave_id).\
            filter(b_peer.master_id == self.id)
        qfa = qb.except_(qa)
        # print("++++",qfa.all())
        qfb = qa.except_(qb)
        # print("++++",qfb.all())
        # return db.object_session(self).query(f_peer).\
        #    filter(f_peer.master_id==qfa)
        return db.object_session(self).query(f_peer).\
            filter(f_peer.master_id.in_(qfb), f_peer.slave_id == self.id)

    @property
    def linkable_interfaces(self):
        return db.object_session(self).query(Interface).\
            filter(Interface.id != self.id,
                   db.not_(Interface.id.in_(
                       db.object_session(self).query(Peer.slave_id).
                           filter(Peer.master_id == self.id)
                   ))
            )

    def __str__(self):
        if self.host:
            return '{}@{}'.format(self.name, self.host)
        else:
            return self.name

    def __repr__(self):
        return '<Interface {} {}@{}>'.format(self.id, self.name, self.host)


class IpAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interface_id = db.Column(db.Integer, db.ForeignKey('interface.id'))
    interface = db.relationship(Interface, back_populates="address")

    peer_id = db.Column(db.Integer, db.ForeignKey('peer.id'))
    peer = db.relationship(Peer, back_populates="allowed_ips")

    version = db.Column(db.Integer, nullable=False)  # 4 or 6
    mask = db.Column(db.Integer, nullable=False)  # ip address mask
    _address0 = db.Column(db.Integer)  # ipv6 32bit msb
    _address1 = db.Column(db.Integer)  # ipv6 32bit
    _address2 = db.Column(db.Integer)  # ipv6 32bit
    _address3 = db.Column(db.Integer, nullable=False)  # ipv6/ipv4 32bit

    @hybrid_property
    def address(self):
        if self.version == 4:
            return ipaddress.IPv4Interface((self._address3, self.mask))
        else:
            addr = b''.join((
                self._address0.to_bytes(4, byteorder='big'),
                self._address1.to_bytes(4, byteorder='big'),
                self._address2.to_bytes(4, byteorder='big'),
                self._address3.to_bytes(4, byteorder='big'),
            ))
            return ipaddress.IPv6Interface((addr, self.mask))

    @address.setter
    def address(self, value):
        if value.version == 4:
            self.version = 4
            self.mask = value.network.prefixlen
            self._address3 = int.from_bytes(value.packed, byteorder='big')
        elif value.version == 6:
            self.version = 6
            self.mask = value.network.prefixlen
            self._address0 = int.from_bytes(value.packed[0:4], byteorder='big')
            self._address1 = int.from_bytes(value.packed[4:8], byteorder='big')
            self._address2 = int.from_bytes(value.packed[8:12], byteorder='big')
            self._address3 = int.from_bytes(value.packed[12:16], byteorder='big')
        else:
            raise ValueError("Only IPv4Network or IPv6Network is supported")

    def __repr__(self):
        return '<IpAddress {} {}>'.format(self.id, self.address)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column("password", db.String, nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """Store the password as a hash for security."""
        self._password = generate_password_hash(value)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def __repr__(self):
        return '<User {} {}>'.format(self.id, self.username)
