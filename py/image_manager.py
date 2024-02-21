
from PySide6.QtCore import QObject, Slot, QFile, QTextStream, QMimeDatabase, QFileInfo, QStandardPaths
from PySide6.QtWidgets import QFileSystemModel
from config import IMAGES_DIR
from __feature__ import snake_case  # convert Qt methods to snake


class ImageManager(QObject):

    def __init__(self):
        super().__init__()
        self._model = QFileSystemModel()
        print(IMAGES_DIR)
        # self._model.set_root_path(QStandardPaths.writable_location(IMAGES_DIR))
        self._model.set_root_path(IMAGES_DIR)



if __name__ == '__main__':
    ImageManager()