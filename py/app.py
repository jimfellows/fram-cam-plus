
# standard imports
import os
import sys

# local imports
from py.logger import Logger
from py.config import LOCAL_DB_PATH, QML_DIR
from py.fram_cam_state import FramCamState
from py.data_selector import DataSelector
from py.camera_manager import CameraManager
from py.cam_controls import CamControls
from py.images_manager import ImageManager
from py.qsqlite import QSqlite
from py.style import Style
from py.settings import Settings
from qrc import qresources  # need this to import compiled qrc resources

# 3rd party imports
from PySide6.QtGui import QGuiApplication, QIcon, QPixmap
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject

class FramCamPlus(QObject):

    def __init__(self):
        super().__init__()
        os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

        self._logger = Logger().configure()

        # create qml engine, make python classes available to qml context
        self.app = QGuiApplication(sys.argv)
        # self.app.setWindowIcon(QPixmap('qrc:/icons/black_nautilus.ico'))  # cant seem to make this work
        self.app.setWindowIcon(QPixmap(r"resources\icons\blue_nautilus.ico"))
        self.engine = QQmlApplicationEngine()
        self.context = self.engine.rootContext()

        # setup main db connections to be shared globally in app
        self.sqlite = QSqlite(LOCAL_DB_PATH, 'fram_cam_db')
        self.sqlite.open_connection()

        # init python classes
        self.state = FramCamState(self.sqlite.db, app=self)
        self.settings = Settings(self.sqlite.db, app=self)
        self.style = Style(app=self)
        self.data_selector = DataSelector(self.sqlite.db, app=self)
        self.camera_manager = CameraManager(self.sqlite.db, self)
        self.cam_controls = CamControls(self.sqlite.db, self)
        self.image_manager = ImageManager(self.sqlite.db, self)

        self.context.setContextProperty('state', self.state)
        self.context.setContextProperty('settings', self.settings)
        self.context.setContextProperty('appStyle', self.style)
        self.context.setContextProperty('dataSelector', self.data_selector)
        self.context.setContextProperty('camControls', self.cam_controls)
        self.context.setContextProperty('imageManager', self.image_manager)

        # lastly, load up qml
        self.engine.load('qrc:/windows/MainWindow.qml')

        if not self.engine.rootObjects():
            sys.exit(-1)

        sys.exit(self.app.exec_())


if __name__ == "__main__":
    FramCamPlus()

