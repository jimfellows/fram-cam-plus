


from PySide6.QtCore import (
    QObject,
    Slot,
    Property,
    Signal,
    Qt
)
from PySide6.QtSql import (
    QSqlTableModel,
    QSqlRelationalTableModel,
    QSqlQueryModel
)

# import PySide6.QtMultimedia
import PySide6.QtMultimedia

# from PySide6.QtMultimedia import (
#     QAudioInput,
#     QCamera,
#     QCameraDevice,
#     QImageCapture,
#     QMediaCaptureSession,
#     QMediaDevices
#     QMediaMetaData,
#     QVideoSink,
#     QMediaRecorder
# )

from py.logger import Logger
from config import IMAGES_DIR
import os
from py.utils import Utils
# from py.qt_models import FramCamQueryModel, FramCamTableModel
import re
from pathlib import Path

from __feature__ import snake_case  # convert Qt methods to snake
import time


class ImagesViewModel(FramCamQueryModel):

    def __init__(self, db):
        super().__init__(db)
        self._sql = '''
            select  * 
            from    IMAGES_VW
            where   coalesce(:haul_id, haul_id) = haul_id
                    and coalesce(:catch_id, catch_id) = catch_id
                    and coalesce(:project_name, project_name) = project_name
                    and coalesce(:bio_label, bio_label) = bio_label
        '''
        self.populate()

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


class FramCamera(QObject):

    unusedSignal = Signal()
    images_view_changed = Signal()
    images_model_changed = Signal()

    def __init__(self, db, app=None):
        super().__init__()
        self._db = db
        self._logger = Logger().get_root()
        self._app = app
        self._devices = QMediaDevices()
        self._camera = QCamera(QMediaDevices.default_video_input())
        self._image_capture = QImageCapture()
        self._capture_session = QMediaCaptureSession()
        self._capture_session.set_camera(self._camera)
        self._capture_session.set_image_capture(self._image_capture)
        self._is_capturing = False
        self.start_camera()
        self._is_camera_running = None

        self._images_model = FramCamTableModel(db, 'IMAGES')
        self._images_view_model = ImagesViewModel(db=db)

        self._images_view_model.model_changed.connect(lambda: self.images_view_changed.emit()) # hook up generic model changed signal to view
        self._image_capture.imageSaved.connect(lambda ix, path: self.create_new_image_record(path))  # image save is async, so hooking to signal
        self.images_model_changed.connect(self._on_images_model_changed)  # anytime images model changed, call wrapper func

        # self._test_model = FramCamQueryModel(self._db, sql='select FILE_NAME from IMAGES_VIEW')
        # self._test_model.set_header_data(0, Qt.Horizontal, "FILE_NAME")
        # self._test_model.query.prepare(self._test_modelsql)
        # self._test_model.query.exec()
        # self._test_model.set_query(self._test_model.query)
        # self._test_model.

    @Property(QObject)
    def test_model(self):
        # return self._test_model
        return []
    @Property(QObject)
    def images_model(self):
        return self._images_model

    def _on_images_model_changed(self):
        self._images_view_model.populate(
            haul_id = self._app.state.cur_haul_id,
            catch_id = self._app.state.cur_catch_id,
            project_name = self._app.state.cur_project,
            bio_label=self._app.state.cur_bio_label
        )

    @Property(QObject)
    def images_view_model(self):
        return self._images_view_model

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
        print(f"Creating new image record at path {image_path}")
        img = self._images_model.record()
        img.set_value(self._images_model.field_index('FILE_PATH'), os.path.dirname(image_path))
        img.set_value(self._images_model.field_index('FILE_NAME'), os.path.basename(image_path))
        img.set_value(self._images_model.field_index('HAUL_ID'), self._app.state.cur_haul_id)
        img.set_value(self._images_model.field_index('CATCH_ID'), self._app.state.cur_catch_id)
        img.set_value(self._images_model.field_index('SPECIMEN_ID'), self._app.state.cur_specimen_id)
        self._images_model.insert_record(-1, img)
        self._images_model.submit_all()
        # self._images_model.
        print(self._db.last_error())

if __name__ == '__main__':
    from config import LOCAL_DB_PATH
    from py.qsqlite import QSqlite
    sqlite = QSqlite(LOCAL_DB_PATH, 'test')
    sqlite.open_connection()

