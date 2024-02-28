


from PySide6.QtCore import QObject, QModelIndex
from py.qt_models import SpecimensModel


class Specimens(QObject):
    def __init__(self, db):
        super().__init__()
        self.model = SpecimensModel(db=db)
        self.model.select()
        print(self.model.rowCount())
        # print(self._data_items)
        for x in range(0, self.model.rowCount()):
            print(x)
            i = QModelIndex(x, 1)
            print(self.model.itemData(i))
            # print(self.model.data())








