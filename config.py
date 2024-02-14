
import os
from pathlib import Path

HOME_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HOME_DIR, 'data')
LOCAL_DB_PATH = os.path.join(DATA_DIR, 'trawl_backdeck.db')
LOGS_DIR = os.path.join(HOME_DIR, 'logs')
BUILD_DIR = os.path.join(HOME_DIR, 'build')
QRC_DIR = os.path.join(HOME_DIR, 'qrc')
QML_DIR = os.path.join(HOME_DIR, 'qml')
VERSION_NUMBER = '2024.1+1'
