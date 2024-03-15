import QtQuick.Controls 6.3
import QtQuick 2.15
import Qt5Compat.GraphicalEffects
import QtMultimedia 6.3

import './qml/controls'
import 'qrc:/qml'



Item {
    id: capturePage

    property alias lvThumbnails: lvThumbnails
    Component.onCompleted: {
        console.info("-----------------------------------------------------------------------")
        camera_manager.targetSink = videoOutput.videoSink
        console.info("-----------------------------------------------------------------------")
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
            target: camera_manager
            function onBarcodeDetected(barcode) {
                shotgun.play()
            }
        }
    Rectangle {
        id: rectBg
        color: appstyle.elevatedSurface_L5
        border.color: "#00000000"
        anchors.fill: parent
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 5
        anchors.topMargin: 5

        Rectangle {
            id: rectImgArea
            color: appstyle.elevatedSurface_L5
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: rectDataSelection.bottom
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.topMargin: 0
            anchors.rightMargin: 0
            anchors.leftMargin: 0

            Rectangle {
                id: rectImgPreview
                //visible: false
                color: appstyle.elevatedSurface_L7
                border.color: appstyle.iconColor
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.rightMargin: 150
                radius: 8

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
                            color: appstyle.accentColor
                        }
                    }
                }
                VideoOutput {
                    id: videoOutput
                    anchors.fill: parent
                    fillMode: VideoOutput.PreserveAspectCrop
                }

                Rectangle {
                    id: rectControls
                    y: 325
                    height: 100
                    color: appstyle.elevatedSurface_L5
                    border.color: appstyle.iconColor
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
                        duration:500
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
                            onFinished: {
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
                            color: appstyle.iconColor
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
                            onClicked: camera_manager.toggle_camera()
                            anchors.verticalCenter: switchPreview.verticalCenter
                            iconSource: 'qrc:/svgs/change_camera.svg'
                        }
                        FramCamButton {
                            id: btnStartCamera
                            width: 75
                            height: 75
                            radius: 20
                            anchors.verticalCenter: switchPreview.verticalCenter
                            iconSource: checked ? 'qrc:/svgs/video_on.svg' : 'qrc:/svgs/video_off.svg'
                            checkable: true
                            onCheckedChanged: {
                                if(checked) {
                                    camera_manager.start_camera()
                                } else {
                                    camera_manager.stop_camera()
                                }
                            }
                        }
                        FramCamButton {
                            id: btnFlash
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            anchors.verticalCenter: switchPreview.verticalCenter
                            iconSource: checked ? 'qrc:/svgs/flash_on.svg' : 'qrc:/svgs/flash_off.svg'
                            checkable: true
                            //visible: camera_manager.isFlashSupported
                        }
                        FramCamButton {
                            id: btnTorch
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            anchors.verticalCenter: switchPreview.verticalCenter
                            iconSource: checked ? 'qrc:/svgs/torch_on.svg' : 'qrc:/svgs/torch_off.svg'
                            checkable: true
                            //visible: camera_manager.isTorchSupport
                        }
                        FramCamButton {
                            id: btnBarcodeScan
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            anchors.verticalCenter: switchPreview.verticalCenter
                            iconSource: 'qrc:/svgs/barcode.svg'
                            checkable: true
                            onClicked: {
                                camera_manager.isBarcodeScannerOn = checked
                            }
                        }
                        FramCamButton {
                            id: btnTaxonScan
                            implicitWidth: 75
                            implicitHeight: 75
                            radius: 20
                            anchors.verticalCenter: switchPreview.verticalCenter
                            iconSource: 'qrc:/svgs/kraken.svg'
                            checkable: true
                        }

                    }

                }
                FramCamButton {
                    id: btnCapture
                    width: 100
                    height: 100
                    iconSource: 'qrc:/svgs/record.svg'
                    iconColor: appstyle.primaryColor
                    borderColor: appstyle.iconColor
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.rightMargin: 10
                    anchors.bottomMargin: 2
                    onClicked: {
                        camera_manager.capture_image_to_file()
                        shutter.play()
                    }

                }
                /*
                Button {
                    id: btnCapture
                    x: 345
                    y: 467
                    width: 92
                    height: 82
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 10
                    anchors.rightMargin: 10
                    flat:true
                    onClicked: {
                        //console.info("BUTTON CLICKED, is camera ready?")
                        //console.info(captureSession.imageCapture.readyForCapture)
                        //var x
                        //x = captureSession.imageCapture.captureToFile('pic.jpeg')
                        //                    captureSession.imageCapture.imageSaved()
                        console.info(x)
                        camera_manager.capture_image_to_file()
                    }

                    background: Rectangle{
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.fill:parent
                        color: "#cfcfcf"
                        radius: 10
                        Image {
                            id: imgButtonCapture
                            source: 'qrc:/svgs/record.svg'
                            sourceSize.height: 40
                            sourceSize.width: 40
                            anchors.left: parent.left
                            height: 40
                            width: 40
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.horizontalCenter: parent.horizontalCenter
                            fillMode: Image.PreserveAspectFit
                            antialiasing: true
                        }

                        ColorOverlay {
                            source: imgButtonCapture
                            color: 'red'
                            //                        anchors.verticalCenter: parent.verticalCenter
                            anchors.top: imgButtonCapture.top
                            anchors.bottom: imgButtonCapture.bottom
                            //                        anchors.horizontalCenter: parent.horizontalCenter
                            antialiasing: true
                            width: imgButtonCapture.width
                            height: imgButtonCapture.height
                        }
                        Label {
                            text: 'Capture'
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 5
                            font.italic: true
                        }
                    }
                }
                */
            }
            ImageEditorBar {
                id: editBar
                anchors.top: parent.top
                //anchors.topMargin: 10
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 10
                anchors.right: rectThumbnails.left
                anchors.rightMargin: -10
                width: 0
                SequentialAnimation {
                    id: animationEditBar
                    // disable listview to prevent additional cliking while menu pops out, then enable again
                    PropertyAction { property: "enabled"; target: lvThumbnails; value: false }
                    PropertyAnimation{
                        target: editBar
                        property: "width"
                        to: if(editBar.width == 0) return rectImgPreview.width; else return 0;
                        duration: 300
                        easing.type: Easing.InOutQuint
                    }
                    PropertyAction { property: "enabled"; target: lvThumbnails; value: true }
                }
                Connections {
                    target: camera_manager.images_proxy
                    function onProxyIndexChanged(new_proxy_index) {
                        var modelIx = camera_manager.images_proxy.sourceIndex
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

                color: appstyle.elevatedSurface_L5
                anchors.left: rectImgPreview.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 0

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
                    model: camera_manager.images_proxy
                    currentIndex: -1
                    onCurrentIndexChanged: {
                        model.proxyIndex = currentIndex
                    }
                    Connections {
                        target: camera_manager.images_model
                        function onSendIndexToProxy(new_index) {
                            var proxyRow = camera_manager.images_proxy.getProxyRowFromSource(new_index)
                            lvThumbnails.currentIndex = proxyRow
                        }
                    }
                    delegate: Column {
                        Image {
                            id: imgThumbnail
                            source: "file:///" + model.full_path
                            width: lvThumbnails.width - 10
                            height: 50
                            fillMode: Image.PreserveAspectFit
                            scale: camera_manager.images_proxy.proxyIndex === index ? 1.2 : 1
                            layer.enabled: camera_manager.images_proxy.proxyIndex === index
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
                                    if (index === camera_manager.images_proxy.proxyIndex) {
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
                                visible: index === camera_manager.images_proxy.proxyIndex
                            }
                            /*
                            Connections {
                                target: camera_manager.images_proxy
                                function onIndexSetSilently(newIndex) {
                                    lvThumbnails.currentIndex = newIndex
                                }
                            }
                            */
                        }
                        Label {
                            id: imgLabel
                            text: model.display_name
                            font.pixelSize: 8
                            font.bold: true
                            font.family: 'roboto'
                            color: appstyle.secondaryFontColor
                            anchors.left: rectUnderline.left
                        }
                        Rectangle {
                            id: rectUnderline
                            height: index === camera_manager.images_proxy.proxyIndex ? 3 : 1
                            width: imgThumbnail.width - 10
                            color: index === camera_manager.images_proxy.proxyIndex ? appstyle.accentColor : appstyle.secondaryFontColor
                            anchors.topMargin: 10
                            anchors.left: imgThumbnail.left
                            anchors.leftMargin: 15

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
            /*
            Camera {
                id: camDefault
            }
            */
            /*
            FramCamCaptureSession {
                id: captureSession
                videoOutput: videoOutput
                camera: camera_manager.camera
                imageCapture: camera_manager.image_capture

                imageCapture: ImageCapture {
                    onImageSaved: function (id, path) {
                        console.info("IMAGE TAKEN!!!")
                        imagePaths.append({"path": path})
                        lvThumbnails.positionViewAtEnd()
                    }
                }

            }
            */
        }
        Rectangle {
            id: rectDataSelection
            height: 75
            color: "#00ffffff"
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.leftMargin: 0
            anchors.rightMargin: 0
            anchors.topMargin: 0

            Row {
                anchors.fill: parent
                spacing: 10
                anchors.rightMargin: 50
                FramCamComboBox {
                    id: comboHauls
                    backgroundColor: appstyle.elevatedSurface_L5
                    fontColor: appstyle.secondaryFontColor
                    borderColor: appstyle.iconColor
                    height: parent.height
                    maxPopupHeight: windowMain.height * 0.65
                    width: parent.width * 0.2
                    fontSize: 14
                    model: data_selector.hauls_model
                    textRole: "haul_number"
                    placeholderText: data_selector.hauls_model.row_count === 0 ? 'N/A' : 'Select Haul...'
                    onCurrentIndexChanged: {
                        model.currentIndex = currentIndex
                    }
                    Component.onCompleted: {  // set ix based on settings saved value
                        comboHauls.currentIndex = model.currentIndex
                    }
                    Connections {
                        target: data_selector.hauls_model
                        function onIndexSetSilently(new_index) {
                            comboHauls.currentIndex = new_index
                        }
                    }
                }

                FramCamComboBox {
                    id: comboCatch
                    backgroundColor: appstyle.elevatedSurface_L5
                    fontColor: appstyle.secondaryFontColor
                    borderColor: appstyle.iconColor
                    height: parent.height
                    maxPopupHeight: windowMain.height * 0.65
                    width: parent.width * 0.2
                    model: data_selector.catches_proxy
                    textRole: "display_name"
                    placeholderText: data_selector.catches_model.row_count === 0 ? 'N/A' : 'Select Catch...'
                    fontSize: 14
                    onCurrentIndexChanged: {
                        model.proxyIndex = currentIndex
                    }
                    Component.onCompleted: {  // set ix based on settings saved value
                        comboCatch.currentIndex = model.getProxyRowFromSource(data_selector.catches_model.currentIndex)
                    }
                    Connections {
                        target: data_selector.catches_model
                        function onIndexSetSilently(new_index) {
                            comboCatch.currentIndex = model.getProxyRowFromSource(new_index)
                        }
                    }
                }
                FramCamComboBox {
                    id: comboProject
                    backgroundColor: appstyle.elevatedSurface_L5
                    fontColor: appstyle.secondaryFontColor
                    borderColor: appstyle.iconColor
                    height: parent.height
                    maxPopupHeight: windowMain.height * 0.65
                    width: parent.width * 0.2
                    model: data_selector.projects_proxy
                    textRole: "project_name"
                    fontSize: 14
                    placeholderText: data_selector.projects_model.row_count === 0 ? 'N/A' : 'Select Project...'
                    onCurrentIndexChanged: {
                        model.proxyIndex = currentIndex
                    }
                    Component.onCompleted: {  // set ix based on settings saved value
                        comboProject.currentIndex = model.getProxyRowFromSource(data_selector.projects_model.currentIndex)
                    }
                    Connections {
                        target: data_selector.projects_model
                        function onIndexSetSilently(new_index) {
                            comboProject.currentIndex = data_selector.projects_proxy.getProxyRowFromSource(new_index)
                        }
                    }
                }
                FramCamComboBox {
                    id: comboBiolabel
                    backgroundColor: appstyle.elevatedSurface_L5
                    fontColor: appstyle.secondaryFontColor
                    borderColor: appstyle.iconColor
                    height: parent.height
                    maxPopupHeight: windowMain.height * 0.65
                    width: parent.width * 0.2
                    model: data_selector.bios_proxy
                    textRole: "bio_label"
                    fontSize: 14
                    placeholderText: data_selector.bios_model.row_count === 0 ? 'N/A' : 'Select Bio Label...'
                    onCurrentIndexChanged: {
                        model.proxyIndex = currentIndex
                    }
                    Component.onCompleted: {  // set ix based on settings saved value
                        comboBiolabel.currentIndex = model.getProxyRowFromSource(data_selector.bios_model.currentIndex)
                    }
                    Connections {
                        target: data_selector.bios_model
                        function onIndexSetSilently(new_index) {
                            comboBiolabel.currentIndex = model.getProxyRowFromSource(new_index)
                        }
                    }
                }
                FramCamButton {
                    id: btnDownloadData
                    implicitWidth: 75
                    implicitHeight: 75
                    radius: 20
                    iconSource: 'qrc:/svgs/download.svg'
                }
            }
        }

    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:0.66;height:480;width:800}
}
##^##*/
