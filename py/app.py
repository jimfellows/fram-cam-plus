
# standard imports
import os
import sys
import time

# local imports
from py.logger import Logger
from py.config import LOCAL_DB_PATH, QML_DIR
from py.fram_cam_state import FramCamState
from py.data_selector import DataSelector
from py.cam_controls import CamControls
from py.images_manager import ImageManager
from py.qsqlite import QSqlite
from py.style import Style
from py.settings import Settings
from py.cloud_uploader import CloudUploader
from qrc import qresources  # need this to import compiled qrc resources

# 3rd party imports
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, QTextStream
from PySide6.QtNetwork import QLocalServer, QLocalSocket




class QSingleApplication(QApplication):
    """
    very basic class that will, if another app is running with the same id on local server
    return isRunning = True.  More comprehensive examples exist out there, for now this is good enough:

    https://github.nwfsc2.noaa.gov/nwfsc-fram/pyFieldSoftware/blob/master/py/common/QSingleApplication.py
    https://gist.github.com/blaxter/5413516
    https://forum.qt.io/topic/5616/pyside-qtsingleapplication

    """
    def __init__(self, app_id, *argv):

        super().__init__(*argv)
        self._app_id = app_id

        # Is there another instance running?
        self._outSocket = QLocalSocket()
        self._outSocket.connectToServer(self._app_id)
        self._isRunning = self._outSocket.waitForConnected()

        if self._isRunning:
            # Yes, there is.
            self._outStream = QTextStream(self._outSocket)

        else:
            self._server = QLocalServer()
            self._server.listen(self._app_id)

    def isRunning(self):
        return self._isRunning


class FramCamPlus(QObject):

    def __init__(self):
        super().__init__()
        os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"  # necessary?

        self._logger = Logger().configure()
        self._logger.info('-------------------------------------------------------------------------------------------')
        self._logger.info(f'~~><((*>  ~~><((*>  ~~><((*> | FramCam+ starting up | ~~><((*>  ~~><((*>  ~~><((*>')
        self._logger.info('-------------------------------------------------------------------------------------------')

        self.app = QSingleApplication('018f72bf-b6c2-7ce7-85ec-17c168491a30', sys.argv)
        if self.app.isRunning():
            # if another instance of framcam is already running, pop error dialog and call exec_() early
            dlg = QMessageBox()
            dlg.setWindowTitle('FRAMCam already running')
            dlg.setText("ERROR: Unable to run multiple FRAMCam instances!\n\nShutting down...")
            dlg.show()
            sys.exit(self.app.exec_())

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
        self.cam_controls = CamControls(self.sqlite.db, self)
        self.data_selector = DataSelector(self.sqlite.db, app=self)
        self.image_manager = ImageManager(self.sqlite.db, self)
        self.cloud_uploader = CloudUploader(self.sqlite.db, self)

        self.context.setContextProperty('state', self.state)
        self.context.setContextProperty('settings', self.settings)
        self.context.setContextProperty('appStyle', self.style)
        self.context.setContextProperty('dataSelector', self.data_selector)
        self.context.setContextProperty('camControls', self.cam_controls)
        self.context.setContextProperty('imageManager', self.image_manager)
        self.context.setContextProperty('cloudUploader', self.cloud_uploader)

        # lastly, load up qml
        self.engine.load('qrc:/windows/MainWindow.qml')

        if not self.engine.rootObjects():
            sys.exit(-1)

        sys.exit(self.app.exec_())


if __name__ == "__main__":
    FramCamPlus()

