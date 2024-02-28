
# standard imports
import os
from pathlib import Path
import re

# local imports
from py.logger import Logger
from py.utils import Utils
from config import IMAGES_DIR

# 3rd party imports
from PySide6.QtCore import (
    QObject,
    Slot,
    Property,
    Signal,
    Qt,
    QAbstractListModel,
    QModelIndex
)
from PySide6.QtMultimedia import (
    QAudioInput,
    QCamera,
    QCameraDevice,
    QImageCapture,
    QMediaCaptureSession,
    QMediaDevices,
    QMediaMetaData,
    QVideoSink,
    QMediaRecorder
)

from PySide6.QtSql import QSqlTableModel, QSqlQueryModel, QSqlQuery, QSqlRecord


class ImagesListModel(QAbstractListModel):

    currentIndexChanged = Signal(int, arguments=['new_index'])

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._logger = Logger.get_root()
        self._db = db
        self._table_model = QSqlTableModel(db=self._db)
        self._table_model.setTable('IMAGES')
        self._table_model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self._table_model.select()  # load me, should this be in INIT, and do we need to do it?
        self._query_model = QSqlQueryModel()
        self._query = QSqlQuery(self._db)
        self._sql = '''
            select      *
            from        IMAGES_VW
            where       coalesce(:haul_id, haul_id) = haul_id
                        and coalesce(:catch_id, catch_id) = catch_id
                        and coalesce(:project_name, project_name) = project_name
                        and coalesce(:bio_label, bio_label) = bio_label
                        and coalesce(:image_id, image_id) = image_id
            order by    image_id desc
        '''
        self._query.prepare(self._sql)
        self._records = []
        self._current_index = -1

    @Property(int, notify=currentIndexChanged)
    def currentIndex(self):
        return self._current_index

    @currentIndex.setter
    def currentIndex(self, new_index):
        if self._current_index != new_index:
            self._current_index = new_index
            self.currentIndexChanged.emit(new_index)

    def populate(self, haul_id=None, catch_id=None, project_name=None, bio_label=None):
        """
        custom query to load up denormalized image results.
        Haul id is required (for now). Other args, if null, will not filter to data results.
        TODO: should we query on specimen id and species_sampling_project_id instead of strings?
        :param haul_id: int, HAULS pkey
        :param catch_id: int, CATCH pkey
        :param project_name: str, name of project for sampling plan (SPECIES_SAMPLING_PLAN_LU.PLAN_NAME field)
        :param bio_label: str, name of bio label (SPECIMEN.ALPHA_VALUE/SPECIMEN.NUMERIC_VALUE)
        """
        self._records = []
        self._query.bindValue(':haul_id', haul_id)
        self._query.bindValue(':catch_id', catch_id)
        self._query.bindValue(':plan_name', project_name)
        self._query.bindValue(':bio_label', bio_label)
        self._query.exec()
        self._query_model.setQuery(self._query)
        self._logger.info(f"Loading {self._query_model.rowCount()} records to images model...")
        for i in range(self._query_model.rowCount()):
            self._records.append(self.record_to_dict(self._query_model.record(i)))

    def insert_to_db(self, image_path, haul_id=None, catch_id=None, specimen_id=None):
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
        _img.setValue(self._table_model.fieldIndex('HAUL_ID'), haul_id)
        _img.setValue(self._table_model.fieldIndex('CATCH_ID'), catch_id)
        _img.setValue(self._table_model.fieldIndex('SPECIMEN_ID'), specimen_id)

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
        self._logger.info(f"Loading image_id {image_id} to list model")
        self._query.bindValue(':image_id', image_id)
        self._query.exec()
        self._query_model.setQuery(self._query)
        self.beginInsertRows(QModelIndex(), index, index)  # tells model/ui about updates
        for i in range(self._query_model.rowCount()):
            self._records.insert(index, self.record_to_dict(self._query_model.record(i)))

        self.currentIndex = index
        self.endInsertRows()  # tells model/ui we're done
        self._logger.info(f"image_id {image_id} loaded to list model at index {self._current_index}")

    @staticmethod
    def record_to_dict(rec: QSqlRecord):
        """
        covert a QSQLrecord instances to a python dict.  Use me to append records to self._records
        :param rec: QSqlRecord
        :return: dictionary
        """
        _keys = [rec.fieldName(k).lower() for k in range(rec.count())]
        _vals = [rec.value(k) for k in _keys]
        return dict(zip(_keys, _vals))

    def append_new_image(self, image_path, haul_id=None, catch_id=None, specimen_id=None):
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

        self._logger.info(f"Inserting record to IMAGES for: {image_path}")
        _img_id = self.insert_to_db(image_path, haul_id, catch_id, specimen_id)
        self.load_image_from_view(_img_id)

    def remove_from_db(self, image_id):
        row = 0
        for ix in range(self._table_model.rowCount()):
            if self._table_model.record(ix).value('IMAGE_ID') == image_id:
                break
            else:
                row += 1

        self._table_model.removeRow(row)

    def remove_from_model(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)
        del self._records[index]
        self.endRemoveRows()

    @Slot(int)
    def remove_image(self, row_index):
        pass



    def rowCount(self, index=0):
        return len(self._records)

    def columnCount(self, index):
        return self._query_model.record().count()

    def data(self, index, role: int):
        if not index.isValid():
            return
        try:
            # return self._records[index.row()].value(self.roleNames()[role].decode('utf-8'))  # before when we were using qsqlrecords
            return self._records[index.row()][self.roleNames()[role].decode('utf-8')]
        except Exception as e:
            self._logger.error(f"FAILED: {e}")
            return None

    def get_value(self, i, key):
        return self._records[i].value(key)

    def roleNames(self):
        _rec = self._query_model.record()
        _fields = [_rec.field(f).name().lower() for f in range(0, _rec.count())]
        return {Qt.DisplayRole + i: r.encode("utf-8") for i, r in enumerate(_fields)}


