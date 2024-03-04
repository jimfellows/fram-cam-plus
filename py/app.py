

# standard imports
import os
import sys

# local imports
from py.logger import Logger
from config import LOCAL_DB_PATH, QML_DIR
from py.fram_cam_state import FramCamState
from py.data_selector import DataSelector
from py.camera_manager import CameraManager
from py.qsqlite import QSqlite
from py.style import Style
from qrc import qresources  # need this to import compiled qrc resources

# 3rd party imports
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject

class FramCamPlus(QObject):

    def __init__(self):
        super().__init__()
        self._logger = Logger().configure()

        # create qml engine, make python classes available to qml context
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.context = self.engine.rootContext()

        # setup main db connections to be shared globally in app
        self.sqlite = QSqlite(LOCAL_DB_PATH, 'fram_cam_db')
        self.sqlite.open_connection()

        # init python classes
        self.state = FramCamState(self.sqlite.db, app=self)
        self.style = Style()
        self.data_selector = DataSelector(self.sqlite.db, app=self)
        self.camera_manager = CameraManager(self.sqlite.db, self)

        self.context.setContextProperty('state', self.state)
        self.context.setContextProperty('style', self.style)
        self.context.setContextProperty('data_selector', self.data_selector)
        self.context.setContextProperty('camera_manager', self.camera_manager)

        # lastly, load up qml
        self.engine.load(os.path.join(QML_DIR, 'MainWindow.qml'))

        if not self.engine.rootObjects():
            sys.exit(-1)

        sys.exit(self.app.exec_())

if __name__ == "__main__":
    FramCamPlus()

