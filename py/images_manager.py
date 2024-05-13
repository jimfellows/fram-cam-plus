

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
from py.config import IMAGES_DIR
from py.qt_models import FramCamFilterProxyModel, FramCamSqlListModel

# 3rd party imports
from PySide6.QtCore import (
    QObject,
    Slot,
    Property,
    Signal,
    Qt,
    QSortFilterProxyModel,
    QModelIndex,
    QThread,
    QRegularExpression
)

from PySide6.QtSql import QSqlTableModel


import pyzbar.pyzbar
# import tensorflow as tf
from PIL import Image
import piexif



class ImagesModel(FramCamSqlListModel):

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
        return self.getData(self._selected_index, 'scientific_name')  or ''

    @Property("QVariant", notify=currentImageChanged)
    def curImgCaptureDt(self):
        return self.getData(self._selected_index, 'captured_dt')  or ''

    def _set_cur_value(self, role_name, value):

        if not self.curImgId:
            self._logger.warning(f"Unable to set {role_name} = {value}, curImgId not set.")
            return

        if self._selected_index == -1:
            self._logger.warning(f"Current Images index not set, unable to set {role_name} = {value}")
            return

        self._logger.debug(f"SETTING {role_name}={value}")
        for _i in range(self._table_model.rowCount()):  # todo: is this iteration the best way to do this?
            if self._table_model.record(_i).value('image_id') == self.curImgId:
                _r = self._table_model.record(_i)
                _r.setValue(self._table_model.fieldIndex(role_name.upper()), value)
                self._table_model.setRecord(_i, _r)
                self._table_model.submitAll()

        self.setRoleData(self._selected_index, role_name.lower(), value)
        self.currentImageValChanged.emit(role_name.lower(), value)  # TODO: emit kv pair?

    @Property("QVariant", notify=currentImageChanged)
    def curImgNotes(self):
        return self.getData(self._selected_index, 'notes') or ''

    @curImgNotes.setter
    def curImgNotes(self, new_notes):
        self._set_cur_value('notes', new_notes)
        self.curImageNotesChanged.emit()

    @Property("QVariant", notify=currentImageChanged)
    def curImgBackupPath(self):
        return self.getData(self._selected_index, 'backup_path') or ''

    @curImgBackupPath.setter
    def curImgBackupPath(self, new_path):
        self._set_cur_value('backup_path', new_path)

    @Property(bool, notify=currentImageChanged)
    def isImgBackedUp(self):
        return self.getData(self._selected_index, 'is_backed_up') == 1

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




