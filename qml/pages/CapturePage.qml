import QtQuick.Controls 6.3
import QtQuick 2.15
import Qt5Compat.GraphicalEffects
import QtMultimedia 6.3
import QtQuick.Layouts 6.3
import 'qrc:/controls'
import 'qrc:/components'



Item {
    id: capturePage

    property alias lvThumbnails: lvThumbnails
    Component.onCompleted: {
        camControls.targetSink = videoOutput.videoSink  // make output sink the destination for our processed frames
    }
    Connections {
        target: windowMain
        function onActivePageChanged() {
            // reset lv index so that when we re-enter and select, it registers as a change
            if (windowMain.activePage.toLowerCase() !== 'capture') {
                lvThumbnails.currentIndex = -1
            }
        }
    }
    SoundEffect {
        id: clack
        source: "qrc:/sounds/clack.wav"
    }
    SoundEffect {
        id: shutter
        source: "qrc:/sounds/shutter.wav"
    }
    SoundEffect {
        id: shotgun
        source: "qrc:/sounds/shotgun.wav"
    }

    YesNoDialog {
        id: dlgBarcodeNotFound
        title: "Scanned Barcode Not Found"
        acceptButtonText: 'Refresh &\nRetry'

        property string missedBarcode;  // stash barcode value here for re-try on search
        property bool awaitingRepull: false;  // use to indicate that on our next pull we want to try selection
        onDeclined: this.close()  // do nothing on cancel

        /*
        How this dialog functions

        1.) Barcode is scanned and not found, dialog opens
        2.) User selects retry, barcode var and is waiting bool flag are set, backdeck retrieval thread starts
        3.) Backdeck retrieval thread results come back, onBackdeckPullResults signal is retrieved
        4.) on success, and with queued flags, we re-attempt data selector barcode select
        */

        onAccepted: {
            this.close()
            awaitingRepull = true;  // true indicates that, when getBackdeckBios finishes, we re-try search
            dataSelector.getBackdeckBios();  // threaded re-pull of backdeck data is async
        }
        Connections {
            target: dataSelector
            function onBarcodeSearched(success, barcode) {
                if (!success) {  // if we search and fail, open this dialog
                    dlgBarcodeNotFound.missedBarcode = barcode
                    dlgBarcodeNotFound.lblMessage.text = "Barcode " + barcode + " not found."
                    dlgBarcodeNotFound.lblAction.text = "Refresh data from backdeck machine and retry?"
                    dlgBarcodeNotFound.open()
                } else {
                    rectDataSelection.flashAllMenus()  // on success, flash TODO: play sound?
                }
            }
            function onBackdeckPullResults(success, msg, rows) {
                // this only attempts a re-select of barcode if awaitingRepull and missedBarcode were originally set
                if (success && dlgBarcodeNotFound.awaitingRepull && dlgBarcodeNotFound.missedBarcode) {
                    dlgBarcodeNotFound.awaitingRepull = false;
                    dataSelector.selectBarcode(dlgBarcodeNotFound.missedBarcode)
                }
            }
        }
    }
    Connections {
            target: camControls
            function onBarcodeDetected(barcode) {
                if (barcode) shotgun.play()
            }
        }
    Rectangle {
        id: rectBg
        color: appStyle.elevatedSurface_L5
        border.color: "#00000000"
        anchors.fill: parent
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 0
        anchors.topMargin: 5

        Rectangle {
            id: rectImgArea
            color: appStyle.elevatedSurface_L5
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: rectDataSelection.bottom
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.topMargin: 0
            anchors.rightMargin: 0
            anchors.leftMargin: 0
            radius: 8
            FramCamButton {
                id: btnCapture
                iconSource: 'qrc:/svgs/box_target.svg'
                iconColor: enabled ? appStyle.accentColor : "gray"
                backgroundColor: "#eeeeee"  // almost white regardless of color scheme
                borderColor: appStyle.iconColor
                disabledBackgroundColor: appStyle.elevatedSurface_L9
                borderWidth: 5
                radius: 20
                enabled: camControls.isCameraRunning && lvThumbnails.currentIndex === -1

                anchors {
                    right: parent.right
                    left: rectImgPreview.right
                    top: rectThumbnails.bottom
                    bottom: parent.bottom
                    leftMargin: 15
                    rightMargin: 15
                }
                onClicked: {
                    if (!dataSelector.cur_haul_num) {
                        dataSelector.requireHaulSelection()
                        return;
                    }
                    camControls.captureImage()
                    shutter.play()
                }
            }
            Rectangle {
                id: rectImgPreview
                //visible: false
                color: appStyle.elevatedSurface_L7
                border.color: appStyle.iconColor
                border.width: 5
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                //anchors.centerIn: parent
                anchors.rightMargin: 175  // make room for thumbnails here
                radius: 8
                clip: true

                property bool flipped: false;

                Connections {
                    target: camControls
                    function onFlipCamera() {
                        rectImgPreview.flipped = !rectImgPreview.flipped
                    }
                }
                transform: Rotation {
                    axis.x: 1; axis.y: 0; axis.z: 0
                    angle: rectImgPreview.flipped ? 360 : 0
                    origin.x: rectImgPreview.width / 2; origin.y: rectImgPreview.height / 2
                    Behavior on angle {
                        NumberAnimation { duration: 800 }
                    }
                }

                Image {
                    id: image
                    width: 100
                    height: 100
                    anchors.verticalCenter: parent.verticalCenter
                    source: "qrc:/svgs/eye_closed.svg"
                    anchors.horizontalCenter: parent.horizontalCenter

                    fillMode: Image.PreserveAspectFit
                    layer {
                        enabled: true
                        effect: ColorOverlay {
                            color: appStyle.iconColor
                        }
                    }
                }
                VideoOutput {
                    id: videoOutput
                    anchors.fill: parent
                    anchors.leftMargin: 5
                    anchors.rightMargin: 5
                    anchors.topMargin: 5
                    anchors.bottomMargin: 5
                    fillMode: VideoOutput.PreserveAspectCrop
                }

                Rectangle {
                    id: rectControls
                    y: 325
                    height: 100
                    radius: 8
                    color: appStyle.elevatedSurface_L5
                    border.color: appStyle.iconColor
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.leftMargin: 0
                    anchors.bottomMargin: 0
                    anchors.rightMargin: 0

                    PropertyAnimation{
                        id: animationControls
                        target: rectControls
                        property: "height"
                        to: if(rectControls.height === 100) return 0; else return 100;
                        duration:400
                        easing.type: Easing.InOutQuint
                    }

                    Rectangle {
                        id: rectMoveControls
                        width: 100
                        height: 40
//                        opacity: 0.5
                        color: "#00000000"

                        anchors {
                            top: parent.top
                            topMargin: -40
                            left: parent.left
                        }

                        Connections {
                            target: animationControls
                            function onFinished() {
                                if (rectControls.height > 75) {
                                    //rectMoveControls.anchors.topMargin = 0
                                    imgMoveControls.source = "qrc:/svgs/collapse_down.svg"
                                } else {
                                    //rectMoveControls.anchors.topMargin = -40
                                    imgMoveControls.source = "qrc:/svgs/expand_up.svg"
                                }
                            }
                        }
                        Image {
                            id: imgMoveControls
                            anchors.fill: parent
                            source: "qrc:/svgs/collapse_down.svg"
                            fillMode: Image.PreserveAspectFit
                        }

                        ColorOverlay {
                            source: imgMoveControls
                            color: appStyle.primaryColorAltDark
                            anchors.top: imgMoveControls.top
                            anchors.bottom: imgMoveControls.bottom
                            antialiasing: true
                            width: imgMoveControls.width
                            height: imgMoveControls.height
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: animationControls.running = true
                        }
                    }

                    Row {
                        id: rowControls
                        anchors.fill: parent
                        anchors.rightMargin: btnCapture.width + 10
                        anchors.leftMargin: 15
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 20
                        anchors.top: parent.top
                        anchors.topMargin: 5

                        property int buttonHeight: 90
                        property int buttonWidth: 100

                        FramCamButton {
                            id: btnChangeCamera
                            implicitWidth: rowControls.buttonWidth
                            implicitHeight: rowControls.buttonHeight
                            radius: 20
                            onClicked: camControls.toggleCamera()
                            iconSource: 'qrc:/svgs/change_camera.svg'
                        }
                        FramCamButton {
                            id: btnStartCamera
                            implicitWidth: rowControls.buttonWidth
                            implicitHeight: rowControls.buttonHeight
                            radius: 20
                            iconSource: checked ? 'qrc:/svgs/video_on.svg' : 'qrc:/svgs/video_off.svg'
                            checkable: true
                            checked: camControls.isCameraRunning
                            onClicked: {
                                if(checked) {
                                    camControls.unfreezeFrame()
                                } else {
                                    camControls.freezeFrame()
                                }
                            }
                        }
                        FramCamButton {
                            id: btnFlash
                            implicitWidth: rowControls.buttonWidth
                            implicitHeight: rowControls.buttonHeight
                            radius: 20
                            iconSource: checked ? 'qrc:/svgs/flash_on.svg' : 'qrc:/svgs/flash_off.svg'
                            checkable: true
                            visible: camControls.isFlashSupported
                        }
                        FramCamButton {
                            id: btnTorch
                            implicitWidth: rowControls.buttonWidth
                            implicitHeight: rowControls.buttonHeight
                            radius: 20
                            iconSource: checked ? 'qrc:/svgs/torch_on.svg' : 'qrc:/svgs/torch_off.svg'
                            checkable: true
                            visible: camControls.isTorchSupported
                        }
                        FramCamButton {
                            id: btnAutofocus
                            implicitWidth: rowControls.buttonWidth
                            implicitHeight: rowControls.buttonHeight
                            radius: 20
                            iconSource: 'qrc:/svgs/autofocus.svg'
                            checkable: true
                            visible: camControls.isFocusModeSupported
                        }
                        FramCamButton {
                            id: btnBarcodeScan
                            implicitWidth: rowControls.buttonWidth
                            implicitHeight: rowControls.buttonHeight
                            radius: 20
                            iconSource: 'qrc:/svgs/barcode.svg'
                            checkable: true
                            checked: camControls.isBarcodeScannerOn
                            onClicked: {
                                camControls.isBarcodeScannerOn = checked
                            }
                        }
                        FramCamButton {
                            id: btnTaxonScan
                            implicitWidth: rowControls.buttonWidth
                            implicitHeight: rowControls.buttonHeight
                            radius: 20
                            visible: false
                            iconSource: 'qrc:/svgs/kraken.svg'
                            checkable: true
                            onClicked: {
                                if (checked) {
                                    camControls.testEmit()
                                }
                            }
                        }

                    }
                }
            }
            ImageEditorArea {
                id: editBar
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: rectThumbnails.left
                width: 0
                SequentialAnimation {
                    id: animationEditBar
                    // disable listview to prevent additional cliking while menu pops out, then enable again
                    PropertyAction { property: "enabled"; target: lvThumbnails; value: false }
                    // if, before animating, editBar width > 0, set to invisible
                    PropertyAnimation { property: "visible"; target: editBar.keyboard; to: if(editBar.width !== 0) return false; else return true}
                    PropertyAnimation{
                        target: editBar
                        property: "width"
                        to: if(editBar.width == 0) return rectImgPreview.width; else return 0;
                        duration: 300
                        easing.type: Easing.InOutQuint
                    }
                    //if, after animating, editBar.width > 0, set to visible
                    PropertyAnimation { property: "visible"; target: editBar.keyboard; to: if(editBar.width !== 0) return true; else return false}
                    PropertyAction { property: "enabled"; target: lvThumbnails; value: true }
                }
                Connections {
                    target: imageManager.imagesProxy
                    function onProxyIndexChanged(new_proxy_index) {
                        console.info("OUR IMAGES PROXY INDEX CHANGED TO " + new_proxy_index)
                        var modelIx = imageManager.imagesProxy.sourceIndex

                        if (new_proxy_index > -1 && editBar.width > 0) {
                            // if we still select an image and edit bar is already out, dont re-animate
                            return;
                        } else {
                            animationEditBar.running = true;
                        }
                    }
                }
            }
            Rectangle {
                id: rectThumbnails
                y: 0
                color: appStyle.elevatedSurface_L5
                anchors.left: rectImgPreview.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 0
                anchors.bottomMargin: 100

                ListView {
                    id: lvThumbnails
                    x: 0
                    y: 0
                    clip: true
                    anchors.fill: parent
                    anchors.leftMargin: 10
                    anchors.rightMargin: 10
                    anchors.topMargin: 20
                    orientation: ListView.Vertical
                    spacing: 10
                    model: imageManager.imagesProxy
                    currentIndex: -1
                    onCurrentIndexChanged: {
                        model.proxyIndex = currentIndex
                    }
                    Connections {
                        target: imageManager.imagesProxy
                        function onSelectIndexInUI(proxy_index) {
                            lvThumbnails.currentIndex = proxy_index
                        }
                    }
                    Connections {
                        target: imageManager.imagesModel
                        function onSelectIndexInUI(new_index) {
                            var proxyRow = imageManager.imagesProxy.getProxyRowFromSource(new_index)
                            lvThumbnails.currentIndex = proxyRow
                        }
                    }
                    delegate: Column {
                        Image {
                            id: imgThumbnail
                            source: "file:///" + model.full_path
                            width: lvThumbnails.width - 30
                            anchors {
                                right: parent.right
                                rightMargin: index === imageManager.imagesProxy.proxyIndex ? 0 : -15
                            }
                            fillMode: Image.PreserveAspectFit
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    // clicking an already active image clears selection
                                    if (index === imageManager.imagesProxy.proxyIndex) {
                                        lvThumbnails.currentIndex = -1
                                    } else {
                                        clack.play()
                                        lvThumbnails.currentIndex = index
                                    }
                                }
                            }
                            Colorize {
                                anchors.fill: imgThumbnail
                                source: imgThumbnail
                                hue: 0.0
                                saturation: 0
                                lightness: 0
                                visible: index !== imageManager.imagesProxy.proxyIndex
                            }
                        }
                        Label {
                            id: imgLabel
                            text: model.bio_label ? model.catch_display_name + '\n' +model.bio_label : model.catch_display_name ? model.catch_display_name : "Haul# " + model.haul_number
                            font.pixelSize: 8
                            font.bold: true
                            font.family: 'roboto'
                            color: appStyle.secondaryFontColor
                            anchors.left: rectUnderline.left
                        }
                        Rectangle {
                            id: rectUnderline
                            height: index === imageManager.imagesProxy.proxyIndex ? 3 : 1
                            width: imgThumbnail.width - 10
                            color: index === imageManager.imagesProxy.proxyIndex ? appStyle.primaryColor : appStyle.secondaryFontColor
                            anchors.topMargin: 10
                            anchors.left: imgThumbnail.left
                            //anchors.leftMargin: imageManager.imagesProxy.proxyIndex === index ? -10 : 0

                        }
                    }
                    add: Transition {
                        PropertyAction { property: "transformOrigin"; value: Item.Top}
                        NumberAnimation { property: "opacity"; from: 0; to: 1.0; duration: 200 }
                        NumberAnimation { property: "scale"; from: 0; to: 1.0; duration: 200 }
                    }
                    displaced: Transition {
                        PropertyAction { properties: "opacity, scale"; value: 1 }  // incase a newly added image becomes displaced
                        NumberAnimation { properties: "x,y"; duration: 200 }
                    }
                    remove: Transition {
                        PropertyAction { property: "transformOrigin"; value: Item.Bottom}
                        NumberAnimation { property: "opacity"; from: 1.0; to: 0; duration: 200 }
                        NumberAnimation { property: "scale"; from: 1.0; to: 0; duration: 200 }
                    }
                }
            }
            ListModel {
                id: imagePaths
            }
        }
        DataSelectorBar {
            id: rectDataSelection
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0
        }
    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:0.66;height:480;width:800}
}
##^##*/
