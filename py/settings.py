

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
        print("starting ping!!!!")
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', self._ip_address]

        result = subprocess.run(command, stdout=subprocess.PIPE)
        output = result.stdout.decode('utf8')
        if "Request timed out." in output or "100% packet loss" in output or 'Destination host unreachable' in output:
            return False
        return True

    def ping_test_old(self):
        print("PINGING FROM TRHEAD!")

        r = os.system('ping %s -n 1' % (self._ip_address,))
        print(r)


class Settings(QObject):

    vesselSubnetChanged = Signal(str, arguments=['new_subnet'])
    uiModeChanged = Signal(str, arguments=['new_mode'])
    backdeckPinged = Signal(bool, arguments=['pingResult'])
    pingStatusChanged = Signal()

    def __init__(self, db, app=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._app = app
        self._cur_vessel_subnet = None
        self._cur_backdeck_ip = None
        self._cur_backdeck_db = None
        self._cur_wheelhouse_ip = None
        self._cur_ui_mode = None
        self._is_ping_running = False

        self._subnet_ping_worker = PingWorker()
        # self._subnet_p

        self._backdeck_ping_worker = PingWorker()
        self._backdeck_ping_thread = QThread()
        self._backdeck_ping_worker.moveToThread(self._backdeck_ping_thread)
        self._backdeck_ping_worker.pingStatus.connect(self._backdeck_pinged)
        self._backdeck_ping_thread.started.connect(self._backdeck_ping_worker.run)
        self._backdeck_ping_thread.started.connect(self._update_ping_status)

        self._wheelhouse_ping_worker = PingWorker()
        self._wheelhouse_ping_thread = QThread()

        self._wheelhouse_ping_thread.started.connect(self._update_ping_status)
        self._wheelhouse_ping_thread.finished.connect(self._update_ping_status)

        self._backdeck_ping_thread.finished.connect(self._update_ping_status)

    def _update_ping_status(self):
        print("UPDATING PING STATUS")
        _status = self._wheelhouse_ping_thread.isRunning() or self._backdeck_ping_thread.isRunning()
        print(f"STATUS = {_status}")
        if self._is_ping_running != _status:
            self._is_ping_running = _status
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
        print("STARTED")
        self._backdeck_ping_thread.start()

    # @Property(QObject)
    # def pingInProcess


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



