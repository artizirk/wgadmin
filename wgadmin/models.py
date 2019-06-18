import ipaddress

from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from . import db


class Interface(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.String, unique=True, nullable=False)
    listen_port = db.Column(db.Integer)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)


class IpAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
