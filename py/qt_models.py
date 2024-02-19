
from PySide6.QtSql import QSqlTableModel, QSqlRelationalTableModel, QSqlRelation



class SettingsModel(QSqlTableModel):
    def __init__(self, db):
        super().__init__(db=db)
        self.setTable('FRAM_CAM_SETTINGS')


class SpecimensModel(QSqlRelationalTableModel):
    def __init__(self, db):
        super().__init__(db=db)
        self.setTable('SPECIMEN')
        self.setRelation(2, QSqlRelation('CATCH', 'CATCH_ID', 'DISPLAY_NAME'))
        self.setRelation(3, QSqlRelation('SPECIES_SAMPLING_PLAN', 'SPECIES_SAMPLING_PLAN_ID', 'PLAN_NAME'))
        self.select()






