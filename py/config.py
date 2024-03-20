
import os
from pathlib import Path

HOME_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print(HOME_DIR)
DATA_DIR = os.path.join(HOME_DIR, 'data')
IMAGES_DIR = os.path.join(DATA_DIR, 'images')
LOCAL_DB_PATH = os.path.join(DATA_DIR, 'trawl_backdeck.db')
LOGS_DIR = os.path.join(HOME_DIR, 'logs')
BUILD_DIR = os.path.join(HOME_DIR, 'build')
QRC_DIR = os.path.join(HOME_DIR, 'qrc')
QML_DIR = os.path.join(HOME_DIR, 'qml')
VERSION_NUMBER = '2024.1+1'
