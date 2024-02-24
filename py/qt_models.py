
from PySide6.QtSql import (
    QSqlTableModel,
    QSqlRelationalTableModel,
    QSqlRelation,
    QSqlQueryModel,
    QSqlQuery
)

from PySide6.QtCore import (
    Property,
    Signal,
    Slot,
    QObject,
    QModelIndex,
    Qt,
    QModelRoleData
)
from py.logger import Logger
from __feature__ import snake_case  # convert Qt methods to snake


class FramCamQueryModel(QSqlQueryModel):
    """
    Subclass of QSqlQueryModel to re-use in other classes.
    TODO: better re-implementation of virtual functions, havent tried

    https://stackoverflow.com/questions/50021702/qsqlquerymodel-reference-error-in-rolename-for-listview-qml
    https://stackoverflow.com/questions/25700014/cant-display-data-from-qsqlquerymodel-in-a-qml-tableview
    """
    current_index_changed = Signal(int, arguments=['i'])
    py_index_update = Signal(int, arguments=['i'])
    model_changed = Signal()

    def __init__(self, db, sql=None):
        super().__init__()
        self._logger = Logger.get_root()
        self._db = db
        self._sql = sql
        self._query = QSqlQuery(db)
        self._current_index = -1
        self.model_changed.connect(self._on_model_loaded)
        self._roles = []

    # @Slot(QModelIndex, QModelRoleData, result="QVariant")
    def data(self, index, role):
        """
        https://stackoverflow.com/questions/25700014/cant-display-data-from-qsqlquerymodel-in-a-qml-tableview
        :param index:
        :param role:
        :return:
        """
        if role < Qt.UserRole:
            # caller requests non-UserRole data, just pass to parent
            return super(FramCamQueryModel, self).data(index, role)

        # caller requests UserRole data, convert role to column (role - Qt.UserRole -1) to return correct data
        return super(FramCamQueryModel, self).data(self.index(index.row(), role - Qt.UserRole - 1), Qt.DisplayRole)

    @Slot(result=QObject)  # don't know how to return a python array/list, so just use QVariant
    def role_name_array(self):
        # This method is used to return a list that QML understands
        list = []
        # list = self.roleNames().items()
        for key, value in self.role_names().items():
            list.append(value)

        return QObject(list)

    @Slot(int, str, result="QVariant")
    def get_value(self, model_ix, model_key):
        print("OK???")
        try:
            return self.record(model_ix).value(model_key)
        except Exception as e:
            print(e)
            return None

    @Slot(result="QVariant")
    def role_names(self):
        return {Qt.DisplayRole + i: r for i, r in enumerate(self._roles)}
    @property
    def query(self):
        return self._query

    @property
    def sql(self):
        return self._sql

    def _on_model_loaded(self):
        """
        things to do when we load the model
        :return:
        """
        self._logger.info(f"{self.__class__.__name__} model loaded")
        # if self.row_count() == 1:
        #     self.set_index_from_py(0)  # if only a single option, set it here

    @Property(int)
    def current_index(self):
        return self._current_index

    @current_index.setter
    def current_index(self, i):
        if self._current_index != i:
            self._current_index = i
            self.current_index_changed.emit(i)

    def get_ix_by_value(self, field_name, value):
        for i in range(0, self.row_count()):
            if value == self.record(i).value(field_name):
                return i

        return -1

    def set_index_from_py(self, i):
        self.py_index_update.emit(i)

    # @property
    # def row_count(self):
    #     return self.row_count(QModelIndex())

    @Slot(int, str, result="QVariant")
    def get_row_value(self, i, col_name):
        """
        Slot for qml to retrieve value given index and col name.
        model.record(i).value(name) doesnt appear to work as a slot
        directly from QSQLQueryModel, so this wrapper fills that need

        TODO: is this hitting the db or memory?

        :param i: row/model index
        :param col_name: name of column (Is this case sensitive?)
        :return: int/str/db type val
        """
        return self.record(i).value(col_name)


# class FramCamTableModel(QSqlTableModel):
#
#     def __init__(self, db, table_name, edit_strategy=QSqlTableModel.OnManualSubmit):
#         super().__init__(db=db)
#         self.set_table(table_name)
#         self.set_edit_strategy(edit_strategy)
#         self.select()  # load me, should this be in INIT?



if __name__ == '__main__':
    pass
