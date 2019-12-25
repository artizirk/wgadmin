# Wireguard admin interface

Plan is to provide a central config server with web ui and a gateway agent


# Development setup

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -r dev-requirements.txt

## Initialize database

    source venv/bin/activate
    flask init-db


## Run dev server

    source venv/bin/activate
    export FLASK_ENV=development
    flask run

## Run unittests

    source venv/bin/activate
    python -m unittest discover tests

## Update requirements.txt

    source venv/bin/activate
    pip-compile --upgrade setup.py
    pip-compile --upgrade dev-requirements.in
    # Apply updates to current venv
    pip-sync dev-requirements.txt requirements.txt
