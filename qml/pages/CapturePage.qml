import QtQuick.Controls 6.3
import QtQuick 2.15
import Qt5Compat.GraphicalEffects
import QtMultimedia 6.3

import './qml/controls'


Item {
    property alias lvThumbnails: lvThumbnails

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
                anchors.rightMargin: 100

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
                                if(position === 1) {
                                    camDefault.start()
                                }
                                else {
                                    camDefault.stop()
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
                        console.info("BUTTON CLICKED, is camera ready?")
                        console.info(captureSession.imageCapture.readyForCapture)
                        var x
                        x = captureSession.imageCapture.captureToFile('pic.jpeg')
                        //                    captureSession.imageCapture.imageSaved()
                        console.info(x)
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
                    height: 75
                    anchors.left: parent.left
                    anchors.right: parent.right

                    anchors.top: parent.top
                    anchors.leftMargin: 0
                    anchors.rightMargin: 0
                    anchors.topMargin: 0


                    orientation: ListView.Horizontal
                    spacing: 10

                    model: imagePaths

                    delegate: Image {
                        required property string path
                        height: 100
                        source: path
                        fillMode: Image.PreserveAspectFit
                    }
                }
            }

            ListModel {
                id: imagePaths
            }
            Camera {
                id: camDefault
            }

            CaptureSession {
                id: captureSession
                videoOutput: videoOutput
                camera: camDefault
                imageCapture: ImageCapture {
                    onImageSaved: function (id, path) {
                        console.info("IMAGE TAKEN!!!")
                        imagePaths.append({"path": path})
                        lvThumbnails.positionViewAtEnd()
                    }
                }
            }

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
                FramCamComboBox {
                    id: ddTows
                    backgroundColor: "#003087"

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
