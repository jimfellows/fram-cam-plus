
# standard imports
import os
from pathlib import Path
import re

# local imports
from py.logger import Logger
from py.utils import Utils
from config import IMAGES_DIR
from py.qt_models import ImagesModel, FramCamFilterProxyModel

# 3rd party imports
from PySide6.QtCore import (
    QObject,
    Slot,
    Property,
    Signal,
    Qt,
    QAbstractListModel,
    QModelIndex,
)

from PySide6.QtGui import QPainter, QImage

from PySide6.QtMultimedia import (
    QAudioInput,
    QCamera,
    QCameraDevice,
    QImageCapture,
    QMediaCaptureSession,
    QMediaDevices,
    QMediaMetaData,
    QVideoSink,
    QMediaRecorder,
    QVideoFrame
)

from PySide6.QtSql import QSqlTableModel, QSqlQueryModel, QSqlQuery, QSqlRecord

# from qimage2ndarray import

import cv2
import numpy as np
import ctypes
from dataclasses import dataclass
from functools import cached_property


# https://gist.github.com/eyllanesc/6486dc26eebb1f1b71469959d086a649#gistcomment-3920960
# https://forum.qt.io/topic/130014/qcamera-draw-on-viewfinder/9


class CameraManager(QObject):

    unusedSignal = Signal()
    images_view_changed = Signal()
    images_model_changed = Signal()
    activeCameraChanged = Signal()
    videoFrameProcessed = Signal("QVariant", arguments=['new_frame'])

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
        self._images_model = ImagesModel(self._db)
        self._images_proxy = FramCamFilterProxyModel(self._images_model)
        # self._images_model.sendIndexToProxy.connect(lambda _i: self._images_proxy.setProxyIndexSilently(_i))

        # setup sink from which we grab images prior to processing
        self._source_sink = QVideoSink()
        self._target_sink = None
        self._capture_session.setVideoSink(self._source_sink)
        self._capture_session.videoSink().videoFrameChanged.connect(lambda f: self._process_video_frame(f))
        self._video_output = None

        # self._capture_session.setVideoOutput(self._video_sink)
        self._image_capture.imageSaved.connect(lambda ix, path: self._on_image_saved(path))  # image save is async, so hooking to signal

        self._app.data_selector.curHaulChanged.connect(self._filter_images_model)
        self._app.data_selector.curCatchChanged.connect(self._filter_images_model)
        self._app.data_selector.curProjectChanged.connect(self._filter_images_model)
        self._app.data_selector.curBioChanged.connect(self._filter_images_model)
        self._load_images_model()
        self._filter_images_model()
        self._painter = QPainter()

    # @Slot(QObject)
    # def setVideoOutput(self, vo):
    #     self._video_output = vo
    #     print(self._video_output.__dict__)

    @Property(QObject)
    def targetSink(self):
        return self._target_sink

    @targetSink.setter
    def targetSink(self, new_video_sink):
        self._target_sink = new_video_sink

    @Property(QObject, constant=True)
    def painter(self):
        return self._painter

    def _process_video_frame(self, frame):
        # print(type(frame), frame)
        # self.videoFrameProcessed.emit(frame)
        print(frame)
        self._target_sink.setVideoFrame(frame)

    def _filter_images_model(self):
        _haul = self._app.data_selector.cur_haul_num or 'NULL'
        _catch = self._app.data_selector.cur_catch_display or 'NULL'
        _proj = self._app.data_selector.cur_project_name or 'NULL'
        _bio = self._app.data_selector.cur_bio_label or 'NULL'

        if not self._app.data_selector.cur_catch_display:
            search_str = f'"haul_number":"{_haul}"*'
        elif not self._app.data_selector.cur_project_name:
            search_str = f'"haul_number":"{_haul}","display_name":"{_catch}"*'
        elif not self._app.data_selector.cur_bio_label:
            search_str = f'"haul_number":"{_haul}","display_name":"{_catch}","project_name":"{_proj}"*'
        else:
            search_str = f'"haul_number":"{_haul}","display_name":"{_catch}","project_name":"{_proj}","bio_label":"{_bio}"'

        self._logger.info(f"Filtering images based on filter string: {search_str}")
        self._images_proxy.filterRoleOnRegex('image_filter_str', search_str)

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

    @Property(QObject, constant=True)
    def images_model(self):
        return self._images_model

    @Property(QObject, constant=True)
    def images_proxy(self):
        return self._images_proxy

    def _load_images_model(self):
        self._images_model.clearBindParams()
        self._images_model.setBindParam(':fram_cam_haul_id', self._app.data_selector.cur_haul_id)
        self._images_model.setBindParam(':fram_cam_catch_id', self._app.data_selector.cur_catch_id)
        self._images_model.setBindParam(':project_name', self._app.data_selector.cur_project_name)
        self._images_model.setBindParam(':bio_label', self._app.data_selector.cur_bio_label)
        self._logger.info(f"Loading images model for params {self._images_model._bind_params}")
        self._images_model.loadModel()

    def _on_image_saved(self, image_path):
        self.images_model.append_new_image(
            image_path,
            haul_id=self._app.data_selector.cur_haul_id,
            catch_id=self._app.data_selector.cur_catch_id,
            bio_id=self._app.data_selector.cur_bio_id
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
        haul_number = self._app.data_selector.cur_haul_num
        vessel_code = Utils.get_vessel_code_from_haul(haul_number)
        vessel_haul = vessel_code + haul_number[-3:]
        catch_display = Utils.scrub_str_for_file_name(self._app.data_selector.cur_catch_display) if self._app.data_selector.cur_catch_display else ''
        project = Utils.scrub_str_for_file_name(self._app.data_selector.cur_project_name) if self._app.data_selector.cur_project_name else ''
        bio_label = self._app.data_selector.cur_bio_label if self._app.data_selector.cur_bio_label else ''
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


