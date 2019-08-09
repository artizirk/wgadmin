# Wireguard admin interface

Plan is to provide a central config server with web ui and a gateway agent


# Development setup

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirement.txt

## Run dev server

    source venv/bin/activate
    flask run

## Run unittests

    source venv/bin/activate
    python -m unittest discover tests