class CameraManager(QObject):

    unusedSignal = Signal()
    images_view_changed = Signal()
    images_model_changed = Signal()
    activeCameraChanged = Signal()


    def __init__(self, db, app=None):
        super().__init__()
        self._app = app
        self._db = db
        self._logger = Logger.get_root()
        self._devices = QMediaDevices()
        self._camera = QCamera(QMediaDevices.defaultVideoInput())
        self._image_capture = QImageCapture()
        self._capture_session = QMediaCaptureSession()
        self._capture_session.setCamera(self._camera)
        self._capture_session.setImageCapture(self._image_capture)
        self._is_capturing = False
        # self.start_camera()
        self._is_camera_running = None
        self._images_model = ImagesListModel(self._db)
        self._load_images_model()
        self._image_capture.imageSaved.connect(lambda ix, path: self._on_image_saved(path))  # image save is async, so hooking to signal
        print(self._camera.supportedFeatures())

    @Property(str, notify=activeCameraChanged)
    def active_camera_name(self):
        return self._camera.cameraDevice().description()

    @Slot()
    def toggle_camera(self):
        if not self._devices.videoInputs() or not self._camera:
            self._logger.warning(f"Unable to get next device, none available")
            return

        if len(self._devices.videoInputs()) == 1:
            self._logger.info(f"Only one video input device available")
            return

        try:
            cur_index = [d.description() for d in self._devices.videoInputs()].index(self._camera.cameraDevice().description())
            self.camera = QCamera(self._devices.videoInputs()[cur_index+1])

        except ValueError as e:
            self._logger.error(f"Error occurred while trying to get toggle camera device: {e}")
            return

        except IndexError:
            self._logger.info("Setting camera to default device")
            self.camera = QCamera(self._devices.videoInputs()[0])


    @Property(QObject)
    def images_model(self):
        return self._images_model

    def _load_images_model(self):
        self._images_model.populate(
            haul_id=self._app.state.cur_haul_id,
            catch_id=self._app.state.cur_catch_id,
            project_name=self._app.state.cur_project,
            bio_label=self._app.state.cur_bio_label
        )

    def _on_image_saved(self, image_path):
        self.images_model.append_new_image(
            image_path,
            haul_id=self._app.state.cur_haul_id,
            catch_id=self._app.state.cur_catch_id,
            specimen_id=self._app.state.cur_specimen_id
        )

    @Property(QObject, notify=images_model_changed)
    def images_model(self):
        return self._images_model

    @Property(QObject)
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, new_camera):
        if self._camera.cameraDevice().description() != new_camera.cameraDevice().description():
            self._camera = new_camera
            self._capture_session.setCamera(self._camera)
            self._camera.start()
            self.activeCameraChanged.emit()
            self._view_camera_features()

    @Property("QVariant", notify=activeCameraChanged)
    def isFlashSupported(self):
        return self._camera.isFlashModeSupported(QCamera.FlashOn)

    @Property("QVariant", notify=activeCameraChanged)
    def isTorchSupported(self):
        return self._camera.isTorchModeSupported(QCamera.TorchOn)

    def _view_camera_features(self):
        print(QCamera.FlashOn)
        self._logger.info(f"Is flash on supported? {self._camera.isFlashModeSupported(QCamera.FlashOn)}")

    @Property(QObject)
    def image_capture(self):
        return self._image_capture

    @Slot(QObject)
    def set_video_output(self, output):
        self._capture_session.setVideoOutput(output)

    @Property(QObject)
    def capture_session(self):
        return self._capture_session

    @Slot()
    def start_camera(self):
        self._logger.info(f"Starting camera {self._camera.cameraDevice().description()}")
        self._camera.start()
        # self._is_camera_running = True

    @Slot()
    def stop_camera(self):
        self._camera.stop()
        # self._is_camera_running =

    @Property(bool)
    def is_camera_active(self):
        return self._camera.isActive()

    def get_image_name(self, ext='jpg'):
        """
        build image file name with current settings
        TODO: what if catch/project/bio isnt selected? need these to be null
        :param ext: str, extension specified, default to jpg
        :return: str, name of image file
        """
        haul_number = self._app.state.cur_haul_number if self._app.state.cur_haul_number else ''
        vessel_code = Utils.get_vessel_code_from_haul(haul_number)
        vessel_haul = vessel_code + haul_number[-3:]
        catch_display = Utils.scrub_str_for_file_name(self._app.state.cur_catch_display) if self._app.state.cur_catch_display else ''
        project = Utils.scrub_str_for_file_name(self._app.state.cur_project) if self._app.state.cur_project else ''
        bio_label = self._app.state.cur_bio_label if self._app.state.cur_bio_label else ''
        return f"{vessel_haul}_{catch_display}_{project}_{bio_label}.{ext}"

    def increment_file_path(self, full_path, i=1):
        """
        append _i to the file path, where i is the next available if we have a duplicate file
        :param full_path: full path to file
        :param i: int, starting integer we attempt to append to file
        :return: str, new full path to image with next available i
        """

        path, ext = os.path.splitext(full_path)
        pattern = re.compile(f'_img\\d+{ext}$')
        if not pattern.search(full_path):
            # if filename doesnt have img# at the end, put it there
            full_path = f"{path}_img{i}{ext}"
        else:
            # if path is already incremented, replace increment with current val
            full_path = re.sub(pattern, f'_img{i}{ext}', full_path)

        if not os.path.exists(full_path):
            return full_path
        else:
            i += 1
            return self.increment_file_path(full_path, i)

    @Slot()
    def capture_image_to_file(self):
        """
        async image capture, on success the imageSaved signal is emitted
        https://doc.qt.io/qtforpython-6/PySide6/QtMultimedia/QImageCapture.html#PySide6.QtMultimedia.PySide6.QtMultimedia.QImageCapture.imageSaved
        """
        img_name = self.get_image_name()
        full_path = Path(self.increment_file_path(os.path.join(IMAGES_DIR, img_name))).as_posix()
        img_result = self._image_capture.captureToFile(full_path)
        self._logger.info(f"Capturing image to {full_path}, capture result={img_result}")

    # def create_new_image_record(self, image_path):
    #     self._logger.info(f"Creating new image here: {image_path}")
    #     self._images_
    #
    #
    #     img = self._images_model.record()
    #     img.setValue(self._images_model.fieldIndex('FILE_PATH'), os.path.dirname(image_path))
    #     img.setValue(self._images_model.fieldIndex('FILE_NAME'), os.path.basename(image_path))
    #     img.setValue(self._images_model.fieldIndex('HAUL_ID'), self._app.state.cur_haul_id)
    #     img.setValue(self._images_model.fieldIndex('CATCH_ID'), self._app.state.cur_catch_id)
    #     img.setValue(self._images_model.fieldIndex('SPECIMEN_ID'), self._app.state.cur_specimen_id)
    #     self._images_model.insertRecord(-1, img)
    #     self._images_model.submitAll()
    #     image_id = self._images_model.query().lastInsertId()
    #     self._images_view_model.append_new_image(image_id)
    #     self.images_model_changed.emit()



if __name__ == '__main__':
    from py.qsqlite import QSqlite
    from config import LOCAL_DB_PATH
    from py.logger import Logger
    l = Logger().configure()
    qsql = QSqlite(LOCAL_DB_PATH, 'test')
    qsql.open_connection()
    m = QSqlQueryModel()
    q = QSqlQuery(qsql.db)
    q.prepare('select * from images_vw')
    q.exec()
    m.setQuery(q)
    l.info("Running thru results")
    for i in range(m.rowCount()):
        _r = m.record(i)
        _keys = [_r.fieldName(k) for k in range(_r.count())]
        _vals = [_r.value(k) for k in _keys]
        record_dict = dict(zip(_keys, _vals))
        print(record_dict)
        # print(m.record(i).)


