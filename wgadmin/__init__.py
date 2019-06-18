import os

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # some deploy systems set the database url in the environ
    db_url = os.environ.get("DATABASE_URL")

    if db_url is None:
        # default to a sqlite database in the instance folder
        db_url = "sqlite:///" + os.path.join(app.instance_path, "wgadmin.sqlite")
        # ensure the instance folder exists
        os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        # default secret that should be overridden in environ or config
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize Flask-SQLAlchemy and the init-db command
    db.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_addr)
    app.cli.add_command(get_addr)


    from . import auth
    app.register_blueprint(auth.bp)

    from . import interfaces
    app.register_blueprint(interfaces.bp)
    app.add_url_rule('/', endpoint='index')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app


def init_db():
    db.drop_all()
    db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('addr')
@with_appcontext
def add_addr():
    """Test command"""
    from .models import IpAddress
    import ipaddress
    a = IpAddress()
    a.address = ipaddress.ip_interface('fe80::1/64')
    print(a.id, a.version, a.mask, a._address0, a._address1, a._address2, a._address3)
    print(a.address)
    db.session.add(a)
    db.session.commit()


@click.command('paddr')
@with_appcontext
def get_addr():
    from .models import IpAddress
    for a in IpAddress.query.all():
        print(a.id, a.version, a.mask, a._address0, a._address1, a._address2, a._address3, a.address)
