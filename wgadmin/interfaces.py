from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .auth import login_required


bp = Blueprint("interfaces", __name__)


@bp.route("/")
def interface_list():
    return render_template("interfaces/list.html")
