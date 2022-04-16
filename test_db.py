from concurrent.futures import ThreadPoolExecutor, as_completed
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import sleep
from datetime import datetime
import json
import os
import argparse
import sys
from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.exc import OperationalError, NoResultFound
from sm.models import User
from sm.models import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pyramid.paster import bootstrap, setup_logging
from transaction import TransactionManager
from sm.models import get_tm_session


def run(tmp_dbsession, login):
    query = tmp_dbsession.query(User)
    u = query.filter(User.login == login).one()
    return u.__dict__


if __name__ == "__main__":
    env = bootstrap("development.ini")
    tmp_tm = TransactionManager(explicit=True)
    logins = ["test2", "romanov_ea", "lebedeva_da"]

    with tmp_tm:
        with ThreadPoolExecutor() as executor:
            futures = []
            for login in logins:
                tmp_dbsession = get_tm_session(
                    env["request"].registry["dbsession_factory"], tmp_tm
                )
                with env["request"].tm:
                    tmp_dbsession = env["request"].dbsession
                    futures.append(executor.submit(run, tmp_dbsession, login))
            for future in as_completed(futures):
                print(future.result())
