# fram-cam-plus

PySide6 + Qt6 + QML tablet app for intelligent image capture at sea. 

This application is developed for usage on Panasonic Toughpads running Windows 10, and is designed to integrate with existing software
used by NOAA software used for at-sea data collection on the Northwest Fisheries Science Center's West Coast Groundfish
Bottom Trawl Survey.

The front end of this application is written using Qt's QML framework, and generally attempts to follow Qt's Model/View architecture.

* [Qt for Python](https://wiki.qt.io/Qt_for_Python)
* [QML](https://doc.qt.io/qt-6/qtqml-index.html)
* [Qt Model/View Architecture](https://doc.qt.io/qt-6/model-view-programming.html)

The goal of this application is to streamline adhoc image capture in the field that to date involves using
a small digital camera, and manually compiling these images postseason.  The general workflow of this app is as follows:

1. Retrieve catch sampling data from the backdeck application
2. Capture images and tag and associate them with the retrieved data
3. Submit the images back to the backdeck software and/or wheelhouse computer

The resulting data set produced is more easily packaged with the tow and catch-level data, and improves the data collection workflow
in the following ways:

* More complete and seamless image collection in the field
* Eliminates the need for post-season image compilation and annotation

## Qt Resource System
The [Qt Resource System](https://doc.qt.io/qt-6/resources.html) is used to compile files for import into the python
backdend of this app.  In addition to image files, QML files are also included in this compile step to help relative
pathing and imports function correctly once the app has been bundled via cx_freeze.

All resources should be listed in qrc/qresoucres.qrc; the compile step is included in compile_and_run.py,
but can also be executed (requires PySide6 install) as follows:

```.\venv\scripts\pyside6-rcc.exe qrc\qresources.qrc -o qrc\qresources.py```

Once compiled, these binary files are made available to the app via an import of qresources.py
in py/app.py.  Newly created QML files or images/svgs/icons should be added to the qresources.qrc file.

## Qt Creator Usage
* [Qt Creator](https://doc.qt.io/qtcreator/)

## Environment Setup

For now, notes for myself, used pyenv-win to setup venv:
```commandline
pyenv install 3.11.2
pyenv shell 3.11.2
pyenv exec python -m venv venv311
.\venv311\scripts\activate
python
```

## Running the App

## Building the App
This app uses cx_Freeze to freeze and distribute an exectueable to run this application.
See the link below, to date (March 2024), the latest release of cx_Freeze isn't compatible with ptyyhono 
3.12, see link below:

https://stackoverflow.com/questions/77861331/cant-create-a-a-exe-file-using-cxfreeze-keyerror-import-star

Also, shiboken6 DLL files aren't fully copying to the bundled cx_Freeze app, so the entirety
of lib/shiboken6 needs to be copied (TODO: fix this?)

cx_Freeze params are set in the pyproject.toml file, to build, call the following from the root dir:

```commandline
cxfreeze build
```

[NSIS](https://nsis.sourceforge.io/Download)
