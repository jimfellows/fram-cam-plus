
from PySide6.QtSql import QSqlTableModel, QSqlRelationalTableModel



class SettingsModel(QSqlTableModel):
    def __init__(self, db):
        super().__init__(db=db)
        self.setTable('FRAM_CAM_SETTINGS')


class SpecimensModel(QSqlRelationalTableModel):
    def __init__(self, db):
        super().__init__(db=db)
        self.setTable('FRAM_CAM_SETTINGS')




