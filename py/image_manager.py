
# from __future__ import annotations

from PySide6.QtCore import QObject, Slot, QFile, QTextStream, QMimeDatabase, QFileInfo, QStandardPaths, Property, QAbstractListModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import QFileSystemModel
from config import IMAGES_DIR
from py.logger import Logger
from dataclasses import dataclass, fields
# https://stackoverflow.com/questions/72367333/using-listmodel-python-pyside6-in-qml
# from __feature__ import snake_case  # convert Qt methods to snake
import os
from datetime import datetime




import os
import sys
import typing
from dataclasses import dataclass, fields
from pathlib import Path


@dataclass
class ImageFile:
    file_path: str = ""
    file_name: str = ""
    created_dt: datetime = None
    is_synced: bool = False

class ImagesListModel(QAbstractListModel):

    imageAdded = Signal()
    imageRemoved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logger = Logger.get_root()
        self._file_path_list = []
        # self._role_names = {'file_path'}

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount():
            file = self._file_path_list[index.row()]
            name = self.roleNames().get(role)
            if name:
                return getattr(file, name.decode())

    def roleNames(self):
        d = {}
        for i, field in enumerate(fields(ImageFile)):
            d[Qt.DisplayRole + i] = field.name.encode()
        return d

    def rowCount(self, index: QModelIndex = QModelIndex()):
        return len(self._file_path_list)

    @Slot(str)
    def add_image(self, image_path):
        self._logger.info(f"Trying to add image {image_path}")
        if not os.path.exists(image_path):
            self._logger.error(f"Unable to add image to model, file DNE: {image_path}")
            return

        try:
            self.beginInsertRows(QModelIndex(), len(self._file_path_list), len(self._file_path_list))
            file_name = os.path.basename(image_path)
            created_dt = datetime.fromtimestamp(os.path.getctime(image_path))
            image_file = ImageFile(image_path, file_name, created_dt, False)
            self._file_path_list.append(image_file)
            self.imageAdded.emit()
            self.endInsertRows()
        except Exception as e:
            self._logger.error(f"ERROR {e}")

    def remove_image(self, file_path):
        self.imageRemoved.emit()

    def populate(self):
        for i in os.listdir(IMAGES_DIR):
            full_path = os.path.join(IMAGES_DIR, i)
            self.add_image(full_path)

class ImageManager(QObject):

    unusedSignal = Signal()
    modelChanged = Signal()

    def __init__(self, app=None):
        super().__init__()
        self._logger = Logger.get_root()
        self._app = app
        self._model = ImagesListModel()
        self._model.populate()
        self._model.imageAdded.connect(lambda: self.modelChanged.emit())
        self._model.imageRemoved.connect(lambda: self.modelChanged.emit())

        self._app.image_capture.image_capture.imageSaved.connect(lambda ix, path: self.model.add_image(path))

    @Property(QObject, notify=modelChanged)
    def model(self):
        return self._model





if __name__ == '__main__':
    m = ImagesListModel()
    print(m.roleNames())