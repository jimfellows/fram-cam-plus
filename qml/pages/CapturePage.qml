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
                iconColor: appStyle.elevatedSurface_L2
                backgroundColor: appStyle.secondaryFontColor
                borderColor: appStyle.iconColor
                disabledBackgroundColor: appStyle.elevatedSurface_L9
                borderWidth: 5
                radius: 20
                enabled: camControls.camera.active && lvThumbnails.currentIndex === -1

                anchors {
                    right: parent.right
                    left: rectImgPreview.right
                    top: rectThumbnails.bottom
                    bottom: parent.bottom
                    leftMargin: 15
                    rightMargin: 15
                }
                onClicked: {
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
                anchors.rightMargin: 175  // make room for thumbnails here
                radius: 8
                clip: true

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
                        anchors.top: parent.top
                        anchors.topMargin: -40
                        //anchors.left: rowControls.right
                        anchors.horizontalCenter: parent.horizontalCenter

                        Connections {
                            target: animationControls
                            function onFinished() {
                                if (rectControls.height > 75) {
                                    //rectMoveControls.anchors.topMargin = 0
                                    imgMoveControls.source = "qrc:/svgs/down_arrow.svg"
                                } else {
                                    //rectMoveControls.anchors.topMargin = -40
                                    imgMoveControls.source = "qrc:/svgs/up_arrow.svg"
                                }
                            }
                        }
                        Image {
                            id: imgMoveControls
                            anchors.fill: parent
                            source: "qrc:/svgs/down_arrow.svg"
                            fillMode: Image.PreserveAspectFit
                        }

                        ColorOverlay {
                            source: imgMoveControls
                            color: appStyle.primaryFontColor
                            opacity: 0.75
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
                        anchors.leftMargin: 10
                        anchors.topMargin: 10
                        //anchors.verticalCenter: parent.verticalCenter
                        spacing: 20
                        FramCamButton {
                            id: btnChangeCamera
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            onClicked: camControls.toggleCamera()
                            iconSource: 'qrc:/svgs/change_camera.svg'
                        }
                        FramCamButton {
                            id: btnStartCamera
                            width: 75
                            height: 75
                            radius: 20
                            iconSource: checked ? 'qrc:/svgs/video_on.svg' : 'qrc:/svgs/video_off.svg'
                            checkable: true
                            checked: camControls.camera.active
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
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            iconSource: checked ? 'qrc:/svgs/flash_on.svg' : 'qrc:/svgs/flash_off.svg'
                            checkable: true
                            visible: camControls.isFlashSupported
                        }
                        FramCamButton {
                            id: btnTorch
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            iconSource: checked ? 'qrc:/svgs/torch_on.svg' : 'qrc:/svgs/torch_off.svg'
                            checkable: true
                            visible: camControls.isTorchSupported
                        }
                        FramCamButton {
                            id: btnAutofocus
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            iconSource: 'qrc:/svgs/autofocus.svg'
                            checkable: true
                            visible: camControls.isFocusModeSupported
                        }
                        FramCamButton {
                            id: btnBarcodeScan
                            implicitWidth: 75
                            implicitHeight: 75
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
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            iconSource: 'qrc:/svgs/kraken.svg'
                            checkable: true
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

                        if (modelIx > -1) editBar.imageSource = imageManager.imagesModel.getData(modelIx, 'full_path')

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
                color: appStyle.surfaceColor
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
                        function onSelectProxyIndexInUI(proxy_index) {
                            console.info("onSelectProxyIndexInUI received: " + proxy_index)
                            lvThumbnails.currentIndex = proxy_index
                        }
                    }
                    Connections {
                        target: imageManager.imagesModel
                        function onSendIndexToProxy(new_index) {
                            console.info("onSendIndexToProxy index received: " + new_index)
                            var proxyRow = imageManager.imagesProxy.getProxyRowFromSource(new_index)
                            lvThumbnails.currentIndex = proxyRow
                        }
                    }
                    delegate: Column {
                        anchors.left: lvThumbnails.left
                        anchors.right: lvThumbnails.right
                        Image {
                            id: imgThumbnail
                            source: "file:///" + model.full_path
                            width: lvThumbnails.width - 30
                            anchors.right: parent.right
                            //width: imageManager.imagesProxy.proxyIndex === index ? lvThumbnails.width : lvThumbnails.width - 30
                            fillMode: Image.PreserveAspectFit
                            //Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                            layer.effect: DropShadow {
                                verticalOffset: 0
                                horizontalOffset: 0
                                radius: 20
                                color: "lightgray"
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    console.info("Image clicked at index " + index)
                                    // clicking an already active image clears selection
                                    if (index === imageManager.imagesProxy.proxyIndex) {
                                        console.info("CLICK: Clicked image already selected, deselecting...")
                                        lvThumbnails.currentIndex = -1
                                    } else {
                                        clack.play()
                                        console.info("CLICK: Selecting new image at index " + index)
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
                            text: model.bio_label ? model.display_name + '\n' +model.bio_label : model.display_name ? model.display_name : "Haul# " + model.haul_number
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
