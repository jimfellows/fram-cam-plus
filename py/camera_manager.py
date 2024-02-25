
# standard imports
import os
from pathlib import Path
import re

# local imports
from py.logger import Logger
from py.utils import Utils
from config import IMAGES_DIR
from py.qt_models import FramCamQueryModel

# 3rd party imports
from PySide6.QtCore import (
    QObject,
    Slot,
    Property,
    Signal,
    Qt,
    QAbstractListModel
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

from PySide6.QtSql import QSqlTableModel, QSqlQueryModel, QSqlQuery
from __feature__ import snake_case  # convert Qt methods to snake


class ImagesListModel(QAbstractListModel):

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db = db
        self._query_model = QSqlQueryModel()
        self._query = QSqlQuery(self._db)
        self._sql = 'select * from images_vw'
        self._records = []

    def populate(self):
        self._query.prepare(self._sql)
        self._query.exec()
        self._query_model.set_query(self._query)

    def row_count(self, index):
        return len(self._records)

    def data(self, index, role: int):
        if not index.is_valid():
            return

        if role == Qt.DisplayRole:
            try:
                val = self._records[index.row()].value(self.role_names()[role].decode('utf-8'))
                return self._records[index.row()].value(self.role_names()[role].decode('utf-8'))
            except:
                return None

    def get_value(self, i, key):
        return self._records[i].value(key)

    def role_names(self):
        _rec = self._query_model.record()
        _fields = [_rec.field(f).name().lower() for f in range(0, _rec.count())]
        return {Qt.DisplayRole + i: r.encode("utf-8") for i, r in enumerate(_fields)}


class ImagesViewModel(QSqlQueryModel):

    model_changed = Signal()

    def __init__(self, db):
        super().__init__()
        self._db = db
        self._sql = '''
            select  *
            from    IMAGES_VW
            where   coalesce(:haul_id, haul_id) = haul_id
                    and coalesce(:catch_id, catch_id) = catch_id
                    and coalesce(:project_name, project_name) = project_name
                    and coalesce(:bio_label, bio_label) = bio_label
        '''
        self._query = QSqlQuery(db)
        self._query.prepare(self._sql)
        self._current_index = -1

    def load(self, haul_id=None, catch_id=None, project_name=None, bio_label=None):
        self._query.bind_value(':haul_id', haul_id)
        self._query.bind_value(':catch_id', catch_id)
        self._query.bind_value(':plan_name', project_name)
        self._query.bind_value(':bio_label', bio_label)
        self._query.exec()
        self.set_query(self._query)
        self.model_changed.emit()

    def data(self):
        pass

    def row_count(self):
        pass

    def role_names(self):
        pass

    @Slot(int, str, result="QVariant")
    def get_value(self, row_ix, field_name):
        print(f"Trying to get value {field_name} at {row_ix}")
        print(f"new val = {self.record(row_ix).value(field_name)}")
        return self.record(row_ix).value(field_name)

class ImagesModel(QSqlTableModel):

    model_changed = Signal()

    def __init__(self, db):
        super().__init__(db=db)
        self.set_table('IMAGES')
        self.set_edit_strategy(QSqlTableModel.OnManualSubmit)
        self.select()  # load me, should this be in INIT?

class ImagesViewModelV1(FramCamQueryModel):

    def __init__(self, db):
        super().__init__(db)
        self._sql = '''
            select  HAUL_NUMBER
                    ,FILE_PATH
                    ,FILE_NAME
                    ,FULL_PATH
            from    IMAGES_VW
        '''
        self._roles = ['haul_number', 'file_path', 'file_name', 'full_path']
        self.populate()
        # self.set_role_names = self._roles

    @Slot(int, name="populate")
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
        self.clear()
        self._query.prepare(self._sql)
        self._query.bind_value(':haul_id', haul_id)
        self._query.bind_value(':catch_id', catch_id)
        self._query.bind_value(':plan_name', project_name)
        self._query.bind_value(':bio_label', bio_label)
        self._query.exec()
        self.set_query(self._query)
        self.model_changed.emit()

class CameraManager(QObject):

    unusedSignal = Signal()
    images_view_changed = Signal()
    images_model_changed = Signal()

    def __init__(self, db, app=None):
        super().__init__()
        self._app = app
        self._db = db
        self._logger = Logger.get_root()
        self._devices = QMediaDevices()
        print(self._devices)
        self._camera = QCamera(QMediaDevices.default_video_input())
        self._image_capture = QImageCapture()
        self._capture_session = QMediaCaptureSession()
        self._capture_session.set_camera(self._camera)
        self._capture_session.set_image_capture(self._image_capture)
        self._is_capturing = False
        # self.start_camera()
        self._is_camera_running = None

        self._images_model = ImagesModel(self._db)
        # self._images_view_model = ImagesViewModel(self._db)
        self._images_view_model = ImagesListModel(self._db)
        self._images_view_model.populate()

        self._image_capture.imageSaved.connect(lambda ix, path: self.create_new_image_record(path))  # image save is async, so hooking to signal

    @Property(QObject, notify=images_model_changed)
    def images_view_model(self):
        return self._images_view_model

    @Property(QObject, notify=images_model_changed)
    def images_model(self):
        return self._images_model

    @Property(QObject)
    def camera(self):
        return self._camera

    @Property(QObject)
    def image_capture(self):
        return self._image_capture

    @Slot(QObject)
    def set_video_output(self, output):
        self._capture_session.set_video_output(output)

    @Property(QObject)
    def capture_session(self):
        return self._capture_session

    @Slot()
    def start_camera(self):
        self._logger.info(f"Starting camera {self._camera.camera_device().description()}")
        self._camera.start()
        # self._is_camera_running = True

    @Slot()
    def stop_camera(self):
        self._camera.stop()
        # self._is_camera_running =

    @Property(bool)
    def is_camera_active(self):
        return self._camera.is_active()

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
        img_result = self._image_capture.capture_to_file(full_path)
        self._logger.info(f"Capturing image to {full_path}, capture result={img_result}")

    def create_new_image_record(self, image_path):
        self._logger.info(f"Creating new image here: {image_path}")
        img = self._images_model.record()
        img.set_value(self._images_model.field_index('FILE_PATH'), os.path.dirname(image_path))
        img.set_value(self._images_model.field_index('FILE_NAME'), os.path.basename(image_path))
        img.set_value(self._images_model.field_index('HAUL_ID'), self._app.state.cur_haul_id)
        img.set_value(self._images_model.field_index('CATCH_ID'), self._app.state.cur_catch_id)
        img.set_value(self._images_model.field_index('SPECIMEN_ID'), self._app.state.cur_specimen_id)
        self._images_model.insert_record(-1, img)
        self._images_model.submit_all()
        self.images_model_changed.emit()


if __name__ == '__main__':
    logger = Logger().configure()
    from config import LOCAL_DB_PATH
    from py.qsqlite import QSqlite, QSqlQuery
    from PySide6.QtSql import QSqlQueryModel

    class Test(QSqlQueryModel):

        def __init__(self):
            super().__init__()
            self.roles = [
                'file_name',
                'file_path'
            ]

        def role_names2(self):
            pass
        def role_names(self):
            return {Qt.UserRole + i: r for i, r in enumerate(self.roles)}

            # roles = {
            #     Qt.UserRole + 1: 'file_name',
            #     Qt.UserRole + 2: 'file_path',
            # }
            # return roles

    sqlite = QSqlite(LOCAL_DB_PATH, 'test')
    sqlite.open_connection()
    m = Test()
    q = QSqlQuery(sqlite.db)
    q.prepare('select file_name, file_path from images_vw')
    q.exec()
    m.set_query(q)
    # m.set_header_data(0, Qt.Horizontal, 'file_name')
    # m.set_header_data(1, Qt.Horizontal, 'file_path')
    # print(m.record())
    print(m.role_names())
    # print(m.row_count())
    # print(m.header_data())


