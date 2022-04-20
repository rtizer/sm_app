SM
==

Prerequisites
---------------

- Python 3.10.4
- PostgreSQL 14.2

Getting Started
---------------

- Change directory into your newly created project if not already there. Your
  current directory should be the same as this README.txt file and setup.py.

    cd sm_app

- Create a Python virtual environment, if not already created.

    python3 -m venv env

- Upgrade packaging tools, if necessary.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Define sqlalchemy.url in development.ini

- Initialize and upgrade the database using Alembic.

    - Generate your first revision.

        env/bin/alembic -c development.ini revision --autogenerate -m "init"

    - Upgrade to that revision.

        env/bin/alembic -c development.ini upgrade head

- Run your project's tests.

    env/bin/pytest

- Load default data into the database using a script.

    env/bin/initialize_sm_db development.ini

- Run JSON documents parser.

    env/bin/parse_sm_document development.ini ./path/to/data/folder

- Run your project.

    env/bin/pserve development.ini