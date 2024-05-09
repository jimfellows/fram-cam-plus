
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

    currentIndexChanged = Signal(int, arguments=['newIndex'])
    indexSetSilently = Signal(int, arguments=['newIndex'])
    selectIndexInUI = Signal(int, arguments=['index'])
    #selectRow = Signal(int, argument=['rowToSelect'])

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

    def setData(self, index, value, role=Qt.DisplayRole):
        """
        re-implementation of virtual function to allow editable model
        set role data to value at specific index in _data list
        """
        if not index.isValid():
            return
        try:
            self._data[index.row()][self.roleNames()[role].decode('utf-8')] = value
            self.dataChanged.emit(index, index)  # emits index twice (we're only editing a single item)
        except Exception as e:
            self._logger.error(f"Error in {self.__class__.__name__}.setData: {e}")

    def setRoleData(self, row, role_name, value):
        """
        wrapper for set data to allow developer to just specify the row num, field/role name, and value to set
        """
        _role_int = self.getRoleByName(role_name)
        _ix = QModelIndex(self.index(row, 0))  # assumes 2-d data structure, so col = 0, is this right?
        self.setData(_ix, value, role=_role_int)

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

    @Property(int, notify=currentIndexChanged)
    def currentIndex(self):
        return self._current_index

    @currentIndex.setter
    def currentIndex(self, new_index):
        if self._current_index != new_index:
            self._current_index = new_index
            self.currentIndexChanged.emit(new_index)
            self._logger.debug(f"{self.__class__.__name__} current index set from {self._current_index} --> {new_index}")

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
        return self.getData(self._current_index, prop_name)

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

    def setIndexSilently(self, new_index):
        """
        idea here is to prep the model by setting the private value first, then emitting the
        new index to the view for selection.  Depends on the fact that the currentIndex setter only
        emits currentIndexChanged if value is different, and b/c here were pre-setting _current_index,
        that wont happen (TODO: could this chain of events be interupted?)
        :param new_index: int
        """
        self._current_index = new_index
        self.indexSetSilently.emit(new_index)
        self._logger.debug(f"Index of {self.__class__.__name__} set to {new_index} silently.")


