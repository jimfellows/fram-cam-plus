

from build.build_utils import compile_qrc_file
import subprocess
from config import QRC_DIR
import os
import sys

_in = os.path.join(QRC_DIR, 'qresources.qrc')
_out = os.path.join(QRC_DIR, 'qresources.py')
compile_qrc_file(_in, _out)

subprocess.call([sys.executable, '-m', 'main'])