class CopyFilesWorker(QObject):
    """
    worker class to copy image files on threaded process
    """
    copyStarted = Signal(int, arguments=['no_of_files'])  # tell progress bar how many files we are copying
    fileCopied = Signal(str, str, bool, arguments=['path', 'new_path', 'success'])  # for each file, emit once done
    copyEnded = Signal(int, int, arguments=['files_copied', 'files_failed'])  # emit when complete, to kill thread
    badDestinationPath = Signal(str, arguments=['path'])

    def __init__(self):
        super().__init__()
        self._logger = Logger.get_root()
        self._files_to_copy = []
        self._destination_folder = None
        self._images_subdir = None
        self._is_running = False

    @staticmethod
    def tag_jpg_w_json_exif(img_path, tag_dict):
        """
        convert python dict to json, then insert into an image's UserComments exif tag
        :param img_path: str, full path to image
        :param tag_dict: dict
        """
        try:
            img = Image.open(img_path)
            exif_dict = piexif.load(img.info["exif"])
            exif_dict['Exif'] = {piexif.ExifIFD.UserComment: json.dumps(tag_dict).encode('utf-8')}
            exif_bytes = piexif.dump(exif_dict)
            img.save(img_path, "jpeg", exif=exif_bytes)
        except Exception as e:
            pass

    @property
    def destination_folder(self) -> str:
        """
        set path before running
        """
        return self._destination_folder

    @destination_folder.setter
    def destination_folder(self, folder_path: str):
        self._destination_folder = folder_path
        self._images_subdir = os.path.join(self._destination_folder, 'images')

    @property
    def files_to_copy(self) -> list[str]:
        """
        set before running, list of full paths to files we want to send to destination
        """
        return self._files_to_copy

    @files_to_copy.setter
    def files_to_copy(self, file_paths: list[str]):
        self._files_to_copy = file_paths

    def run(self):
        """
        main call of thread, must set files_to_copy and destination_folder props first
        emit start, copy, and end signals
        """
        _successes = 0
        _fails = 0
        if not self._destination_folder or not os.path.exists(self._destination_folder):
            self._logger.error(f"Unable to find target folder to copy files to: {self._destination_folder}")
            self.copyEnded.emit(_successes, _fails)
            self._logger.info(f"File copy completed: successes = {_successes}, failures = {_fails}")
            self.badDestinationPath.emit(self._destination_folder or '')
            return

        os.makedirs(self._images_subdir, exist_ok=True)
        self._logger.info(f"Copying {len(self._files_to_copy)} to {self._images_subdir}")
        self.copyStarted.emit(len(self._files_to_copy))
        self._is_running = True

        for f in self._files_to_copy:
            try:
                _new_path = os.path.join(self._images_subdir, os.path.basename(f))
                shutil.copyfile(f, _new_path)
                self._logger.info(f"File copied: {f} --> {_new_path}")
                _successes += 1
                self.fileCopied.emit(f, _new_path, True)
            except Exception as e:
                self._logger.error(f"Error while copying {f}: {e}")
                _fails += 1
                self.fileCopied.emit(f, '', False)

        self._is_running = False
        self.copyEnded.emit(_successes, _fails)
        self._logger.info(f"File copy completed: successes = {_successes}, failures = {_fails}")


