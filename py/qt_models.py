
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
from py.logger import Logger
from py.utils import Utils


class FramCamSqlListModel(QAbstractListModel):
    """
    Subclass of QAbstractListModel which loads data from SQL query.
    Class is written to be read-only, but may be subclassed again to add write functionality
    """

    currentIndexChanged = Signal(int, arguments=['newIndex'])

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._logger = Logger.get_root()
        self._db = db
        self._sql = None
        self._query_model = QSqlQueryModel()
        self._query = QSqlQuery(self._db)
        self._data = []
        self._current_index = -1
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

    @Property(int, notify=currentIndexChanged)
    def currentIndex(self):
        return self._current_index

    @currentIndex.setter
    def currentIndex(self, new_index):
        if self._current_index != new_index:
            self._current_index = new_index
            self.currentIndexChanged.emit(new_index)
            self._logger.info(f"{self.__class__.__name__} current index changed to {new_index}")

    def clearModel(self):
        self.beginResetModel()
        self._data = []
        self.endResetModel()
        self._logger.info(f"{self.__class__.__name__} data cleared from model.")

    def setBindParam(self, key, val):
        self._bind_params[key] = val

    def loadModel(self):
        """
        basic loading of model from SQL results.  If param binding is required
        :return:
        """
        self.clearModel()
        for k, v in self._bind_params.items():
            self._logger.info(f"Binding param {k}={v}")
            self._query.bindValue(k, v)
        self._query.exec()
        self._logger.info(f"{self.__class__.__name__} loadModel query returned {self._query_model.rowCount()} results")
        self._query_model.setQuery(self._query)
        self.beginInsertRows(QModelIndex(), 0, self._query_model.rowCount() - 1)
        for _i in range(self._query_model.rowCount()):
            self._data.append(Utils.qrec_to_dict(self._query_model.record(_i)))
        self.endInsertRows()
        self._logger.info(f"Loaded {self._query_model.rowCount()} items to {self.__class__.__name__} model.")

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

    def getData(self, index, prop_name):
        try:
            return self._data[index][prop_name]
        except IndexError:
            self._logger.error(f"Row {index} not found in model {self.__class__.__name__}, unable to getData")
        except KeyError:
            self._logger.error(f"{prop_name} not found in model {self.__class__.__name__}, unable to getData.")

    def getItem(self, index):
        try:
            print(f"Getting item at index {index} for {self.__class__.__name__}")
            return self._data[index]
        except IndexError:
            self._logger.error(f"Row {index} not found in model {self.__class__.__name__}, unable to getItem")

    def removeItem(self, row_index):
        self.beginRemoveRows(QModelIndex(), row_index, row_index)
        del self._data[row_index]
        self.endRemoveRows()

    def getRoleByName(self, role_name):
        try:
            return {v: k for k, v in self.roleNames().items()}[role_name.encode('utf-8')]
        except KeyError:
            self._logger.warning(f"Role {role_name} does not exist in model.")


class HaulsModel(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        self.sql = 'select * from fram_cam_hauls order by cast(haul_number as bigint) desc'


class CatchesModel(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        self.sql = '''
            select  distinct
                    display_name
                    ,haul_number
                    ,fram_cam_haul_id
                    ,fram_cam_catch_id
                    
            from    BIO_OPTIONS_VW
            where   opt_instance = 1
                    and fram_cam_haul_id = :fram_cam_haul_id
        '''


class ProjectsModel(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        self.sql = '''
            select  distinct
                    project_name
                    ,project_scientist
                    ,display_name
            from    BIO_OPTIONS_VW
            where   opt_instance = 1
                    and fram_cam_haul_id = :fram_cam_haul_id
        '''

class BiosModel(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        self.sql = '''
            select 
                    *
            from    BIO_OPTIONS_VW
            where   opt_instance = 1
                    and fram_cam_haul_id = :fram_cam_haul_id
        '''

class FramCamFilterProxyModel(QSortFilterProxyModel):

    currentIndexChanged = Signal()

    def __init__(self, source_model, parent=None):
        super().__init__(parent)
        self._logger = Logger.get_root()
        self.setSourceModel(source_model)

    @Slot(int)
    def setSourceModelIndex(self, i):
        """
        allows us to translate selected row index of proxy model and convert it to the row index of the source
        :param i: int, row index
        :return:
        """
        _proxy_index = self.index(i, 0, QModelIndex())
        _source_index = self.mapToSource(_proxy_index)
        try:
            self.sourceModel().currentIndex = _source_index.row()
        except AttributeError:
            self._logger.error(f"Source model of {self.__class__.__name__} does not have currentIndex property!")

    def filterRoleOnStr(self, role_name: str, value: str):

        try:
            _role_num = self.sourceModel().getRoleByName(role_name)
        except AttributeError:
            self._logger.error(f"Source model of {self.__class__.__name__} does not have getRoleByName method!")
            return

        self.setFilterRole(_role_num)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterFixedString(value)

    def filterRoleOnRegex(self, role_name: str, regex_pattern: str):
        """
        specify name of role and a regex pattern to filter proxy model with
        :param role_name: name of field/role we'd like to filter on
        :param regex_pattern: regular expression pattern that QT likes
        """
        try:
            _role_num = self.sourceModel().getRoleByName(role_name)
        except AttributeError:
            self._logger.error(f"Source model of {self.__class__.__name__} does not have getRoleByName method!")
            return

        self.setFilterRole(_role_num)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterRegularExpression(regex_pattern)




if __name__ == '__main__':
    from py.logger import Logger
    from config import LOCAL_DB_PATH
    from py.qsqlite import QSqlite

    l = Logger().configure()
    sqlite = QSqlite(LOCAL_DB_PATH, 'test')
    sqlite.open_connection()
    model = ProjectsModel(db=sqlite.db)
    model.setBindParam(':fram_cam_haul_id', 10)
    model.loadModel()
    print(model.roleNames())
    print(model.getRoleByName('display_name'))

    # print(model.rowCount())
    # proxy = QSortFilterProxyModel()
    # print(model.roleNames())
    # proxy.setSourceModel(model)
    # proxy.setFilterRole(2)
    # proxy.setFilterFixedString('LST')
    # print(model._data)
    # print(proxy.rowCount())




