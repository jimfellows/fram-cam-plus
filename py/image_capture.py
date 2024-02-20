

from PySide6.QtCore import QObject, Slot, Property
from PySide6.QtMultimedia import (QAudioInput, QCamera, QCameraDevice,
                                  QImageCapture, QMediaCaptureSession,
                                  QMediaDevices, QMediaMetaData,
                                  QMediaRecorder)
from py.logger import Logger
from config import IMAGES_DIR
from __feature__ import snake_case  # convert Qt methods to snake


class ImageCapture(QObject):

    def __init__(self, db, app=None):
        super().__init__()
        self._logger = Logger().get_root()
        self._app = app
        self._devices = QMediaDevices()
        self._camera = QCamera(QMediaDevices.default_video_input())
        self._capture_session = QMediaCaptureSession()
        self._capture_session.set_camera(self._camera)
        self._is_capturing = False
        self._camera.start()

    @Property(QObject)
    def camera(self):
        return self._camera

    @Slot()
    def start_camera(self):
        self._logger.info(f"Starting camera {self._camera.camera_device().description()}")
        self._camera.start()

    @Slot()
    def stop_camera(self):
        self._camera.stop()

    def get_image_name(self):
        haul_number = self._app.settings.cur_haul_number if self._app.settings.cur_haul_number else ''
        catch_display = self._app.settings.cur_catch_display if self._app.settings.cur_catch_display else ''
        project = self._app.settings.cur_project if self._app.settings.cur_project else ''
        bio_label = self._app.settings.cur_bio_label if self._app.settings.cur_bio_label else ''
        print(f"{haul_number}_{catch_display}_{project}_{bio_label}")


    @Slot()
    def capture_image_to_file(self):
        self.get_image_name()


if __name__ == '__main__':
    pass

