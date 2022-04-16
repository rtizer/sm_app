import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.exc import NoResultFound, OperationalError
from transaction import TransactionManager

from .. import models


def parse_document(dbsession, file):
    with open(file) as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            return False

        try:
            query = dbsession.query(models.user.User)
            u = query.filter(models.user.User.login == data["login"]).one()
        except NoResultFound:
            u = models.user.User(login=data["login"])
            dbsession.add(u)
        doc = models.document.Document(data=json.dumps(data))
        dbsession.add(doc)
        u.document.append(doc)

        os.remove(file)

        return f"Parsed {file}... Login {data['login']}"


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_uri",
        help="Configuration file, e.g., development.ini",
    )
    parser.add_argument(
        "path",
        help="Folder path, ./data",
    )
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    try:
        tm = TransactionManager(explicit=True)
        while True:
            files = sorted(
                [f"{args.path}/{file}" for file in os.listdir(f"{args.path}/")]
            )
            with tm:
                with ThreadPoolExecutor() as executor:
                    futures = []
                    for file in files:
                        dbsession = models.get_tm_session(
                            env["request"].registry["dbsession_factory"], tm
                        )
                        futures.append(executor.submit(parse_document, dbsession, file))
                    for future in as_completed(futures):
                        print(future.result())
            sleep(1)

    except OperationalError:
        print(
            """
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to initialize your database tables with `alembic`.
    Check your README.txt for description and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.
            """
        )
