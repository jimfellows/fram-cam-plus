
QML_IMPORT_NAME = "com.library.name"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0 # Optional

from PySide6.QtCore import QObject, Slot, Property, Signal
from PySide6.QtQml import QmlElement
from PySide6.QtMultimedia import (QAudioInput, QCamera, QCameraDevice,
                                  QImageCapture, QMediaCaptureSession,
                                  QMediaDevices, QMediaMetaData, QVideoSink,
                                  QMediaRecorder)
from py.logger import Logger
from config import IMAGES_DIR
import os
from py.utils import Utils
import re
from pathlib import Path
from __feature__ import snake_case  # convert Qt methods to snake
import time


class ImageCapture(QObject):

    unusedSignal = Signal()

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
        """
        build image file name with current settings
        TODO: what if catch/project/bio isnt selected? need these to be null
        :param ext: str, extension specified, default to jpg
        :return: str, name of image file
        """
        haul_number = self._app.settings.cur_haul_number if self._app.settings.cur_haul_number else ''
        vessel_code = Utils.get_vessel_code_from_haul(haul_number)
        vessel_haul = vessel_code + haul_number[-3:]
        catch_display = Utils.scrub_str_for_file_name(self._app.settings.cur_catch_display) if self._app.settings.cur_catch_display else ''
        project = Utils.scrub_str_for_file_name(self._app.settings.cur_project) if self._app.settings.cur_project else ''
        bio_label = self._app.settings.cur_bio_label if self._app.settings.cur_bio_label else ''
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


if __name__ == '__main__':
    pass

