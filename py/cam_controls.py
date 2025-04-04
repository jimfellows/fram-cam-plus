
"""

"""
# standard imports
import os
from pathlib import Path
import re

# local imports
from py.logger import Logger
from py.utils import Utils
from py.config import IMAGES_DIR

# 3rd party imports
from araviq6 import VideoFrameWorker, VideoFrameProcessor, array2qvideoframe
import cv2
from PySide6.QtQml import QJSValue
from PySide6.QtCore import (
    QObject,
    Slot,
    Property,
    Signal,
    QJsonValue
)
from PySide6.QtMultimedia import (
    QCamera,
    QImageCapture,
    QMediaCaptureSession,
    QMediaDevices,
    QVideoSink,
    QVideoFrame
)
import numpy as np
import pyzbar.pyzbar
# import tensorflow as tf


class CVFrameWorker(VideoFrameWorker):
    """
    VideoFrameWorker class to apply opencv effects/processing to frames received from
    camera.

    This class is used with VideoFrameProcessor, and works as follows:

    1.) create this frame worker and a VideoFrameProcessor
    2.) add the worker to the processor: VideoFrameProcessor.setWorker(your_worker)
    3.) connect QCaptureSession videoSink.videoFrameChanged to processor.processVideoFrame to send frames from cam
    4.) process image array via this class's processArray method
    5.) receive processed array via the processors videoFrameProcessed signal
    6.) call videoSink.setVideoFrame(your_processed_frame) with sink associated with QML video output to display in UI

    camera -> session source sink -> frame -> processArray -> target sink -> video output

    https://gist.github.com/eyllanesc/6486dc26eebb1f1b71469959d086a649#gistcomment-3920960
    https://araviq6.readthedocs.io/en/stable/examples/frame.camera.html

    TODO: extract code from araviq6 package to eliminate dependency??
    """
    barcodeDetected = Signal("QVariant", "QVariant", arguments=['barcode', "barcode_coords"])  # a barcode was detected, notify others
    taxonDetected = Signal(str, arguments=['taxon_name'])  # a taxon class was detected
    feedFrozen = Signal()  # frame feed was stopped (setting pencil sketch effect)
    feedUnfrozen = Signal()  # frame feed resumed (unset pencil sketch effect)
    processingChanged = Signal()  # check if we actually need to pipe frame to CV worker
    isProcessingNecessary = Signal(bool, arguments=['status'])  # just go direct to UI? false means no processing
    sendFrameToDisplay = Signal("QVariant", arguments=['frame'])

    BARCODE_THROTTLE_COUNT = 10000  # use me to slow down emit sequence when we get a burst of detections

    def __init__(self):
        VideoFrameWorker.__init__(self)
        self._logger = Logger.get_root()
        self._barcode_polys = None  # array of coordinates defining bounding polygons for barcode detected
        self._last_barcode_scanned = None  # hold latest barcode scan here
        self._barcode_frames_scanned = 0  # use to count/limit frames scanned to boost performance, if needed
        self._taxon_frames_scanned = 0  # use to count/limit frames scanned to boost performance, if needed
        self._do_scan_barcode = False  # if true, scan image for barcode
        self._do_scan_taxon = False  # if true, scan image for taxon
        self._do_gaussian_blur = False  # if true, apply gaussian blur
        self._do_pencil_sketch = False  # if true, apply pencil sketch effect
        self._freeze_requested = False  # if true, apply pencil sketch and emit
        self._do_process = None  # if false, send frames direct to UI
        self.processingChanged.connect(self.check_processor_status)  # whenever a config changes, this emits
        self.cv_barcode_detector = cv2.barcode.BarcodeDetector()

    @property
    def do_process(self) -> bool:
        return self._do_process

    @do_process.setter
    def do_process(self, new_status: bool):
        if self._do_process != new_status:
            self._logger.debug(f"Status of frame processor changed, do_process={new_status}")
            self._do_process = new_status
            self.isProcessingNecessary.emit(new_status)

    def check_processor_status(self):
        self.do_process = self._do_scan_barcode or self._do_scan_taxon or self._do_pencil_sketch or self._do_gaussian_blur

    def request_freeze_frame(self):
        """
        allows us to do the following, synchronously:
        1. process one last frame using the pencil sketch effect
        2. tell processArray method that, once finished, emit signal to freeze processing
        3. this signal can then be picked up / connected to elsewhere to stop the camera
        """
        self._logger.info(f"Frame processing freeze requested")
        self.enable_pencil_sketch(True)
        self._freeze_requested = True

    def request_unfreeze(self):
        """
        idea here is to undo pencil sketch and re-enable frame-by-frame processing.
        The unfrozen signal should be picked up and connected to restarting the camera to
        begin re-piping data back through the frame processor, while also removing pencil sketch effect
        :return:
        """
        self._logger.debug(f"Frame processing unfreeze requested")
        self.enable_pencil_sketch(False)
        self._freeze_requested = False
        self.feedUnfrozen.emit()

    def enable_barcode_scanner(self, status: bool):
        """
        toggle whether we should scan each array for a barcode
        :param status: bool, set barcode scanner on or off?
        """
        self._logger.debug(f"Barcode scanner status set to: {status}")
        self._do_scan_barcode = status
        self.processingChanged.emit()

    def enable_taxon_scanner(self, status: bool):
        self._logger.debug(f"Taxon scanner status set to: {status}")
        self._do_scan_taxon = status
        self.processingChanged.emit()

    def enable_gaussian_blur(self, status: bool):
        self._logger.debug(f"Gausian blur status set to: {status}")
        self._do_gaussian_blur = status
        self.processingChanged.emit()

    def enable_pencil_sketch(self, status: bool):
        self._logger.debug(f"Pencil sketch status set to: {status}")
        self._do_pencil_sketch = status
        self.processingChanged.emit()

    # def set_frame_size

    def resize_image(self, img_array: np.ndarray) -> np.ndarray:
        """
        boost performance by downsizing image prior to processing
        :param img_array: cv image array
        :return: cv image array
        """
        _height, _width = img_array.shape[:2]

        # _max_height, _max_width = 720, 1280
        _max_height, _max_width = 480, 640

        if _height > _max_height or _width > _max_width:
            scaling_factor = _max_height / float(_height)
            if _max_width / float(_width) < scaling_factor:
                scaling_factor = _max_width / float(_width)

            # resize image
            img_array = cv2.resize(img_array, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
        _height, _width = img_array.shape[:2]

        return img_array

    def processArray(self, array: np.ndarray) -> np.ndarray:
        """
        for now, process every frame, but only redraw the rectangle every N frame processed, in an attempt
        to help the bounding box persist a bit longer on screen
        :param array: numpy array representing image pi3els
        :return: that same array, with a opencv bounding box drawn
        """
        array = self.resize_image(array)

        if self._do_scan_barcode:
            array = self._scan_barcode(array)

        if self._do_scan_taxon:
            array = self._scan_taxon(array)

        if self._do_gaussian_blur:
            array = self._gaussian_blur(array)
            self.sendFrameToDisplay.emit(array)

        if self._do_pencil_sketch:
            array = self._pencil_sketch(array)
            self.sendFrameToDisplay.emit(array)

        if self._freeze_requested:
            self.feedFrozen.emit()

        return array

    def _scan_taxon(self, array: np.ndarray) -> np.ndarray:
        """
        Placeholder, experimental processor that will scan image and attempt to
        classify taxonomy
        :param array: opencv image np_array (should we specify type here?)
        :return:
        """
        return array

    def _apply_threshold(self, array: np.ndarray) -> np.array:
        """
        https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html
        :param array: numpy ndimensional array (an image)
        :return:
        """
        ret, thresh1 = cv2.threshold(cv2.cvtColor(array, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)
        return thresh1

    def _apply_adaptive_threshold(self, array: np.ndarray) -> np.ndarray:
        return cv2.adaptiveThreshold(cv2.cvtColor(array, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    def _apply_adaptive_gaussian_threshold(self, array: np.ndarray) -> np.ndarray:
        return cv2.adaptiveThreshold(cv2.cvtColor(array, cv2.COLOR_BGR2GRAY), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    def _apply_otsus_binarization(self, array: np.ndarray) -> np.ndarray:
        ret, thresh = cv2.threshold(cv2.cvtColor(array, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return thresh

    def reset_last_barcode(self):
        self._last_barcode_scanned = None

    def _apply_barcode_polys_to_img(self, img_array, barcode_coords):
        return cv2.polylines(
            np.array(img_array),
            barcode_coords,
            True,
            (118, 230, 0),  # accent green
            # (205, 90, 106),  # red
            50  # nice and thick line that kind of looks like a barcode scanner
        )

    def _scan_barcode(self, array):
        """
        use zbar algorithm to identify barcode in cv array.
        If found, emit it to UI.  For now using a very basic thresholding is being used to help things out.
        Use binary threshold result for detection, but still return original image with polys drawn.
        :param array: array in format for cv
        :return: same array but with bounding poly drawn
        """
        _redraw_every_n = 1  # adjust higher if you want to not process each...
        _throttle_scan_for_n = 10
        try:
            if self._barcode_frames_scanned % _redraw_every_n == 0:
                # apply threshold to make barcode binary
                #_binary = self._apply_threshold(array)
                # _binary = self._apply_adaptive_threshold(array)
                _binary = self._apply_adaptive_gaussian_threshold(array)
                r = pyzbar.pyzbar.decode(_binary, symbols=[128, 39])  #symbols = ['128'] for now just code 128, are vials this version too?
                if r:
                    self._logger.debug(f"Barcode detected by CVFrameProcessor!")
                    # https://docs.opencv.org/3.4/dc/da5/tutorial_py_drawing_functions.html
                    self._barcode_polys = np.array([[p.x, p.y] for p in r[0][3]], np.int32)
                    self._barcode_polys = [self._barcode_polys.reshape((len(self._barcode_polys), 1, 2))]


                    _barcode = r[0][0].decode('utf-8')
                    self.BARCODE_THROTTLE_COUNT += 1
                    if self.BARCODE_THROTTLE_COUNT > _throttle_scan_for_n or _barcode != self._last_barcode_scanned:
                        array = self._apply_barcode_polys_to_img(array, self._barcode_polys)
                        self.barcodeDetected.emit(_barcode, array)  # notify UI that we scanned a barcode
                        self.BARCODE_THROTTLE_COUNT = 0  # reset throttle when we emit a barcode
                        self._logger.debug(f"Barcode {_barcode} detected by CVFrameProcessor and emitted unthrottled!")
                    else:
                        self._logger.debug(f"Barcode detection not emitted due to throttle.")

                    self._last_barcode_scanned = _barcode
                else:
                    self._barcode_polys = None

        except Exception as e:
            pass

        finally:
            self._barcode_frames_scanned += 1
            return array

    def _gaussian_blur(self, array: np.ndarray) -> np.ndarray:
        """
        use me while processing array frame to add blur
        """
        return cv2.GaussianBlur(array, (0, 0), 25)

    def _pencil_sketch(self, array: np.ndarray) -> np.ndarray:
        """
        https://subscription.packtpub.com/book/data/9781785282690/1/ch01lvl1sec10/creating-a-black-and-white-pencil-sketch
        :param array: cv image array
        :return: cv image array, with pencial scketch effect
        """
        _gray_img = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
        _gaussian = cv2.GaussianBlur(_gray_img, (21, 21), 0, 0)
        return cv2.divide(_gray_img, _gaussian, scale=256.0)


class CamControls(QObject):

    """
    define controls for camera/multimedia device for app here.  Facilitate processing of frames from
    camera to processor, and capture of still frames.
    """

    cameraChanged = Signal()  # tell ui that camera device has changed
    cameraStatusChanged = Signal(bool, arguments=['status'])
    barcodeDetected = Signal(str, arguments=['barcode'])  # notify if we have detected a new barcode
    videoFrameProcessed = Signal("QVariant", arguments=['new_frame'])  # send frame from processor to final sink
    controlsChanged = Signal()  # for now just using generic signal anytime control (e.g. flash, focus etc) changes
    flipCamera = Signal()
    cameraResolutionChanged = Signal()
    barcodeNotFound = Signal(str, arguments=['barcode'])
    barcodeFound = Signal(str, arguments=['barcode'])


    def __init__(self, db, app=None, parent=None):
        super().__init__(parent)
        self._app = app
        self._db = db
        self._logger = Logger.get_root()

        # things we need from multimedia for camera/capture
        self._devices = QMediaDevices()  # list our available devices here
        _state_cam = self._app.state.get_state_value('Current Camera')
        self._camera = self._get_camera_by_name(_state_cam)
        self._is_camera_running = False
        self._image_capture = QImageCapture()

        self._capture_session = QMediaCaptureSession()
        self._capture_session.setCamera(self._camera)
        self._capture_session.setImageCapture(self._image_capture)
        self._source_sink = QVideoSink()  # feed frames from camera to this sink, then emit to processor
        self._target_sink = None  # placeholder, we'll set the sink associated with our QML video output to this var
        self._video_output = None
        self._capture_session.setVideoSink(self._source_sink)

        # frame processing worker/thread setup
        self._frame_processor = VideoFrameProcessor()  # process frames here, runs CVFrameWorker on internal thread
        self._cv_frame_worker = CVFrameWorker()  # worker to use opencv to take frames from source sink
        self._cv_frame_worker.isProcessingNecessary.connect(self._toggle_frame_processor)  # if not necessary, turn off
        self._frame_processor.setWorker(self._cv_frame_worker)  # connect processor and worker

        # by default, dont hook up frame processor: sourceSink --> processor --> targetSink
        self._capture_session.videoSink().videoFrameChanged.connect(self._display_frame)  # pipe frame from source to target

        # for some reason when I call self._camera.start / stop directly, this doesnt work
        self._cv_frame_worker.feedFrozen.connect(self.stopCamera)
        self._cv_frame_worker.feedUnfrozen.connect(self.startCamera)
        self._cv_frame_worker.barcodeDetected.connect(lambda bc, frame: self._set_detected_barcode(bc, frame))
        self._cv_frame_worker.sendFrameToDisplay.connect(lambda frame: self._display_frame(array2qvideoframe(frame)))
        self._camera.activeChanged.connect(self._set_camera_status)

        # custom control variables, store them in state table and load on start
        self._is_barcode_scanner_on = None
        self.isBarcodeScannerOn = self._app.state.get_state_value('Barcode Scanner On') == 'True'
        self._is_taxon_scanner_on = None
        self.isTaxonScannerOn = self._app.state.get_state_value('Taxon Scanner On') == 'True'
        self._is_torch_on = None
        self.isTorchOn = self._app.state.get_state_value('Torch On') == 'True'
        self._cur_flash_mode = None
        self.curFlashMode = self._app.state.get_state_value('Flash Mode')
        self._cur_focus_mode = None
        self.curFocusMode = self._app.state.get_state_value('Focus Mode')
        self._detected_barcode = None

    def _toggle_frame_processor(self, turn_on):
        """
        hooked up to cv_frame_processor, if a config changes in that class that makes processing
        pointless, we turn it off, else turn on.
        :param turn_on: boolean, should we process frames?
        """
        self._logger.debug(f"Toggling frame processor to {turn_on}")
        if turn_on:
            self.connectFrameProcessor()
        else:
            self.disconnectFrameProcessor()

    @Slot()
    def disconnectFrameProcessor(self):
        """
        break slot/signal connection that passes frames to processor, and
        make connection direct from sourceSink --> targetSink
        """
        self._logger.debug("Disconnecting frame processor, piping frames direct to UI sink...")
        try:
            self._capture_session.videoSink().videoFrameChanged.disconnect(self._frame_processor.processVideoFrame)
        except RuntimeError: # if not yet connected, thats ok
            self._logger.debug(f"frameProcessor not yet connected, unable to disconnect.")

    @Slot()
    def connectFrameProcessor(self):
        """
        build slot/signal connection that passes frames to processor, and
        disconnect direct connection from sourceSink --> targetSink
        """
        self._logger.debug("Disconnecting frame processor, piping frames direct to UI sink...")
        self._capture_session.videoSink().videoFrameChanged.connect(self._frame_processor.processVideoFrame)  # pass frame from session to processor

    def startCamera(self):
        self._camera.start()

    def stopCamera(self):
        self._camera.stop()

    @Property(bool, notify=cameraStatusChanged)
    def isCameraRunning(self):
        return self._is_camera_running

    def _set_camera_status(self, status):
        if self._is_camera_running != status:
            self._is_camera_running = status
            self.cameraStatusChanged.emit(status)

    @Slot()
    def clearBarcode(self):
        self._set_detected_barcode(None)
        self._cv_frame_worker.reset_last_barcode()

    @Property(QObject)
    def camera(self) -> QCamera:
        return self._camera

    @camera.setter
    def camera(self, new_camera: QCamera):
        if self._camera != new_camera:

            _do_restart = self._camera.isActive()
            self._camera = new_camera

            if not isinstance(self._camera, QCamera):
                self._app.state.set_state_value('Current Camera', None)
                self._logger.warning(f"Current camera is not of type QCamera: {self._camera}")
                return

            self._app.state.set_state_value('Current Camera', new_camera.cameraDevice().description())
            self._capture_session.setCamera(self._camera)

            if _do_restart:
                self._camera.start()
                self.flipCamera.emit()

            self.cameraChanged.emit()
            self._view_camera_features()

    @Property(QObject, constant=True)
    def imageCapture(self):
        return self._image_capture

    @Property(str, notify=cameraChanged)
    def curCameraName(self) -> str:
        return self._camera.cameraDevice().description()

    @Property("QVariant", notify=cameraResolutionChanged)
    def curCameraResolution(self):
        return self._cur_camera_resolution

    @curCameraResolution.setter
    def curCameraResolution(self, new_res):
        print(f"New res ({type(new_res)}): {new_res}")
        self._logger.info(f"Setting camera resolution to {new_res}")
        if isinstance(new_res, QJSValue):
            print(f"Converting res to variant!")
            new_res = new_res.toVariant()

        print(f"New res after conversion: {new_res}")
        self._cur_camera_resolution = new_res
        try:
            _fmt = self._camera.cameraFormat()
            _fmt.resolution().setWidth(new_res['width'])
            _fmt.resolution().setHeight(new_res['height'])
            self._camera.setCameraFormat(_fmt)
        except Exception as e:
            self._logger.error(f"Unable to set camera resolution to {new_res}: {e}")

    def _view_camera_formats(self):
        print(f"Our current fmt is {self._camera.cameraFormat().resolution()}")
        for fmt in self._camera.cameraDevice().videoFormats():
            print(f"Camera option = {fmt.resolution()}")
            # print(fmt.resolution())

    def _view_camera_features(self):
        """
        print out a bunch of info about what the active camera can do
        """
        self._logger.info(
            f'''
            ------------------------------------------------------------------------------------------
                Camera {self._camera.cameraDevice().description()} supports the following features:

                Flash On: {self._camera.isFlashModeSupported(QCamera.FlashOn)}
                Auto Flash: {self._camera.isFlashModeSupported(QCamera.FlashAuto)}
                Torch: {self._camera.isTorchModeSupported(QCamera.TorchOn)}
                Auto Focus: {self._camera.isFocusModeSupported(QCamera.FocusModeAuto)}
                Manual focus: {self._camera.isFocusModeSupported(QCamera.FocusModeManual)}

                Barcode Exposure Mode: {self._camera.isExposureModeSupported(QCamera.ExposureBarcode)}
                Beach Exposure Mode: {self._camera.isExposureModeSupported(QCamera.ExposureBeach)}
                Manual Exposure Mode: {self._camera.isExposureModeSupported(QCamera.ExposureManual)}
                Auto Exposure Mode: {self._camera.isExposureModeSupported(QCamera.ExposureAuto)}

                {self._camera.supportedFeatures}
            ------------------------------------------------------------------------------------------
            '''
        )

    def _get_camera_by_name(self, device_name: str):
        try:
            return QCamera([d for d in self._devices.videoInputs() if d.description() == device_name][0])
        except IndexError:
            self._logger.warning(f"Unable to find camera device called: {device_name}, returning default.")
            return QCamera(QMediaDevices.defaultVideoInput())

    @Slot()
    def toggleCamera(self):
        """
        allows us to get the next item in list of devices.  If at the end of the list, wrap around and
        select the first one.  If only one item, do nothing.
        Should also be able to plug in device, then retoggle.

        Use camera setter to trigger necessary prop updates/signalling
        """
        if not self._devices.videoInputs() or not self._camera:
            self._logger.warning(f"Unable to get next device, none available")
            return

        if len(self._devices.videoInputs()) == 1:
            self._logger.info(f"Only one video input device available")
            self._view_camera_features()
            self._view_camera_formats()
            return

        try:

            cur_index = [d.description() for d in self._devices.videoInputs()].index(self._camera.cameraDevice().description())
            self.camera = QCamera(self._devices.videoInputs()[cur_index+1])

        except ValueError as e:
            self._logger.error(f"Error occurred while trying to toggle camera device: {e}")
            return

        except IndexError:
            self._logger.info("Setting camera to default device")
            self.camera = QCamera(self._devices.videoInputs()[0])

    def _display_frame(self, frame: QVideoFrame):
        """
        pass frame from processor to target sink associated with VideoOutput for final display
        :param frame: QVideoFrame
        """
        self._target_sink.setVideoFrame(frame)

    def _set_detected_barcode(self, new_barcode: str, barcode_polys=[]):
        """
        hook this up to barcodeDetected signal, transform, then emit if different
        :param new_barcode: str, unformatted barcode str read from image
        :return: str, formatted with dashes if necessary
        """
        if len(barcode_polys):

            self._display_frame(array2qvideoframe(barcode_polys))

        bc = self.transform_barcode_tag(new_barcode) if new_barcode else new_barcode
        self._logger.debug(f"barcode detected: {bc}")
        if self._detected_barcode != bc:
            self._logger.debug(f"Detected barcode is new: {bc}")
            self._detected_barcode = bc
            self.barcodeDetected.emit(bc)

    @Property("QVariant", notify=barcodeDetected)
    def detectedBarcode(self):
        return self._detected_barcode

    @Property(QObject)
    def targetSink(self) -> QVideoSink:
        return self._target_sink

    @targetSink.setter
    def targetSink(self, new_video_sink: QVideoSink):
        self._target_sink = new_video_sink

    def transform_barcode_tag(self, barcode_str: str) -> str:
        """
        since barcode doesn't store hyphens from whole specimen tags, we add them back in:
        2022008900067006 --> 2022-008-900-067-006
        :param barcode_str: value read from barcode vial/tag
        :return: reformatted str
        """
        if len(barcode_str) == 16 and barcode_str[:2] == '20':  # loosely make sure its a whole specimen tag...
            _yr = barcode_str[:4]
            _other = barcode_str[4:]
            self._logger.debug(f"Barcode transformed, before = {barcode_str}")
            barcode_str = _yr + '-' + '-'.join(f'{_other[i:i + 3]}' for i in range(0, len(_other), 3))
            self._logger.debug(f"Barcode transformed, after = {barcode_str}")

        return barcode_str

    @Slot()
    def freezeFrame(self):
        """
        send request to stop frame feed, but do something to last frame first
        """
        self._cv_frame_worker.request_freeze_frame()

    @Slot()
    def unfreezeFrame(self):
        """
        send request to restart frame feed, and disable effect we put in place for last frame before freeze
        """
        self._cv_frame_worker.request_unfreeze()

    @Property("QVariant", notify=cameraChanged)
    def isFlashSupported(self):
        return self._camera.isFlashModeSupported(QCamera.FlashOn)

    @Property("QVariant", notify=cameraChanged)
    def isTorchSupported(self):
        return self._camera.isTorchModeSupported(QCamera.TorchOn)

    @Property("QVariant", notify=cameraChanged)
    def isFocusModeSupported(self):
        return self._camera.isFocusModeSupported(QCamera.FocusModeAuto) and self._camera.isFocusModeSupported(QCamera.FocusModeManual)

    @Property(bool, notify=controlsChanged)
    def isBarcodeScannerOn(self) -> bool:
        return self._is_barcode_scanner_on

    @isBarcodeScannerOn.setter
    def isBarcodeScannerOn(self, new_status: bool):
        if self._is_barcode_scanner_on != new_status:
            self._is_barcode_scanner_on = new_status
            self._cv_frame_worker.enable_barcode_scanner(new_status)
            self._app.state.set_state_value('Barcode Scanner On', str(new_status))
            self.controlsChanged.emit()

    @Property(bool, notify=controlsChanged)
    def isTaxonScannerOn(self) -> bool:
        return self._is_taxon_scanner_on

    @isTaxonScannerOn.setter
    def isTaxonScannerOn(self, new_status: bool):
        if self._is_taxon_scanner_on != new_status:
            self._is_taxon_scanner_on = new_status
            self._app.state.set_state_value('Taxon Scanner On', str(new_status))
            self.controlsChanged.emit()

    @Property(bool, notify=controlsChanged)
    def isTorchOn(self):
        return self._is_torch_on

    @isTorchOn.setter
    def isTorchOn(self, new_status):
        if self._is_torch_on != new_status:
            self._is_torch_on = new_status
            self._app.state.set_state_value('Torch On', str(new_status))
            self.controlsChanged.emit()

    @Property(int, notify=controlsChanged)
    def curFocusMode(self):
        return self._cur_focus_mode

    @curFocusMode.setter
    def curFocusMode(self, new_mode):
        if self._cur_focus_mode != new_mode:
            self._cur_focus_mode = new_mode
            # self._camera.
            self.controlsChanged.emit()

    @Property(int, notify=controlsChanged)
    def curFlashMode(self):
        return self._cur_flash_mode

    @curFlashMode.setter
    def curFlashMode(self, new_mode):
        if self._cur_flash_mode != new_mode:
            self._cur_flash_mode = new_mode
            self._camera.setFocusMode(new_mode)
            self.controlsChanged.emit()

    def _get_image_name(self, ext='jpg') -> str:
        """
        build image file name, format is {HAUL#}{VESSEL_CODE}_{CATCH DISPLAY NAME}_{PROJECT}_{BIOLABEL}.{ext}
        If null items will be ommitted
        :param ext: str, extension specified, default to jpg
        :return: str, name of image file
        """
        haul_number = self._app.data_selector.cur_haul_num
        vessel_code = Utils.get_vessel_code_from_haul(haul_number)
        vessel_haul = vessel_code + haul_number[-3:]
        catch_display = '_' + Utils.scrub_str_for_file_name(self._app.data_selector.cur_catch_display) if self._app.data_selector.cur_catch_display else ''
        project = '_' + Utils.scrub_str_for_file_name(self._app.data_selector.cur_project_name) if self._app.data_selector.cur_project_name else ''
        bio_label = '_' + self._app.data_selector.cur_bio_label if self._app.data_selector.cur_bio_label else ''
        return f"{vessel_haul}{catch_display}{project}{bio_label}.{ext}"

    def _increment_file_path(self, full_path, i=1):
        """
        append _i to the file path, where i is the next available if we have a duplicate file
        :param full_path: full path to file
        :param i: int, starting integer we attempt to append to file
        :return: str, new full path to image with next available i
        """

        path, ext = os.path.splitext(full_path)
        pattern = re.compile(f'_img\\d+{ext}$')
        if not pattern.search(full_path):
            # if filename doesnt have img# at the end, put it there
            full_path = f"{path}_img{i}{ext}"
        else:
            # if path is already incremented, replace increment with current val
            full_path = re.sub(pattern, f'_img{i}{ext}', full_path)

        if not os.path.exists(full_path):
            return full_path
        else:
            i += 1
            return self._increment_file_path(full_path, i)

    @Slot()
    def captureImage(self):
        """
        async image capture, on success the imageSaved signal is emitted
        https://doc.qt.io/qtforpython-6/PySide6/QtMultimedia/QImageCapture.html#PySide6.QtMultimedia.PySide6.QtMultimedia.QImageCapture.imageSaved
        """
        img_name = self._get_image_name()
        full_path = Path(self._increment_file_path(os.path.join(IMAGES_DIR, img_name))).as_posix()
        img_result = self._image_capture.captureToFile(full_path)
        self._logger.info(f"Capturing image to {full_path}, capture result={img_result}")


