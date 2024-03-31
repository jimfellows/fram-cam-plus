
import subprocess, platform, re
from PySide6.QtCore import QObject, Slot, Property, Signal


class WifiConnectionWorker(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        pass

class S3UploadWorker(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        pass

class CloudUploader(QObject):

    checkAvailableNetworks = Signal()

    def __init__(self, db, app=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._app = app

    @Property("QVariantList", notify=checkAvailableNetworks)
    def wifiNetworks(self):
        return self.getAvailableNetworks()

    @Slot()
    def getAvailableNetworks(self) -> list[str]:
        """
        subprocess gets list of wifi networks out in the format, below, and regex uses
        a positive lookupback to get the names after SSID N : <NETWORK NAME>

            Interface name : Wi-Fi
            There are 7 networks currently visible.

            SSID 1 : YOUR WIFI NETWORK NAME
                Network type            : Infrastructure
                Authentication          : WPA2-Personal
                Encryption              : CCMP
        :return: str[]
        """
        # Check if the OS is Windows, if other platform, need to implement new logic
        if platform.system() == "Windows":
            list_networks_command = 'netsh wlan show networks' # Command to list Wi-Fi networks on Windows using netsh.
            output = subprocess.check_output(list_networks_command, shell=True, text=True)
            # TODO: this only works if there are less than 10...
            return [x for x in re.findall('(?<=SSID \d : ).*', output) if x]  # positive lookback gets str after "SSID <N> : "


if __name__ == '__main__':
    cu = CloudUploader('a')
    print(cu.getAvailableNetworks())