

from PySide6.QtCore import QObject, Property, Signal, Slot, QThread
from py.logger import Logger
import subprocess
import os
import platform

TEST_IP = '127.0.0.1'

class PingWorker(QObject):
    """
    Class to run ping tests for Victor in a thread
    """
    pingStarted = Signal()
    pingEnded = Signal()
    pingStatus = Signal(bool, arguments=['ping_status'])

    def __init__(self, ip_address=None):
        super().__init__()
        self._logger = Logger.get_root()
        self._is_running = False
        self._ip_address = ip_address
        self._success = False

    @property
    def ip_address(self):
        return self._ip_address

    @ip_address.setter
    def ip_address(self, new_ip):
        self._ip_address = new_ip

    def run(self):
        self._is_running = True
        self._success = self.ping_test()
        self.pingStatus.emit(self._success)

    def ping_test(self):
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self._ip_address]
        self._logger.debug(f"Pinging subnet: {command}")

        result = subprocess.run(command, stdout=subprocess.PIPE)
        output = result.stdout.decode('utf8')
        if "Request timed out." in output or "100% packet loss" in output or 'Destination host unreachable' in output:
            return False
        return True


class Settings(QObject):

    vesselSubnetChanged = Signal(str, arguments=['new_subnet'])
    uiModeChanged = Signal(str, arguments=['new_mode'])
    backdeckPinged = Signal(bool, arguments=['pingResult'])
    pingStatusChanged = Signal()
    backdeckDbChanged = Signal(str, arguments=['new_path'])
    wheelhouseDataDirChanged = Signal(str, arguments=['new_dir'])
    wheelhouseDataDirVerified = Signal(bool, arguments=['isValid'])
    backdeckDbVerified = Signal(bool, arguments=['isValid'])

    def __init__(self, db, app=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._app = app
        self._logger = Logger.get_root()

        # for now the user doesnt set these, but are based on the subnet setting
        self._cur_vessel_subnet = None
        self._cur_backdeck_ip = None
        self._cur_backdeck_db = None
        self._cur_wheelhouse_ip = None

        # vars that the user can set from the UI, lets try to pull them from FRAM_CAM_STATE on startup
        self._cur_ui_mode = self._app.state.get_state_value('Current UI Mode')
        self._cur_backdeck_db = self._app.state.get_state_value('Current Backdeck DB')
        self._cur_wheelhouse_data_dir = self._app.state.get_state_value('Current Wheelhouse Data Dir')

        # if backdeck/wheelhouse ping thread is running, set to true
        self._is_ping_running = False

        # ping the subnet/access point?
        self._subnet_ping_worker = PingWorker()

        # backdeck ping worker/thread setup
        self._backdeck_ping_worker = PingWorker()
        self._backdeck_ping_thread = QThread()
        self._backdeck_ping_worker.moveToThread(self._backdeck_ping_thread)
        self._backdeck_ping_worker.pingStatus.connect(self._backdeck_pinged)
        # TODO: started signal isnt calling update_ping_status in a timely fashion, why???
        self._backdeck_ping_thread.started.connect(self._backdeck_ping_worker.run)
        self._backdeck_ping_worker.pingStarted.connect(self._update_ping_status)
        # self._backdeck_ping_thread.started.connect(self._update_ping_status)
        self._backdeck_ping_thread.finished.connect(self._update_ping_status)

        # wheelhousee ping worker/thread setup
        self._wheelhouse_ping_worker = PingWorker()
        self._wheelhouse_ping_thread = QThread()
        self._wheelhouse_ping_worker.pingStarted.connect(self._update_ping_status)
        self._wheelhouse_ping_thread.finished.connect(self._update_ping_status)

        self.curVesselSubnet = self._app.state.get_state_value('Current Vessel Subnet')

    def _update_ping_status(self):
        self._logger.debug(f"Updating ping status")
        _status = self._wheelhouse_ping_thread.isRunning() or self._backdeck_ping_thread.isRunning()
        if self._is_ping_running != _status:
            self._is_ping_running = _status
            self._logger.debug(f"Ping status set to {_status}")
            self.pingStatusChanged.emit()

    @Property(bool, notify=pingStatusChanged)
    def isPingRunning(self):
        return self._is_ping_running

    @Property(str, notify=vesselSubnetChanged)
    def curVesselSubnet(self):
        return self._cur_vessel_subnet

    @curVesselSubnet.setter
    def curVesselSubnet(self, new_subnet):
        if self._cur_vessel_subnet != new_subnet:
            self._cur_vessel_subnet = new_subnet
            self._app.state.set_state_value('Current Vessel Subnet', new_subnet)
            self._backdeck_ping_worker.ip_address = self.curBackdeckIp
            self._wheelhouse_ping_worker.ip_address = self.curWheelhouseIp
            self.vesselSubnetChanged.emit(new_subnet)

    def _backdeck_pinged(self, status):
        self.backdeckPinged.emit(status)
        self._backdeck_ping_thread.quit()

    @Slot()
    def pingBackdeck(self):
        self._backdeck_ping_thread.start()

    @Property(str, notify=vesselSubnetChanged)
    def curBackdeckIp(self):
        if self._cur_vessel_subnet == TEST_IP:
            return TEST_IP
        else:
            return f"{self._cur_vessel_subnet}.{5}"

    @Property(str, notify=vesselSubnetChanged)
    def curWheelhouseIp(self):
        if self._cur_vessel_subnet == TEST_IP:
            return TEST_IP
        else:
            return f"{self._cur_vessel_subnet}.{2}"

    @Property(str, notify=uiModeChanged)
    def curUiMode(self):
        return self._cur_ui_mode

    @curUiMode.setter
    def curUiMode(self, new_mode):
        if self._cur_ui_mode != new_mode:
            self._cur_ui_mode = new_mode
            self._app.state.set_state_value('Current UI Mode', new_mode)
            self.uiModeChanged.emit(new_mode)


    @Property(str, notify=backdeckDbChanged)
    def curBackdeckDb(self):
        return self._cur_backdeck_db

    @curBackdeckDb.setter
    def curBackdeckDb(self, new_path):
        if self._cur_backdeck_db != new_path:
            self._cur_backdeck_db = new_path
            self._app.state.set_state_value('Current Backdeck DB', new_path)
            self.backdeckDbChanged.emit(new_path)

    @Property(str, notify=wheelhouseDataDirChanged)
    def curWheelhouseDataDir(self):
        return self._cur_wheelhouse_data_dir

    @curWheelhouseDataDir.setter
    def curWheelhouseDataDir(self, new_dir):
        if self._cur_wheelhouse_data_dir != new_dir:
            self._cur_wheelhouse_data_dir = new_dir
            self._app.state.set_state_value('Current Wheelhouse Data Dir', new_dir)
            self.wheelhouseDataDirChanged.emit(new_dir)

    @Slot()
    def verifyWheelhouseDataDir(self):
        self._logger.debug(f"Verifying wheelhouse data dir: {self._cur_wheelhouse_data_dir}")
        if self._cur_wheelhouse_data_dir:
            status = os.path.isdir(self._cur_wheelhouse_data_dir)
            self.wheelhouseDataDirVerified.emit(status)

    @Slot()
    def verifyBackdeckDb(self):
        self._logger.debug(f"Verifying backdeck database data dir: {self._cur_backdeck_db}")
        if self._cur_backdeck_db:
            status = os.path.isfile(self._cur_backdeck_db)
            self.backdeckDbVerified.emit(status)

