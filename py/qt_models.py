
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
    QModelRoleData,
    QAbstractListModel,
    QSortFilterProxyModel
)
from py.utils import Utils
from py.logger import Logger
import os
import re
from datetime import datetime

class FramCamSqlListModel(QAbstractListModel):
    """
    Subclass of QAbstractListModel which loads data from SQL query.
    Class is written to be read-only, but may be subclassed again to add write functionality
    """
    selectedIndexChanged = Signal(int, arguments=['index'])
    selectIndexInUI = Signal(int, arguments=['index'])

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._logger = Logger.get_root()
        self._db = db
        self._sql = None
        self._query_model = QSqlQueryModel()
        self._query = QSqlQuery(self._db)
        self._data = []
        self._selected_index = -1
        self._bind_params = {}

    @property
    def sql(self):
        return self._sql

    @sql.setter
    def sql(self, new_sql):
        if self._sql != new_sql:
            self._sql = new_sql
            self._query.prepare(self._sql)

    def data(self, index: QModelIndex, role: int):
        """
        re-implementation of super class' virtual method.  Retrieve single data point using index of
        _data and key val expected in dictionary
        :param index: QtModelIndex
        :param role: integer representation of role
        :return: whatever val is pulled from SQL query and stuffed into dict
        """
        if not index.isValid():
            return
        try:
            return self._data[index.row()][self.roleNames()[role].decode('utf-8')]
        except Exception as e:
            self._logger.error(f"Failed to retrieve data from {self.__class__.__name__}: {e}")
            return None

    def setData(self, row: int, value: any, role_name: str):
        """
        re-implementation of virtual function to allow editable model
        set role data to value at specific index in _data list
        https://doc.qt.io/qtforpython-6/PySide6/QtCore/QAbstractItemModel.html#PySide6.QtCore.QAbstractItemModel.setData
        """
        _index = self.index(row, 0)
        if not _index.isValid():
            self._logger.error(f"Invalid index used for setData, row {row} = {value}")
            return False
        try:
            role_num = self.getRoleByName(role_name)  # convert name of role to its integer number
            # TODO: I'm converting to role_name to role_num back to role_num, necessary?
            self._data[row][self.roleNames()[role_num].decode('utf-8')] = value  # use role no as key to get str
            self.dataChanged.emit(_index, _index)  # tell model something has updated
            return True
        except Exception as e:
            self._logger.error(f"Error in {self.__class__.__name__}.setData: {e.__name__} {e}")
            return False

    def flags(self, index):
        return Qt.ItemIsEditable

    def roleNames(self):
        """
        re-implementation of super class' virtual method.  Role names dynamically built based on return
        of the SQL and the record produced.  Note that these are cast to lowercase
        :return: dict {0: 'first_field', 1: 'second_field'...}
        """
        _rec = self._query_model.record()
        _fields = [_rec.field(f).name().lower() for f in range(0, _rec.count())]  # iterate over cols and return name
        return {Qt.DisplayRole + i: r.encode("utf-8") for i, r in enumerate(_fields)}

    def rowCount(self, index=0):
        """
        re-implementation of super class' virtual method. How many current rows do we have stored in model?
        :param index: just making virtual method happy
        :return: int
        """
        return len(self._data)

    @Property(int, notify=selectedIndexChanged)
    def selectedIndex(self):
        return self._selected_index

    @selectedIndex.setter
    def selectedIndex(self, new_index):
        if self._selected_index != new_index:
            self._selected_index = new_index
            self.selectedIndexChanged.emit(new_index)
            self._logger.debug(f"{self.__class__.__name__} current index set from {self._selected_index} --> {new_index}")

    def clearModel(self):
        self.beginResetModel()
        self._data = []
        self.endResetModel()
        self._logger.debug(f"{self.__class__.__name__} data cleared from model.")

    def setBindParam(self, key, val):
        try:
            old_val = self._bind_params[key]
            is_updated = old_val != val
        except KeyError:
            is_updated = True

        self._bind_params[key] = val
        return is_updated

    def clearBindParams(self):
        self._bind_params = {}

    def loadModel(self, bind_params=None):
        """
        basic loading of model from SQL results.  If param binding is required
        :return:
        """
        self.clearModel()
        if bind_params:
            for k, v in bind_params.items():
                self._logger.debug(f"Binding param {k}={v}")
                self._query.bindValue(k, v)
        self._query.exec()
        self._query_model.setQuery(self._query)
        self.beginInsertRows(QModelIndex(), 0, self._query_model.rowCount() - 1)
        for _i in range(self._query_model.rowCount()):
            self._data.append(Utils.qrec_to_dict(self._query_model.record(_i)))
        self.endInsertRows()
        self._logger.debug(f"Loaded {self._query_model.rowCount()} items to {self.__class__.__name__} model.")

    def appendRow(self, data_item, index=None):
        """
        add a single row to the model
        :param data_item: dict, record converted to dict
        :param index: location of insert
        :return:
        """
        index = self.rowCount() if index is None else index
        self.beginInsertRows(QModelIndex(), index, index)
        self._data.insert(index, data_item)
        self.endInsertRows()

    @Slot(int, str, result="QVariant")
    def getData(self, index, prop_name):
        if index == -1:
            return
        try:
            return self._data[index][prop_name]
        except IndexError:
            self._logger.error(f"Row {index} not found in model {self.__class__.__name__}, unable to getData")
        except KeyError:
            self._logger.error(f"{prop_name} not found in model {self.__class__.__name__}, unable to getData.")

    def getCurrentData(self, prop_name):
        return self.getData(self._selected_index, prop_name)

    def getItem(self, index):
        if index == -1:
            return None
        try:
            return self._data[index]
        except IndexError:
            self._logger.error(f"Row {index} not found in model {self.__class__.__name__}, unable to getItem")

    def getItemIndex(self, item):
        # for some reason self._data.index(item) didnt work...
        for i, data_item in enumerate(self._data):
            if item == data_item:
                return i
        return -1

    def getRowIndexByValue(self, role_name, value):
        """
        Note that this will return the first match in the model, so using a unique val to search
        on is often desired
        :param field_name:
        :param value:
        :return:
        """
        try:
            return [i for i, row in enumerate(self._data) if row[role_name] == value][0]
        except KeyError:
            self._logger.error(f"Role {role_name} not found in {self.__class__.__name__}")
            return -1

        except IndexError:
            self._logger.warning(f"Row with {role_name}={value} not found, returning -1")
            return -1

    def removeItem(self, row_index):
        if row_index == -1:
            return

        self.beginRemoveRows(QModelIndex(), row_index, row_index)
        del self._data[row_index]
        self.endRemoveRows()

    def getRoleByName(self, role_name):
        try:
            return {v: k for k, v in self.roleNames().items()}[role_name.encode('utf-8')]
        except KeyError:
            self._logger.warning(f"Role {role_name} does not exist in model.")


