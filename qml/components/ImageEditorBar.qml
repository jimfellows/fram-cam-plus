import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 2.15

import 'qrc:/qml'
import QtQuick.VirtualKeyboard 2.1

Rectangle {
    id: root
    color: appstyle.surfaceColor
    border.color: appstyle.iconColor
    implicitHeight: 417
    implicitWidth: 480
    radius: 8
    clip: true

    property string imageSource;
    property int labelWidth: 100;

    GridLayout {
        id: gridLayout
        anchors {
            fill: parent
            leftMargin: 10
            rightMargin: 20
            topMargin: 10
            bottomMargin: 10
        }
        rows: 2
        columns: 2

        Rectangle {
            id: rectImageArea
            Layout.preferredWidth: parent.width * 0.4 - 5
            Layout.preferredHeight: parent.height * 0.5 - 5
            //color: appstyle.elevatedSurface_L9
            color: '#556a75'
            radius: 8

            Image {
                id: imgPreview
                anchors {
                    fill: parent
                    topMargin: 5
                    bottomMargin: 5
                    leftMargin: 5
                    rightMargin: 5
                }
                source: camera_manager.images_model.curImgPath ? "file:///" + camera_manager.images_model.curImgPath : ''
                fillMode: Image.PreserveAspectFit
            }
        }
        Rectangle {
            id: rectEditArea
            Layout.preferredWidth: parent.width * 0.6 - 5
            Layout.preferredHeight: parent.height * 0.5 - 5
            color: '#556a75'
            radius: 8
            Label {
                id: lblTitle
                text: camera_manager.images_model.curImgFileName
                color: appstyle.primaryFontColor
                font.bold: true

                anchors {
                    top: parent.top
                    left: parent.left
                    topMargin: 10
                    leftMargin: 10
                }

            }
            RowLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: 15
                anchors.topMargin: 10
                anchors.top: lblTitle.bottom

                ColumnLayout {
                    id: colImageInfo
                    Layout.preferredWidth: parent.width * 0.6
                    Layout.preferredHeight: parent.height
                    spacing: 5
                    RowLayout {
                        Layout.fillWidth: true
                        Label { text: 'Haul #:'; Layout.alignment: Qt.AlignRight; Layout.preferredWidth: root.labelWidth; font.bold: true; font.underline: true; color: appstyle.secondaryFontColor }
                        Label { text: camera_manager.images_model.curImgHaulNum; Layout.alignment: Qt.AlignLeft; color: appstyle.secondaryFontColor}
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        visible: false
                        Label {
                            text: 'File:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                        }
                        Label {
                            text: camera_manager.images_model.curImgFileName
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Catch:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                        }
                        Label {
                            text: camera_manager.images_model.curImgSciName ? camera_manager.images_model.curImgCatch+' ('+camera_manager.images_model.curImgSciName+')' : camera_manager.images_model.curImgCatch
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Project:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                        }
                        Label {
                            text: camera_manager.images_model.curImgProject
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Tag/Barcode:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                        }
                        Label {
                            text: camera_manager.images_model.curImgBioLabel
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Captured:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                        }
                        Label {
                            text: camera_manager.images_model.curImgCaptureDt
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                        }
                    }
                    TextArea {
                        Layout.preferredWidth: parent.width
                        Layout.preferredHeight: 50
                        placeholderText: "Take notes using the keyboard below..."
                        focus: root.width > 0
                        //color: appstyle.iconColor
                    }
                }
                ColumnLayout {
                    Layout.fillHeight: true
                    Layout.rightMargin: 5
                    spacing: 3
                    FramCamButton {
                        text: 'Save & Close'
                        Layout.preferredHeight: 60
                    }
                    FramCamButton {
                        text: 'Delete'
                        Layout.preferredHeight: 60
                        onClicked: {
                            camera_manager.images_model.removeImage(camera_manager.images_model.currentIndex)
                        }
                    }
                    FramCamButton {
                        text: 'Sync to Wheelhouse'
                        Layout.preferredHeight: 60
                    }
                }
            }  //rowlayout for image info
        }
        Rectangle {
            id: rectKeyboardArea
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: parent.height * 0.5 - 5
            Layout.columnSpan: 2
            color: 'black'
            radius: 8
            InputPanel  {
                id: keyboard
                width: parent.width
            }
            /*
            HandwritingInputPanel {
                inputPanel: keyboard
                active: true
            }
            */
        }
    }

}
