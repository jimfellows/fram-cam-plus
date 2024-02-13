
import os
from pathlib import Path

cwd = os.path.abspath(__file__)
PYTHON_DIR = str(Path(cwd))
HOME_DIR = str(Path(cwd).parents[1])
DATA_DIR = os.path.join(HOME_DIR, 'data')
LOCAL_DB_PATH = os.path.join(DATA_DIR, 'trawl_backdeck.db')
LOGS_DIR = os.path.join(HOME_DIR, 'logs')
BUILD_DIR = os.path.join(HOME_DIR, 'build')
VERSION_NUMBER = '2024.1+1'
