
from PySide6.QtCore import QObject
from py.qt_models import SettingsModel


class Settings(QObject):
    def __init__(self, db):
        super().__init__()
        self.model = SettingsModel(db=db)
        self.model.select()
        print(self.model.rowCount())
        for x in range(0, self.model.rowCount()):
            print(self.model[x])








