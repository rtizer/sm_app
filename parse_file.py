from concurrent.futures import ThreadPoolExecutor
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
from sm.models.user import User
from sm.models.document import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from transaction import TransactionManager
from sm.models import get_tm_session

SRC_PATH = './sm/scripts/json'

class MyHandler(FileSystemEventHandler):
    
    def __get_db_session(self):
        with self.__tm:
            return get_tm_session(self.__dbsession_factory, self.__tm)
    
    def __init__(self, *args, **kwargs):
        super(MyHandler, self).__init__(*args)
        self.__tm = kwargs.get('tm')
        self.__dbsession_factory = kwargs.get('dbsession_factory')
        
    
    def __process(self, file):
        with open(file) as f:
            data = json.load(f)
            print(f"Contains: {data}")
            
            session = self.__get_db_session()
            
            try:
                query = session.query(User)
                u = query.filter(User.login == data["login"]).one()
            except NoResultFound:
                u = User(
                    login=data["login"]
                )
                session.add(u)
            
            doc = Document(
                data = json.dumps(data)
            )
            session.add(doc)
            
            u.document.append(doc)
            
            session.commit()
            
            session.close()
    
            
    def cold_start(self):
        files = sorted([f"{SRC_PATH}/{file}" for file in os.listdir(f"{SRC_PATH}/")])
        with ThreadPoolExecutor() as executor:
            for i, result in enumerate(executor.map(self.__process, files)):
                print(f"Processed {files[i]}...")
    
    def on_any_event(self, event):
        print(event.event_type, event.src_path)

    def on_created(self, event):
        print("on_created", event.src_path)
        with ThreadPoolExecutor() as executor:
            executor.submit(self.__process, event.src_path)

    def on_deleted(self, event):
        print("on_deleted", event.src_path)

    def on_modified(self, event):
        print("on_modified", event.src_path)

    def on_moved(self, event):
        print("on_moved", event.src_path)


if __name__ == "__main__":
    env = bootstrap('development.ini')
    tmp_tm = TransactionManager(explicit=True)
    event_handler = MyHandler(
        tm=tmp_tm, 
        dbsession_factory=env['request'].registry['dbsession_factory']
        )
    # event_handler.cold_start()
    observer = Observer()
    observer.schedule(event_handler, path=SRC_PATH, recursive=False)
    observer.start()
    
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()