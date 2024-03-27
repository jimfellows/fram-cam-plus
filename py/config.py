
"""
    config.py: location to store global variables to be re-used throughout the project.

    Note that to date all paths are based on the parent directory of this file;
    Moving this file will mean all other paths will change.

    TODO: should we be using more Path() objects???  this works for now
    TODO: should we call os.makedirs(<PATH>, exists_ok=True) on all of these?
"""

import os
from pathlib import Path

# full paths relative to intial home directory (one up from py/config.py)
HOME_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(HOME_DIR, 'data')  # sqlite + data produced by the app lives here

IMAGES_DIR = os.path.join(DATA_DIR, 'images')  # captured images, subdir of "data"
os.makedirs(IMAGES_DIR, exist_ok=True)

LOCAL_DB_PATH = os.path.join(DATA_DIR, 'fram_cam.db')  # path to sqlite file

LOGS_DIR = os.path.join(HOME_DIR, 'logs')  # logging writes to files here, should be one file per day, per machine
os.makedirs(LOGS_DIR, exist_ok=True)

BUILD_DIR = os.path.join(HOME_DIR, 'build')  # builds go here do we use this???
QRC_DIR = os.path.join(HOME_DIR, 'qrc')  # compiled QRC resources go here
QML_DIR = os.path.join(HOME_DIR, 'qml')  # qml


VERSION_NUMBER = '2024.0.0+1'