class HaulsModel(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        self.sql = 'select distinct haul_number, backdeck_haul_id from backdeck_bios_vw order by substr(haul_number, -3) desc'

class CatchesModel(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        self.sql = '''
            select  distinct
                    catch_display_name
                    ,haul_number
                    ,common_name
                    ,scientific_name
                    ,taxonomy_id
                    ,backdeck_catch_id
                    
            from    backdeck_bios_vw
            where   haul_number = :haul_number
        '''


class ProjectsModel(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        # get distinct list of projects, display names, and filter str, project must be not null
        self.sql = '''
            select  distinct
                    project_name
                    ,catch_display_name
                    ,project_scientist
                    ,bio_filter_str
            from    backdeck_bios_vw
            where   project_name is not null
                    and haul_number = :haul_number
        '''

class BiosModel(FramCamSqlListModel):
    def __init__(self, db):
        super().__init__(db)
        self.sql = '''
            select 
                    *
            from    backdeck_bios_vw
            where   haul_number = :haul_number
                    and bio_label is not null
        '''

class FramCamFilterProxyModel(QSortFilterProxyModel):

    proxyIndexChanged = Signal(int, arguments=['new_proxy_index'])
    selectProxyIndexInUI = Signal(int, arguments=['proxy_index'])  # use me to simulate a click of proxy model item
    indexSetSilently = Signal(int, arguments=['newIndex'])

    def __init__(self, source_model, parent=None, name=None):
        super().__init__(parent)
        self._logger = Logger.get_root()
        self._proxy_index = -1
        self.setSourceModel(source_model)
        self._name = name if name else self.__class__.__name__

    def setProxyIndexSilently(self, new_index):
        self._proxy_index = new_index

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
    def getSourceRowFromProxy(self, proxy_row: int):
        _proxy_index = self.index(proxy_row, 0, QModelIndex())
        _source_index = self.mapToSource(_proxy_index)
        self._logger.debug(f"Converted {self._name} proxy row {proxy_row} to source row {_source_index.row()}")
        return _source_index.row()

    @Slot(int, result=int)
    def getProxyRowFromSource(self, source_row: int):
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
        self._current_index = i
        _proxy_index = self.index(i, 0, QModelIndex())
        _source_index = self.mapToSource(_proxy_index)
        try:
            self.sourceModel().currentIndex = _source_index.row()
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


class ImagesModel(FramCamSqlListModel):
    sendIndexToProxy = Signal(int, arguments=['new_index'])  # TODO: move me into framcamsqllistmodel, rename to sendIndexToView???
    currentImageChanged = Signal()
    currentImageValChanged = Signal(str, "QVariant", arguments=['role_name', 'value'])
    curImageNotesChanged = Signal()  # use me to update backup status (notes change --> need to repush)


    def __init__(self, db):
        super().__init__(db)
        self.sql = '''
            select      *
            from        IMAGES_VW
            where       coalesce(nullif(:haul_number, ''), haul_number, '1') = coalesce(haul_number, '1')
                        and coalesce(nullif(:catch_display_name, ''), catch_display_name, '1') = coalesce(catch_display_name, '1')
                        and coalesce(nullif(:project_name, ''), project_name, '1') = coalesce(project_name, '1')
                        and coalesce(nullif(:bio_label, ''), bio_label, '1') = coalesce(bio_label, '1')
                        and coalesce(:image_id, image_id) = image_id
            order by    image_id desc
        '''

        self._table_model = QSqlTableModel(db=self._db)
        self._table_model.setTable('IMAGES')
        self._table_model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self._table_model.select()
        self._table_proxy = QSortFilterProxyModel()

        self._cur_image = None
        self._cur_image_file_name = None
        self._is_cur_image_backed_up = None

        # anytime notes change on image, flag image for re-backup
        self.curImageNotesChanged.connect(lambda k='is_backed_up', v=0: self._set_cur_value(k, v))

        super().currentIndexChanged.connect(self._set_cur_image)

    def _set_cur_image(self):
        self._cur_image = self.getItem(self._current_index)
        self.currentImageChanged.emit()

    @Property("QVariant", notify=currentImageChanged)
    def curImgId(self):
        return self.getData(self._current_index, 'image_id')

    @Property("QVariant", notify=currentImageChanged)
    def curImgFilePath(self):
        return self.getData(self._current_index, 'full_path') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgFileName(self):
        return self.getData(self._current_index, 'file_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgNo(self):
        _fname = self.getData(self._current_index, 'file_name') or ''
        try:
            return re.search('img\d+', _fname).group()
        except AttributeError:
            return None

    @Property("QVariant", notify=currentImageChanged)
    def curImgHaulNum(self):
        return self.getData(self._current_index, 'haul_number') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgBioLabel(self):
        return self.getData(self._current_index, 'bio_label') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgProject(self):
        return self.getData(self._current_index, 'project_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgCatch(self):
        return self.getData(self._current_index, 'catch_display_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgCommonName(self):
        return self.getData(self._current_index, 'common_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgSciName(self):
        return self.getData(self._current_index, 'scientific_name')  or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgCaptureDt(self):
        return self.getData(self._current_index, 'captured_dt')  or ''

    def _set_cur_value(self, role_name, value):

        if not self.curImgId:
            self._logger.warning(f"Unable to set {role_name} = {value}, curImgId not set.")
            return

        if self._current_index == -1:
            self._logger.warning(f"Current Images index not set, unable to set {role_name} = {value}")
            return

        self._logger.debug(f"SETTING {role_name}={value}")
        for _i in range(self._table_model.rowCount()):  # todo: is this iteration the best way to do this?
            if self._table_model.record(_i).value('image_id') == self.curImgId:
                _r = self._table_model.record(_i)
                _r.setValue(self._table_model.fieldIndex(role_name.upper()), value)
                self._table_model.setRecord(_i, _r)
                self._table_model.submitAll()

        self.setRoleData(self._current_index, role_name.lower(), value)
        self.currentImageValChanged.emit(role_name.lower(), value)  # TODO: emit kv pair?

    @Property("QVariant", notify=currentImageChanged)
    def curImgNotes(self):
        return self.getData(self._current_index, 'notes') or ''

    @curImgNotes.setter
    def curImgNotes(self, new_notes):
        self._set_cur_value('notes', new_notes)
        self.curImageNotesChanged.emit()

    @Property("QVariant", notify=currentImageChanged)
    def curImgBackupPath(self):
        return self.getData(self._current_index, 'backup_path') or ''

    @curImgBackupPath.setter
    def curImgBackupPath(self, new_path):
        self._set_cur_value('backup_path', new_path)

    @Property(bool, notify=currentImageChanged)
    def isImgBackedUp(self):
        return self.getData(self._current_index, 'is_backed_up') == 1

    def setImageSyncPath(self, local_path, sync_path, is_successful):
        """
        allows us to set value for images that arent the "current" selection
        """
        if is_successful:
            _model_row = self.getRowIndexByValue('full_path', local_path)
            _img_id = self.getData(_model_row, 'image_id')
            for _i in range(self._table_model.rowCount()):
                if self._table_model.record(_i).value('image_id') == _img_id:
                    _r = self._table_model.record(_i)
                    _r.setValue(self._table_model.fieldIndex('BACKUP_PATH'), sync_path)
                    _r.setValue(self._table_model.fieldIndex('IS_BACKED_UP'), 1)
                    self._table_model.setRecord(_i, _r)
                    self._table_model.submitAll()

            self.setRoleData(_model_row, 'backup_path', sync_path)
            self.currentImageChanged.emit()

    def insert_to_db(self, image_path: str, image_data: dict):
        """
        method to create a new rec in IMAGES table and return newly generated IMAGE_ID pkey value
        :param image_path: full str path to image
        :param haul_id: int, pkey for HAULS table
        :param catch_id: int, pkey for CATCH table
        :param specimen_id: int, pkey for SPECIMEN table
        :return: int, pkey for new IMAGES table rec
        """
        if not os.path.exists(image_path):
            self._logger.error(f"Unable to add file to IMAGES table: newly image not found at {image_path}")
            return

        self._logger.info(f"Creating new image here: {image_path}")

        # create the shell record, then set values
        _img = self._table_model.record()
        _img.setValue(self._table_model.fieldIndex('FILE_PATH'), os.path.dirname(image_path))
        _img.setValue(self._table_model.fieldIndex('FILE_NAME'), os.path.basename(image_path))
        self._logger.debug(f"Creating image with the following data: {image_data}")
        for k, v in image_data.items():
            _col_ix = self._table_model.fieldIndex(str(k).upper())
            if _col_ix:
                try:
                    _img.setValue(k, v)
                except Exception as e:
                    self._logger.error(f"Unable to set {k} = {v} in IMAGES table model")
                    continue
            else:
                self._logger.warning(f"Column {str(k).upper()} not found in IMAGES table model.")

        _img.setValue(self._table_model.fieldIndex('CAPTURED_DT'), datetime.now().isoformat(timespec="seconds"))

        # do the insert, manually commit, then get newly created ID back out
        self._table_model.insertRecord(-1, _img)
        self._table_model.submitAll()
        _img_id = self._table_model.query().lastInsertId()
        self._logger.info(f"New IMAGES record created with IMAGE_ID = {_img_id}")
        return _img_id

    def load_image_from_view(self, image_id, index=0):
        """
        following insert to IMAGES table, use image_id to get denormalized version from view
        and put it into view model / list view
        :param image_id:
        :return:
        TODO: check if image_id row already exists, if so rip out and replace
        """
        self._logger.debug(f"Loading image_id {image_id} to list model")
        self._query.bindValue(':image_id', image_id)
        self._query.exec()
        self._query_model.setQuery(self._query)
        for i in range(self._query_model.rowCount()):
            self.appendRow(Utils.qrec_to_dict(self._query_model.record(i)), index=index)

        self._logger.debug(f"image_id {image_id} loaded to list model at index {self._current_index}")
        self.sendIndexToProxy.emit(index)  # selects new row in proxy / listview

    def append_new_image(self, image_path: str, image_data: dict):
        """
        In the event that the camera has saved an image to disk, this function performs what needs
        to happen immediately after with respect to the  list model
        1.) insert to database
        2.) retrieve denormalized rec from view
        3.) append to array aka listmodel
        :param image_id: int, db pkey for IMAGES table
        """
        if not os.path.exists(image_path):
            self._logger.error(f"Unable to add file to list model: newly image not found at {image_path}")
            return

        self._logger.debug(f"Inserting record to IMAGES for: {image_path}")
        _img_id = self.insert_to_db(image_path, image_data)
        self.load_image_from_view(_img_id)

    @Slot(int)
    def removeImage(self, row_ix):
        # TODO: better way to delete from db?
        _image_id = self.getData(row_ix, 'image_id')
        _file_path = self.getData(row_ix, 'full_path')
        if os.path.exists(_file_path):
            os.remove(_file_path)
        _table_ix = -1
        for _i in range(self._table_model.rowCount()):
            if self._table_model.record(_i).value('image_id') == _image_id:
                self._table_model.removeRow(_i)
                self._table_model.submitAll()
                break

        self.removeItem(row_ix)
        if self.rowCount() != 0:
            self.sendIndexToProxy.emit(row_ix)  # select the new image that is now in this index after deletion
            self.currentImageChanged.emit()  # image changes but index stays the same, so calling this manually


if __name__ == '__main__':
    from py.logger import Logger
    from py.config import LOCAL_DB_PATH
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




