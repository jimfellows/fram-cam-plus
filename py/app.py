# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
from datetime import datetime

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtSql import QSqlDatabase
from PySide6.QtCore import QObject

from py.logger import Logger
from py.trawl_backdeck_db import backdeck_db
import config
from py.settings import Settings
from py.specimens import Specimens
from py.data_selector import DataSelector
from py.image_capture import ImageCapture

from qrc import qresources  # need this to import compiled qrc resources

# from py.camera import Camera

# def run():
#     Logger()
#     # setup main logger to be used globally in app
#     logger = Logger.get_root()  # return the main root logger
#     logger.info('-------------------------------------------------------------------------------------------')
#     logger.info(f'~~><(((*>  ~~><(((*> ~~><(((*>  | FRAMCam Started |  ~~><(((*>  ~~><(((*> ~~><(((*>')
#     logger.info('-------------------------------------------------------------------------------------------')
#     logger.info(f"HOME DIR = {config.HOME_DIR}")
#     logger.info(f"PYTHON DIR = {config.DATA_DIR}")
#
#     # setup main db connections to be shared globally in app
#     backdeck_db = QSqlDatabase.addDatabase('QSQLITE', 'backdeck_db')
#     backdeck_db.setDatabaseName(config.LOCAL_DB_PATH)
#     if backdeck_db.open():
#         logger.info(f"Successfully opened connection to {backdeck_db.databaseName()}")
#     else:
#         msg = f"Unable to connect to local db: {backdeck_db.databaseName()}"
#         logger.error(msg)
#         raise Exception(msg)
#
#     print('IS OPEN????')
#     print(backdeck_db.isOpen())
#
#     settings = Settings(backdeck_db)
#     specimens = Specimens(backdeck_db)
#     data_selector = DataSelector(backdeck_db)
#
#
#
#     # engine.load(os.fspath(Path(__file__).resolve().parent / "qml/MainWindow.qml"))
#     context = engine.rootContext()
#     context.setContextProperty('data_selector', data_selector)
#     context.setContextProperty('fram_cam', fram_cam)
#
#     engine.load(os.path.join(config.QML_DIR, 'MainWindow.qml'))
#
#     if not engine.rootObjects():
#         sys.exit(-1)
#     sys.exit(app.exec_())


class FramCamPlus(QObject):

    def __init__(self):
        super().__init__()
        logs = Logger()
        logs.configure()
        self._logger = logs.get_root()

        # setup main db connections to be shared globally in app
        self.db = QSqlDatabase.addDatabase('QSQLITE', 'backdeck_db')
        self.db.setDatabaseName(config.LOCAL_DB_PATH)
        if self.db.open():
            self._logger.info(f"Successfully opened connection to {self.db.databaseName()}")
        else:
            msg = f"Unable to connect to local db: {self.db.databaseName()}"
            self._logger.error(msg)
            raise Exception(msg)

        # init python classes
        self.settings = Settings(self.db, app=self)
        self.data_selector = DataSelector(self.db, app=self)
        self.image_capture = ImageCapture(self.db, app=self)

        # create qml engine, make python classes available to qml context
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.context = self.engine.rootContext()
        self.context.setContextProperty('settings', self.settings)
        self.context.setContextProperty('data_selector', self.data_selector)
        self.context.setContextProperty('image_capture', self.image_capture)

        # lastly, load up qml
        self.engine.load(os.path.join(config.QML_DIR, 'MainWindow.qml'))

        if not self.engine.rootObjects():
            sys.exit(-1)


        sys.exit(self.app.exec_())

if __name__ == "__main__":
    FramCamPlus()