class FramCamFilterProxyModel(QSortFilterProxyModel):

    proxyIndexChanged = Signal(int, arguments=['proxy_index'])
    selectIndexInUI = Signal(int, arguments=['proxy_index'])  # use me to simulate a click of proxy model item

    def __init__(self, source_model, parent=None, name=None):
        super().__init__(parent)
        self._logger = Logger.get_root()
        self._proxy_index = -1
        self.setSourceModel(source_model)
        self._name = name if name else self.__class__.__name__

    @Property(int, notify=proxyIndexChanged)
    def proxyIndex(self):
        return self._proxy_index

    @proxyIndex.setter
    def proxyIndex(self, new_index):
        self._logger.debug(f"Setting {self._name} proxy index: {self._proxy_index} --> {new_index}")
        if self._proxy_index != new_index:
            self._proxy_index = new_index
            self.proxyIndexChanged.emit(new_index)
            self.setSourceModelIndex(new_index)

    @Property(int, notify=proxyIndexChanged)
    def sourceIndex(self):
        return self.getSourceRowFromProxy(self._proxy_index)

    @Slot(int, result=int)
    def getSourceRowFromProxy(self, proxy_row: int) -> int:
        """
        map proxy row back to source, taking proxy index in as input
        :param proxy_row: int, row index of proxy
        :return: int, row index of underlying source model
        """
        _proxy_index = self.index(proxy_row, 0, QModelIndex())
        _source_index = self.mapToSource(_proxy_index)
        self._logger.debug(f"Converted {self._name} proxy row {proxy_row} to source row {_source_index.row()}")
        return _source_index.row()

    @Slot(int, result=int)
    def getProxyRowFromSource(self, source_row: int) -> int:
        """
        map the proxy from with the source row as input
        :param source_row: int, underlying model row index
        :return: int, proxy index mapped from source
        """
        _source_index = self.sourceModel().index(source_row, 0, QModelIndex())
        _proxy_index = self.mapFromSource(_source_index)
        self._logger.debug(f"Converted {self._name} source model row {source_row} to proxy row {_proxy_index.row()}")
        return _proxy_index.row()

    @Slot(int)
    def setSourceModelIndex(self, i):
        """
        allows us to translate selected row index of proxy model and convert it to the row index of the source
        :param i: int, row index
        :return:
        """
        _proxy_index = self.index(i, 0, QModelIndex())
        _source_index = self.mapToSource(_proxy_index)
        self._logger.debug(f"Setting source model index to {_source_index.row()} from proxy model {self._name}")
        try:
            self.sourceModel().selectedIndex = _source_index.row()
        except AttributeError:
            self._logger.error(f"Source model of {self._name} does not have currentIndex property!")

    def filterRoleOnStr(self, role_name: str, value: str):
        self._logger.debug(f"Filtering {self._name} ({self.rowCount} rows), role {role_name}={value}")
        try:
            _role_num = self.sourceModel().getRoleByName(role_name)
        except AttributeError:
            self._logger.error(f"Source model of {self._name} does not have getRoleByName method!")
            return

        self.invalidateRowsFilter()
        self.setFilterRole(_role_num)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterFixedString(value)
        self._logger.debug(f"{self._name} rows after fixed str filter: {self.rowCount()}")

    def filterRoleOnRegex(self, role_name: str, regex_pattern: str):
        """
        specify name of role and a regex pattern to filter proxy model with
        :param role_name: name of field/role we'd like to filter on
        :param regex_pattern: regular expression pattern that QT likes
        """
        self._logger.debug(f"Filtering {self._name} ({self.rowCount()} rows), role {role_name}, regex: {regex_pattern}")
        try:
            _role_num = self.sourceModel().getRoleByName(role_name)
        except AttributeError:
            self._logger.error(f"Source model of {self._name} does not have getRoleByName method!")
            return

        #self.invalidateRowsFilter()
        self.setFilterRole(_role_num)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterRegularExpression(regex_pattern)
        self._logger.debug(f"{self._name} rows after regex filter: {self.rowCount()}")

    def filterRoleWildcard(self, role_name: str, pattern: str):
        """
        specify name of role and a regex pattern to filter proxy model with
        :param role_name: name of field/role we'd like to filter on
        :param regex_pattern: regular expression pattern that QT likes
        """
        self._logger.debug(f"Filtering {self._name} ({self.rowCount()} rows), role {role_name}, wildcard*: {pattern}")
        try:
            _role_num = self.sourceModel().getRoleByName(role_name)
        except AttributeError:
            self._logger.error(f"Source model of {self.__class__.__name__} does not have getRoleByName method!")
            return

        self.setFilterRole(_role_num)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterWildcard(pattern)
        self._logger.debug(f"{self._name} rows after wildcard filter: {self.rowCount()}")




if __name__ == '__main__':
    pass



