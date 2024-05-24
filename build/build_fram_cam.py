

import sys
import os
import shutil

from cx_Freeze import setup, Executable
from build_utils import make_nsis_installer
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # gross, how can i do this better

from py.config import VERSION_NUMBER


PYTHON_DIR = sys.exec_prefix

# look for sqlite3.dll in a few places (conda envs, others..), if not found, script will error out
sqlite_dll_paths = ['DLLs\sqlite3.dll', 'Scripts\sqlite3.dll']
path_sqlite_dll = None
for p in sqlite_dll_paths:
    full_path = os.path.join(PYTHON_DIR, p)
    if os.path.exists(full_path):
        path_sqlite_dll = full_path

# incase cx_freeze doesnt set these shiboken vars
# tcl_paths = [r'Lib\tcl8.6', r'DLLs\tcl8.6']
# for p in tcl_paths:
#     full_tcl_path = os.path.join(PYTHON_DIR, p)
#     if os.path.exists(full_tcl_path):
#         os.environ['TCL_LIBRARY'] = full_tcl_path
#         os.environ['TK_LIBRARY'] = full_tcl_path

# incase cx_freeze doesnt set these TCL vars
tcl_paths = [r'Lib\tcl8.6', r'DLLs\tcl8.6']
for p in tcl_paths:
    full_tcl_path = os.path.join(PYTHON_DIR, p)
    if os.path.exists(full_tcl_path):
        os.environ['TCL_LIBRARY'] = full_tcl_path
        os.environ['TK_LIBRARY'] = full_tcl_path

excludes = []
include_files = [
    ['py', 'lib/py'],  # puts local py imports into lib
    ['qrc', 'lib/qrc'],
    ['data/fram_cam.db', 'lib/data/fram_cam.db'],  # data also into lib
    [os.path.join(PYTHON_DIR, 'lib/site-packages/shiboken6/'), 'lib/shiboken6/'],
    [os.path.join(PYTHON_DIR, 'Lib/site-packages/pyzbar/libiconv.dll'), 'lib/libiconv.dll'],
    # did adding opencv resolve the need for this?
    ['resources/icons', 'lib/icons']
]
packages = ["PySide6", "pyzbar", "cv2", 'araviq6', 'sqlite3', "encodings", 'piexif', 'PIL']
path = []

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
                     'includes':      [],
                     'include_files': include_files,
                     'excludes':      excludes,
                     'packages':      packages,
                     'path':          path,
                     'build_exe':     'build/exe.win64-3.6/FramCam+'
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
exe = None
if sys.platform == 'win32':
    exe = Executable(
        target_name='FramCam+.exe',
        script='main.py',
        base='Win32GUI',  # use this to hide console output (releases)
        icon='resources/icons/blue_nautilus.ico'
    )

# Prompt to nuke existing directory
deployed_path = r'build\exe.win64-3.6\FramCam+'
if os.path.exists(deployed_path):
    shutil.rmtree(deployed_path)

setup(
      name='FramCam',
      options={'build_exe': build_exe_options},
      executables=[exe]
)

make_nsis_installer('build/fram_cam_setup.nsi', VERSION_NUMBER)

