import ipaddress

from sqlalchemy.exc import IntegrityError
from flask import (
    Blueprint, Response, flash, g, redirect, render_template, request, url_for
)
from http import HTTPStatus

from . import db
from .models import Interface, IpAddress, Peer
from .auth import login_required
from .forms import InterfaceSearchForm
from . import utils

bp = Blueprint("config", __name__)


def generate_wg_config(id, variant="quick", private_key_placeholder=True):
    iface = Interface.query.get_or_404(id)
    body = ["[Interface]"]
    if private_key_placeholder:
        body.append("\n# PrivateKey = REPLACE ME!!")
    body.append("\n# PublicKey = " + iface.public_key)
    if iface.listen_port:
        body.append("\nListenPort = " + str(iface.listen_port))

    if variant == "quick":
        body.append("\nAddress = ")
        for addr in iface.address:
            body.append(str(addr.address))
            body.append(', ')
        del body[-1]  # Remove last ,

    for peer in iface.fully_linked_peers:
        body.append("\n\n# " + str(peer.slave))
        body.append("\n[Peer]")
        body.append("\nPublicKey = " + peer.slave.public_key)
        if peer.slave.persistent_keepalive:
            body.append("\nPersistentKeepalive = " + str(peer.slave.persistent_keepalive))
        if peer.slave.endpoint:
            body.append("\nEndpoint = " + peer.slave.endpoint)
        body.append("\nAllowedIPs = ")
        for addr in peer.slave.allowed_ips:
            body.append(str(addr.address))
            body.append(', ')
        del body[-1]  # Remove last ,
    body.append("\n")

    return Response(body, mimetype='text/plain')


@bp.route("/export/<int:id>/wg-quick")
def export_wg_quick(id):
    return generate_wg_config(id, "quick")


@bp.route("/export/<int:id>/wg-sync")
def export_wg_synx(id):
    return generate_wg_config(id, "sync",
                              private_key_placeholder=False)


@bp.route("/export/<int:id>/onetime", methods=("GET", "POST"))
def export_onetime(id):
    iface = Interface.query.get_or_404(id)
    if request.method == "POST":
        iface.public_key = request.form.get("publicKey")
        db.session.add(iface)
        try:
            db.session.commit()
            return generate_wg_config(id, "quick",
                                      private_key_placeholder=False)
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE" in str(e):
                msg = "Error: Public Key is not UNIQUE"
                return Response(msg, status=HTTPStatus.CONFLICT,
                                mimetype='text/plain')
            else:
                msg = "Error: {}".format(e)
                return Response(msg, status=HTTPStatus.BAD_REQUEST,
                                mimetype='text/plain')
    return render_template("export_onetime_conf.html", iface=iface)
