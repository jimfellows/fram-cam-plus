# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
from datetime import datetime

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtSql import QSqlDatabase

from py.logger import Logger
from py.trawl_backdeck_db import backdeck_db
import py.config as config
from py.settings import Settings

# from py.camera import Camera

def run():
    Logger()
    # setup main logger to be used globally in app
    logger = Logger.get_root()  # return the main root logger
    logger.info('-------------------------------------------------------------------------------------------')
    logger.info(f'~~><(((*>  ~~><(((*> ~~><(((*>  | FRAMCam Started |  ~~><(((*>  ~~><(((*> ~~><(((*>')
    logger.info('-------------------------------------------------------------------------------------------')
    logger.info(f"PYTHON DIR = {config.PYTHON_DIR}")
    logger.info(f"HOME DIR = {config.HOME_DIR}")
    logger.info(f"PYTHON DIR = {config.DATA_DIR}")

    # setup main db connections to be shared globally in app
    backdeck_db = QSqlDatabase.addDatabase('QSQLITE', 'backdeck_db')
    backdeck_db.setDatabaseName(config.LOCAL_DB_PATH)
    if backdeck_db.open():
        logger.info(f"Successfully opened connection to {backdeck_db.databaseName()}")
    else:
        msg = f"Unable to connect to local db: {backdeck_db.databaseName()}"
        logger.error(msg)
        raise Exception(msg)

    settings = Settings(backdeck_db)

    exit()

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load(os.fspath(Path(__file__).resolve().parent / "qml/main.qml"))
    context = engine.rootContext()

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()

