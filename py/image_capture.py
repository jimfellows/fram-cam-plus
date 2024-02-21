
QML_IMPORT_NAME = "com.library.name"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0 # Optional

from PySide6.QtCore import QObject, Slot, Property
from PySide6.QtQml import QmlElement
from PySide6.QtMultimedia import (QAudioInput, QCamera, QCameraDevice,
                                  QImageCapture, QMediaCaptureSession,
                                  QMediaDevices, QMediaMetaData, QVideoSink,
                                  QMediaRecorder)
from py.logger import Logger
from config import IMAGES_DIR
import os
from __feature__ import snake_case  # convert Qt methods to snake


class ImageCapture(QObject):

    def __init__(self, db, app=None):
        super().__init__()
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
        haul_number = self._app.settings.cur_haul_number if self._app.settings.cur_haul_number else ''
        catch_display = self._app.settings.cur_catch_display if self._app.settings.cur_catch_display else ''
        project = self._app.settings.cur_project if self._app.settings.cur_project else ''
        bio_label = self._app.settings.cur_bio_label if self._app.settings.cur_bio_label else ''
        return f"{haul_number}_{catch_display}_{project}_{bio_label}.{ext}"


    @Slot()
    def capture_image_to_file(self):
        img_name = self.get_image_name()
        full_path = os.path.join(IMAGES_DIR, img_name)
        self._logger.info(f"Capturing image to {full_path}")
        img_result = self._image_capture.capture_to_file(full_path)
        self._logger.info(f"Img result: {img_result}")


@QmlElement
class FramCamCaptureSession(QMediaCaptureSession):

    def __init__(self):
        super().__init__()
        self._

if __name__ == '__main__':
    pass

