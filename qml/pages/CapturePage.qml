import QtQuick.Controls 6.3
import QtQuick 2.15
import Qt5Compat.GraphicalEffects
import QtMultimedia 6.3
//import com.library.name 1.0

import './qml/controls'
//import './qml/AppStyle'


Item {
    property alias lvThumbnails: lvThumbnails
    Component.onCompleted: {
        camera_manager.set_video_output(videoOutput)
        switchPreview.position = camera_manager.is_camera_active ? 1 : 0
    }

    Rectangle {
        id: rectBg
        color: "#00ffffff"
        border.color: "#00000000"
        anchors.fill: parent
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 5
        anchors.topMargin: 5

        Rectangle {
            id: rectImgArea
            color: "#00ffffff"
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
                color: "#bababa"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.rightMargin: 150

                Image {
                    id: image
                    width: 100
                    height: 100
                    anchors.verticalCenter: parent.verticalCenter
                    source: "qrc:/svgs/eye_closed.svg"
                    anchors.horizontalCenter: parent.horizontalCenter
                    fillMode: Image.PreserveAspectFit
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
                    opacity: 0.5
                    color: "#000000"
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
                        to: if(rectControls.height === 100) return 5; else return 100;
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
                        anchors.topMargin: 0
                        anchors.horizontalCenter: parent.horizontalCenter

                        Connections {
                            target: animationControls
                            onFinished: {
                                if (rectControls.height > 75) {
                                    rectMoveControls.anchors.topMargin = 0
                                    imgMoveControls.source = "qrc:/svgs/down_arrow.svg"
                                } else {
                                    rectMoveControls.anchors.topMargin = -40
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
                            color: 'white'
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
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.topMargin: 0
                        anchors.bottomMargin: 0
                        anchors.rightMargin: 5
                        anchors.leftMargin: 5

                        FramCamSwitch {
                            id: switchPreview
                            width: 100
                            spacing: 6
                            switchWidth: 100
                            titleText: "Camera Preview"
                            titleFontSize: 12
                            titleColor: "#ffffff"
                            checkedColor: "#0085ca"
                            onPositionChanged: {
                                if (position === 1) {
                                    camera_manager.start_camera()
                                }
                                else {
                                    camera_manager.stop_camera()
                                }
                            }
                        }
                    }
                }

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
            }

            Rectangle {
                id: rectThumbnails
                y: 0

                color: "black"
                anchors.left: rectImgPreview.right
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 0
                opacity: 0.5

                ListView {
                    id: lvThumbnails
                    x: 0
                    y: 0
                    anchors.fill: parent
                    anchors.leftMargin: 10
                    anchors.rightMargin: 10
                    anchors.topMargin: 20
                    orientation: ListView.Vertical
                    spacing: 10
                    model: camera_manager.images_model

                    delegate: Column {
                        Image {
                            id: imgThumbnail
                            source: "file:///" + model.full_path
                            width: lvThumbnails.width - 10
                            height: 50
                            fillMode: Image.PreserveAspectFit
                            scale: camera_manager.images_model.currentIndex === index ? 1.2 : 1
                            layer.enabled: camera_manager.images_model.currentIndex === index
                            layer.effect: DropShadow {
                                verticalOffset: 0
                                horizontalOffset: 0
                                //opacity: 0.5
                                radius: 20
                                color: "lightgray"
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: camera_manager.images_model.currentIndex = index
                            }
                        }
                        Label {
                            id: imgLabel
                            text: model.catch_display_name
                            font.pixelSize: 8
                            font.bold: true
                            font.family: 'roboto'
                            color: "white"
                            anchors.left: rectUnderline.left
                        }
                        Rectangle {
                            id: rectUnderline
                            height: 1
                            width: imgThumbnail.width - 10
                            color: "white"
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
            height: 53
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
                    backgroundColor: "#003087"
                    height: parent.height
                    width: parent.width * 0.2
                    fontSize: 14
                    model: data_selector.hauls_model
                    placeholderText: data_selector.hauls_model.row_count === 0 ? 'N/A' : 'Select Haul...'
                    onCurrentIndexChanged: {
                        model.current_index = currentIndex
                    }
                    Component.onCompleted: {  // set ix based on settings saved value
                        comboHauls.currentIndex = data_selector.hauls_model.current_index
                    }
                }
                FramCamComboBox {
                    id: comboCatch
                    backgroundColor: "#003087"
                    height: parent.height
                    width: parent.width * 0.3
                    model: data_selector.catches_model
                    placeholderText: data_selector.catches_model.row_count === 0 ? 'N/A' : 'Select Catch...'
                    fontSize: 14
                    onCurrentIndexChanged: {
                        console.info("CATCH COMBO INDEX CHANGED to " + currentIndex)
                        model.current_index = currentIndex
                    }
                    Component.onCompleted: {  // set ix based on settings saved value
                        comboCatch.currentIndex = data_selector.catches_model.current_index
                    }
                }
                FramCamComboBox {
                    id: comboProject
                    backgroundColor: "#003087"
                    height: parent.height
                    width: parent.width * 0.3
                    model: data_selector.projects_model
                    fontSize: 14
                    placeholderText: data_selector.projects_model.row_count === 0 ? 'N/A' : 'Select Project...'
                    onCurrentIndexChanged: {
                        model.current_index = currentIndex
                    }
                    Component.onCompleted: {  // set ix based on settings saved value
                        comboProject.currentIndex = data_selector.projects_model.current_index
                    }
                    Connections {
                        target: data_selector.projects_model
                        onPy_index_update: {
                            comboProject.currentIndex = i
                        }

                    }
                }
                FramCamComboBox {
                    id: comboBiolabel
                    backgroundColor: "#003087"
                    height: parent.height
                    width: parent.width * 0.2
                    model: data_selector.bios_model
                    fontSize: 14
                    placeholderText: data_selector.bios_model.row_count === 0 ? 'N/A' : 'Select Bio Label...'
                    onCurrentIndexChanged: {
                        model.current_index = currentIndex
                    }
                    Component.onCompleted: {  // set ix based on settings saved value
                        comboBiolabel.currentIndex = data_selector.bios_model.current_index
                    }
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
