
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # gross, how can i do this better

import re
import fileinput
from py.config import QRC_DIR
from pathlib import Path


# to date, when pyside is installed this exe should be in venv/Scripts
RCC_EXE = Path(os.path.join(os.path.dirname(sys.executable), 'pyside6-rcc.exe'))

def compile_qresources():
    _in = os.path.join(QRC_DIR, 'qresources.qrc')
    _out = os.path.join(QRC_DIR, 'qresources.py')
    compile_qrc_file(_in, _out)


def compile_qrc_file(source_qrc_file, dest_py_file):
    """
    use pyside6-rcc.exe to create python files from qrc
    :param source_qrc_file: full path to qrc file
    :param dest_py_file: destination of python output file
    """
    subprocess.run([RCC_EXE, source_qrc_file, '-o', dest_py_file])


def increment_build_number(build_config_path, var_name, do_increment=True) -> str:
    """
    Increment build number.  Assumes format of versioning is MAJOR.MINOR.PATCH+BUILD,
    where each component is an undefined number of digits.  Copied from build_observer,
    but altered to accommodate other app version variables.

    :param build_config_path: relative path to config file where version# lives
    :param var_name: name of python version variable (assumes format VAR_NAME = '')
    :param do_increment: perform increment. For testing, can set this to False
    :return: version string
    """
    if not os.path.exists(build_config_path):
        print(f'*** Unable to increment build #.  Cant find config file {build_config_path}.')
        return ''
    version_info = None
    for i, line in enumerate(fileinput.input(build_config_path, inplace=1)):
        m = re.search(var_name + r' = \"[0-9]*\.[0-9]*\.[0-9]*\+(?P<build_num>[0-9]*)', line)
        if m:
            old_build_num = int(m.group('build_num'))
            if do_increment:
                line = line.replace('+' + str(old_build_num), '+' + str(old_build_num + 1))
            m = re.search(var_name + r' = \"(?P<ver>[0-9]*\.[0-9]*\.[0-9]*\+[0-9]*)', line)
            version_info = m.group('ver')
        sys.stdout.write(line)

    return version_info


def make_nsis_installer(nsi_file, version):
    """
    Call me during build process after cx_Freeze dir has been
    created.  NSIS setup.nsi expects VERSION var input from command line
    PRE-REQ: https://nsis.sourceforge.io/Download, command makensis needs to
    be avaible as command
    :nsi_file: path to .nsi file NSIS def for installer
    :version: str, from PyCollector.version.PYCOLLECTOR_VERSION
    """
    try:
        print(f"Building NSIS Installer with {nsi_file}, v{version}...")
        subprocess.check_output(f"makensis /DVERSION={version} {nsi_file}")
    except Exception as e:
        print(f"Unable to build NSIS Installer: {e}")
