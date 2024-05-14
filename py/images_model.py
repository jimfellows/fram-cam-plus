

# standard imports
import os
from pathlib import Path
import re
import shutil
import json
from datetime import datetime

# local imports
from py.logger import Logger
from py.utils import Utils
from py.qt_models import FramCamSqlListModel

# 3rd party imports
from PySide6.QtCore import (
    Slot,
    Property,
    Signal,
)

from PySide6.QtSql import QSqlTableModel


class ImagesModel(FramCamSqlListModel):

    currentImageChanged = Signal()
    currentImageValChanged = Signal(str, "QVariant", arguments=['role_name', 'value'])
    curImageNotesChanged = Signal()  # use me to update backup status (notes change --> need to repush)


    def __init__(self, db):
        super().__init__(db)
        self._logger = Logger.get_root()
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

        self._cur_image = None
        self._cur_image_file_name = None
        self._is_cur_image_backed_up = None
        self._cur_image_notes = None

        # anytime notes change on image, flag image for re-backup
        self.curImageNotesChanged.connect(self._unbackup_image)
        super().selectedIndexChanged.connect(self._set_cur_image)

    def _set_cur_image(self):
        self._cur_image = self.getItem(self._selected_index)
        self.currentImageChanged.emit()

    @Property("QVariant", notify=currentImageChanged)
    def curImgId(self):
        return self.getData(self._selected_index, 'image_id')

    @Property("QVariant", notify=currentImageChanged)
    def curImgFilePath(self):
        return self.getData(self._selected_index, 'full_path') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgFileName(self):
        return self.getData(self._selected_index, 'file_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgNo(self):
        _fname = self.getData(self._selected_index, 'file_name') or ''
        try:
            return re.search('img\d+', _fname).group()
        except AttributeError:
            return None

    @Property("QVariant", notify=currentImageChanged)
    def curImgHaulNum(self):
        return self.getData(self._selected_index, 'haul_number') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgBioLabel(self):
        return self.getData(self._selected_index, 'bio_label') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgProject(self):
        return self.getData(self._selected_index, 'project_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgCatch(self):
        return self.getData(self._selected_index, 'catch_display_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgCommonName(self):
        return self.getData(self._selected_index, 'common_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgSciName(self):
        return self.getData(self._selected_index, 'scientific_name') or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgCaptureDt(self):
        return self.getData(self._selected_index, 'captured_dt') or ''

    def _set_cur_value(self, role_name, value):
        if not self.curImgId:
            self._logger.warning(f"Unable to set {role_name} = {value}, curImgId not set.")
            return

        if self._selected_index == -1:
            self._logger.warning(f"Current Images index not set, unable to set {role_name} = {value}")
            return

        self._logger.debug(f"SETTING {role_name}={value} for image {self.curImgId}")
        self.setData(self._selected_index, value, role_name)
        self._logger.error(f"Our imageid = {self.curImgId}")
        for _i in range(self._table_model.rowCount()):  # todo: is this iteration the best way to do this?
            if self._table_model.record(_i).value('image_id') == self.curImgId:
                print(f"UPDATING RECORD with image id: {self.curImgId}")
                _r = self._table_model.record(_i)
                _r.setValue(self._table_model.fieldIndex(role_name.upper()), value)
                self._table_model.setRecord(_i, _r)
                self._table_model.submitAll()

        self.currentImageValChanged.emit(role_name.lower(), value)  # TODO: emit kv pair?

    @Property("QVariant", notify=currentImageChanged)
    def curImgNotes(self):
        return self.getData(self._selected_index, 'notes') or ''

    @curImgNotes.setter
    def curImgNotes(self, new_notes):
        _cur_notes = self.getData(self._selected_index, 'notes')
        if _cur_notes != new_notes:
            self._set_cur_value('notes', new_notes)
            self.curImageNotesChanged.emit()

    @Property("QVariant", notify=currentImageChanged)
    def curImgBackupPath(self):
        return self.getData(self._selected_index, 'backup_path') or ''

    @curImgBackupPath.setter
    def curImgBackupPath(self, new_path):
        self._set_cur_value('backup_path', new_path)

    @Property(int, notify=currentImageChanged)
    def isImgBackedUp(self):
        return self.getData(self._selected_index, 'is_backed_up')

    @isImgBackedUp.setter
    def isImgBackedUp(self, new_status):
        if self.isImgBackedUp != new_status:
            self._set_cur_value('is_backed_up', new_status)

    def _unbackup_image(self):
        self.isImgBackedUp = 0

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

            self.setData(_model_row, sync_path, 'backup_path')
            self.setData(_model_row, 1, 'is_backed_up')

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
            if _col_ix and v is not None:  # allow default values to happen
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

        self._logger.debug(f"image_id {image_id} loaded to list model at index {self._selected_index}")
        self.selectIndexInUI.emit(index)  # selects new row in proxy / listview

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
            self.selectIndexInUI.emit(row_ix)  # select the new image that is now in this index after deletion
            self.currentImageChanged.emit()  # image changes but index stays the same, so calling this manually