class ImageManager(QObject):
    """
    class to handle image file related processes
    """
    imagesViewChanged = Signal()
    imagesModelChanged = Signal()
    copyStarted = Signal(int, arguments=['no_of_files'])
    fileCopied = Signal(str, str, bool, arguments=['path', 'new_path', 'success'])
    copyEnded = Signal(int, int, arguments=['files_copied', 'files_failed'])
    badDestinationPath = Signal(str, arguments=['path'])

    def __init__(self, db, app=None, parent=None):
        super().__init__(parent)
        self._app = app
        self._db = db
        self._logger = Logger.get_root()

        # our models
        self._images_model = ImagesModel(self._db)  # stores underlying images
        self._images_proxy = FramCamFilterProxyModel(self._images_model)  # allows filtering by haul/catch/proj/bio

        # filter proxy model as any of the data selections change
        self._app.data_selector.curHaulChanged.connect(self._filter_images_model)
        self._app.data_selector.curCatchChanged.connect(self._filter_images_model)
        self._app.data_selector.curProjectChanged.connect(self._filter_images_model)
        self._app.data_selector.curBioChanged.connect(self._filter_images_model)

        # on init, get everything we have, then filter if menu is set from state
        self._load_images_model()
        self._filter_images_model()

        # receive capture signal, which appends new image to model
        self._app.cam_controls.imageCapture.imageSaved.connect(lambda ix, path: self._on_image_captured(path))  # dont need index from signal

        # # threading stuff to copy image files
        self._file_copy_thread = None
        self._file_copy_worker = None

    def get_exif_dict(self, file_path):
        _ix = self._images_model.getRowIndexByValue('full_path', file_path)
        return self._images_model.getItem(_ix)

    @Slot()
    def copyCurImageToWheelhouse(self):
        """
        wrap our threaded method, but only send off our currently selected image
        """
        self._copy_images_to_wheelhouse([self._images_model.curImgFilePath])

    @Slot("QVariantList")
    def copyImagesToWheelhouse(self, images: list[any]):
        self._copy_images_to_wheelhouse(images)

    def _copy_images_to_wheelhouse(self, images: list[any]):
        """
        create thread and worker each time we run.
        could use a runnable if its too many, but should be fine
        :param images: list of full paths to the images we want to copy to WH dest
        """
        # threading stuff to copy image files
        self._copy_files_thread = QThread()
        self._copy_files_worker = CopyFilesWorker()
        self._copy_files_worker.moveToThread(self._copy_files_thread)
        self._copy_files_thread.started.connect(self._copy_files_worker.run)

        # connecting QML directly to the worker signals causes crash, so passing via signals here
        self._copy_files_worker.copyStarted.connect(self.copyStarted.emit)
        self._copy_files_worker.fileCopied.connect(self.fileCopied.emit)
        self._copy_files_worker.fileCopied.connect(self._images_model.setImageSyncPath)
        self._copy_files_worker.copyEnded.connect(self.copyEnded.emit)
        self._copy_files_worker.copyEnded.connect(self._copy_files_thread.quit)
        self._copy_files_worker.badDestinationPath.connect(self.badDestinationPath)

        # set props we need to run, then run
        self._copy_files_worker.destination_folder = self._app.settings.curWheelhouseDataDir
        self._copy_files_worker.files_to_copy = images
        self._copy_files_thread.start()

    def _filter_images_model(self):
        """
        use currently selected vals in data selector to filter our images. Means
        that as the user selects different/more specific values, the thumbnails visible will change in the UI
        """
        # the underlying view for data selector converts nulls to "NULL" in filter str, hence the OR NULL
        _haul = self._app.data_selector.cur_haul_num or 'NULL'
        _catch = self._app.data_selector.cur_catch_display or 'NULL'
        _proj = self._app.data_selector.cur_project_name or 'NULL'
        _bio = self._app.data_selector.cur_bio_label or 'NULL'

        if not self._app.data_selector.cur_catch_display:
            search_str = f'"haul_number":"{_haul}"*'
        elif not self._app.data_selector.cur_project_name:
            search_str = f'"haul_number":"{_haul}","catch_display_name":"{_catch}"*'
        elif not self._app.data_selector.cur_bio_label:
            search_str = f'"haul_number":"{_haul}","catch_display_name":"{_catch}","project_name":"{_proj}"*'
        else:
            search_str = f'"haul_number":"{_haul}","catch_display_name":"{_catch}","project_name":"{_proj}","bio_label":"{_bio}"'

        search_str = QRegularExpression.wildcardToRegularExpression(search_str)  # convert our "*" chars to regex
        self._logger.debug(f"Filtering images based on filter string: {search_str}")
        self._images_proxy.filterRoleOnRegex('image_filter_str', search_str)
        self._logger.error(f"Filtering images on {search_str}, proxy index = {self._images_proxy.proxyIndex}")
        self._logger.error(f"Filtering images on {search_str}, model index = {self._images_model.selectedIndex}")

    @Property(QObject, constant=True)
    def imagesModel(self) -> ImagesModel:
        return self._images_model

    @Property(QObject, constant=True)
    def imagesProxy(self) -> FramCamFilterProxyModel:
        return self._images_proxy

    def _load_images_model(self):
        """
        using selected vals, load the images associated.
        each image taken is appended, and filtering based on user data selection is handled by proxy
        """
        self._images_model.clearBindParams()
        # TODO: do i need to handle null vals?
        self._images_model.setBindParam(':haul_number', self._app.data_selector.cur_haul_num)
        self._images_model.setBindParam(':catch_display', self._app.data_selector.cur_catch_display)
        self._images_model.setBindParam(':project_name', self._app.data_selector.cur_project_name)
        self._images_model.setBindParam(':bio_label', self._app.data_selector.cur_bio_label)
        self._logger.debug(f"Loading images model for params {self._images_model._bind_params}")
        self._images_model.loadModel()

    def _on_image_captured(self, image_path: str):
        """
        when signal is received from cam_controls that an image was taken, add to model
        :param image_path: full path to image location, sent over via capture signal
        """
        self._images_model.append_new_image(
            image_path,
            self._app.data_selector.cur_selection_data
        )

