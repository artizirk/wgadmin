import ipaddress

from sqlalchemy.exc import IntegrityError
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from . import db
from .models import Interface, IpAddress, Peer
from .auth import login_required

bp = Blueprint("interfaces", __name__)


@bp.route("/")
def list():
    ifaces = Interface.query.all()
    return render_template("interfaces/list.html", ifaces=ifaces)


@bp.route("/add", methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        interface = Interface()
        interface.host = request.form["host"]
        interface.name = request.form["name"]
        interface.description = request.form["description"]
        interface.public_key = request.form["publicKey"]

        if "generateIp" in request.form:
            ip = IpAddress()
            ip.address = ipaddress.ip_interface("fe80::1/64")
            interface.address.append(ip)
            db.session.add(ip)
        db.session.add(interface)
        try:
            db.session.commit()
            flash("New WireGuard interface added")
            return redirect(url_for("interfaces.edit", id=interface.id))
        except IntegrityError as e:
            db.session.rollback()
            if "UNIQUE" in str(e):
                flash("Error: Public Key is not UNIQUE")
            else:
                flash("Error: {}".format(e))
            return render_template("interfaces/add.html", form=request.form)
    return render_template("interfaces/add.html", form={})


@bp.route("/edit/<int:id>", methods=("GET",))
def edit(id):
    iface = Interface.query.filter_by(id=id).first_or_404()
    return render_template("interfaces/edit.html", iface=iface)


@bp.route("/edit/<int:id>", methods=("POST",))
def edit_post(id):
    iface = Interface.query.get_or_404(id)
    if request.form["action"] == "delete":
        db.session.delete(iface)
        db.session.commit()
        flash("Interface {}@{} deleted".format(iface.host, iface.name))
        return redirect(url_for("interfaces.list"))
    elif request.form["action"] == "update":
        iface.host = request.form["host"]
        iface.name = request.form["name"]
        iface.description = request.form["description"]
        iface.public_key = request.form["publicKey"]
        db.session.commit()
        flash("Interface updated")
    elif request.form["action"] == "addAddress":
        ip = IpAddress()
        try:
            ip.address = ipaddress.ip_interface(request.form["address"])
        except ValueError as e:
            flash("Error adding IP address: {}".format(e))
        else:
            iface.address.append(ip)
            db.session.add(ip)
            db.session.commit()
            flash("IP address added")
    elif request.form["action"] == "deletePeer":
        peer_id = request.form['peer']
        peer = Peer.query.get_or_404(peer_id)
        db.session.delete(peer)
        db.session.commit()
    else:
        print("not action")
    return redirect(url_for("interfaces.edit", id=id))


@bp.route("/edit/<int:id>/add_peer", methods=("GET", "POST"))
def add_peer(id):
    iface = Interface.query.get_or_404(id)
    if request.method == "POST":
        peer_id = request.form["peer"]
        peer_iface = Interface.query.filter_by(id=peer_id).first_or_404()
        peer = Peer()
        peer.master_id = iface.id
        peer.slave_id = peer_iface.id
        db.session.add(peer)
        db.session.add(iface)
        db.session.commit()
        flash("Peer {}@{} added".format(peer_iface.host, peer_iface.name))
        return redirect(url_for("interfaces.edit", id=id))
    ifaces = iface.linkable_interfaces
    return render_template("interfaces/add_peer.html", iface=iface, ifaces=ifaces)
