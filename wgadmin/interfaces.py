import ipaddress

from sqlalchemy.exc import IntegrityError
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from . import db
from .models import Interface, IpAddress, Peer
from .auth import login_required
from . import forms
from . import utils

bp = Blueprint("interfaces", __name__)


def add_ipv6_link_local_address(iface):
    ip = IpAddress()
    subnet = ipaddress.ip_network("fe80::/64")
    address = utils.gen_ip(iface.public_key, subnet)
    interface_addr = ipaddress.ip_interface((address, 128))
    ip.address = interface_addr
    iface.address.append(ip)
    db.session.add(ip)
    return ip


@bp.route("/")
def list():
    search_form = forms.InterfaceSearchForm(request.args)
    if search_form.query.data:
        ifaces = Interface.query.filter(db.or_(
            Interface.name.like('%' + search_form.query.data + '%'),
            Interface.host.like('%' + search_form.query.data + '%'),
        )).all()
    else:
        ifaces = Interface.query.all()
    return render_template("interfaces/list.html",
                           search_form=search_form, ifaces=ifaces)


@bp.route("/add", methods=('GET', 'POST'))
def add():
    if request.method == 'POST':
        interface = Interface()
        interface.host = request.form["host"]
        interface.name = request.form["name"]
        interface.description = request.form["description"]
        interface.public_key = request.form["publicKey"]

        if "generateIp" in request.form:
            add_ipv6_link_local_address(interface)
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


@bp.route("/edit/<int:id>", methods=("GET", "POST"))
def edit(id):
    iface = Interface.query.get_or_404(id)
    info_form = forms.InterfaceInfoForm(obj=iface)
    if info_form.validate_on_submit():
        info_form.populate_obj(iface)
        db.session.commit()
        flash("Interface updated")
        return redirect(url_for("interfaces.edit", id=id))
    return render_template("interfaces/edit/info.html",
                           iface=iface, info_form=info_form)


@bp.route("/edit/<int:id>/addresses", methods=("GET", "POST"))
def addresses(id):
    iface = Interface.query.get_or_404(id)
    if request.method == "POST":
        if request.form["action"] in {"addAddress", "addRoute"}:
            ip = IpAddress()
            try:
                ip.address = ipaddress.ip_interface(request.form["address"])
            except ValueError as e:
                flash("Error adding IP address: {}".format(e))
            else:
                if request.form["action"] == "addRoute":
                    ip.route_only = True
                    iface.route.append(ip)
                else:
                    ip.route_only = False
                    iface.address.append(ip)
                db.session.add(ip)
                db.session.commit()
                flash("IP Address added")
        elif request.form["action"] == "generateLinkLocalAddress":
            add_ipv6_link_local_address(iface)
            db.session.commit()
            flash("Link Local IP address added")
        elif request.form["action"] in {"deleteAddress", "deleteRoute"}:
            ip = IpAddress.query.get_or_404(request.form["id"])
            db.session.delete(ip)
            db.session.commit()
            flash("IP Address deleted")
        else:
            flash("Invalid action")
        return redirect(url_for("interfaces.addresses", id=id))
    return render_template("interfaces/edit/addresses.html", iface=iface)


@bp.route("/edit/<int:id>/peers", methods=("GET", "POST"))
def peers(id):
    iface = Interface.query.get_or_404(id)
    if request.method == "POST" and request.form["action"] == "deletePeer":
        peer_id = request.form['peer']
        peer = Peer.query.get_or_404(peer_id)
        db.session.delete(peer)
        db.session.commit()
        return redirect(url_for("interfaces.peers", id=id))
    return render_template("interfaces/edit/peers.html", iface=iface)


@bp.route("/edit/<int:id>/delete", methods=("GET", "POST"))
def delete(id):
    iface = Interface.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(iface)
        db.session.commit()
        flash("Interface {}@{} deleted".format(iface.host, iface.name))
        return redirect(url_for("interfaces.list"))
    return render_template("interfaces/edit/delete.html", iface=iface)


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
        return redirect(url_for("interfaces.peers", id=id))

    search_form = forms.InterfaceSearchForm(request.args)
    if search_form.query.data:
        ifaces = iface.linkable_interfaces.filter(db.or_(
            Interface.name.like('%' + search_form.query.data + '%'),
            Interface.host.like('%' + search_form.query.data + '%'),
        )).all()
    else:
        ifaces = iface.linkable_interfaces
    return render_template("interfaces/add_peer.html",
                           iface=iface, ifaces=ifaces, search_form=search_form)
