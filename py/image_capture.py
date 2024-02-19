

from PySide6.QtCore import QObject, Slot, Property
from PySide6.QtMultimedia import (QAudioInput, QCamera, QCameraDevice,
                                  QImageCapture, QMediaCaptureSession,
                                  QMediaDevices, QMediaMetaData,
                                  QMediaRecorder)
from py.logger import Logger
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

    @Property(QCamera)
    def camera(self):
        return self._camera

    @Slot()
    def start_camera(self):
        self._logger.info(f"Starting camera {self._camera.camera_device().description()}")
        self._camera.start()

    @Slot()
    def stop_camera(self):
        self._camera.stop()

    @Slot()
    def capture_image_to_file(self):
        pass


if __name__ == '__main__':
    fc = FramCamera()
    fc.start()

