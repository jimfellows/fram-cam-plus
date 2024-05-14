

# standard imports
import os
import shutil
import json

# local imports
from py.logger import Logger
from py.qt_models import FramCamFilterProxyModel
from py.images_model import ImagesModel

# 3rd party imports
from PySide6.QtCore import (
    QObject,
    Slot,
    Property,
    Signal,
    QThread,
    QRegularExpression
)

from PIL import Image
import piexif



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
    currentImageChanged = Signal()
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
        self._images_proxy = FramCamFilterProxyModel(self._images_model, name='images_proxy')  # allows filtering by haul/catch/proj/bio

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

        self._images_model.currentImageChanged.connect(self.currentImageChanged.emit)

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

