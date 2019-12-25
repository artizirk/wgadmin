import ipaddress

from sqlalchemy.exc import IntegrityError
from flask import (
    Blueprint, Response, flash, g, redirect, render_template, request, url_for
)

from . import db
from .models import Interface, IpAddress, Peer
from .auth import login_required
from .forms import InterfaceSearchForm
from . import utils

bp = Blueprint("config", __name__)


@bp.route("/export/<int:id>/wg-quick")
def export_wg_quick(id):
    iface = Interface.query.get_or_404(id)
    body = ["[Interface]\n# PrivateKey = REPLACE ME!!"]
    if iface.listen_port:
        body.append("\nListenPort = " + iface.listen_port)
    body.append("\nAddress = ")
    for addr in iface.address:
        body.append(str(addr.address)+', ')

    for peer in iface.fully_linked_peers:
        body.append("\n\n[Peer]")
        body.append("\nPublicKey = "+peer.slave.public_key)
        body.append("\nAllowedIPs = ")
        for addr in peer.slave.allowed_ips:
            body.append(str(addr.address) + ', ')
        body.append("\nPersistentKeepalive = 60\n")

    return Response(body, mimetype='text/plain')
