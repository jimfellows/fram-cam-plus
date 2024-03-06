import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 2.15

import 'qrc:/qml'
import QtQuick.VirtualKeyboard 2.1

Rectangle {
    id: root
    color: "#121212"
    border.color: "gray"
    implicitHeight: 417
    implicitWidth: 480
    radius: 8
    clip: true

    property string imageSource;

    GridLayout {
        id: gridLayout
        anchors {
            fill: parent
            leftMargin: 5
            rightMargin: 50
            topMargin: 5
            bottomMargin: 5
        }
        rows: 2
        columns: 2

        Rectangle {
            id: rectImageArea
            Layout.preferredWidth: parent.width * 0.6 - 5
            Layout.preferredHeight: parent.height * 0.5 - 5
            opacity: 0.5
            color: "#ffffff"
            radius: 8

            Image {
                id: imgPreview
                anchors.fill: parent
                source: "file:///" + root.imageSource
                fillMode: Image.PreserveAspectFit
            }
        }
        Rectangle {
            id: rectEditArea
            Layout.preferredWidth: parent.width * 0.4 - 5
            Layout.preferredHeight: parent.height * 0.5 - 5
            opacity: 0.5
            color: "#ffffff"
            radius: 8

            ColumnLayout {
                id: colImageInfo
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: 5
                anchors.topMargin: 10
                anchors.top: parent.top
                spacing: 5
                RowLayout {
                    Layout.fillWidth: true
                    Label { text: 'Haul #:'; Layout.alignment: Qt.AlignRight }
                    Label { text: camera_manager.images_model.curImgHaulNum; Layout.alignment: Qt.AlignLeft }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: 'File Name:'
                        Layout.alignment: Qt.AlignRight
                    }
                    Label {
                        text: camera_manager.images_model.curImgFileName
                        Layout.alignment: Qt.AlignLeft
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: 'Catch Display:'
                        Layout.alignment: Qt.AlignRight
                    }
                    Label {
                        text: camera_manager.images_model.curImgCatch
                        Layout.alignment: Qt.AlignLeft
                    }
                }
                /*
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: 'Common Name:'
                        Layout.alignment: Qt.AlignRight
                    }
                    Label {
                        text: camera_manager.images_model.curImgCommonName
                        Layout.alignment: Qt.AlignLeft
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: 'Scientific Name:'
                        Layout.alignment: Qt.AlignRight
                    }
                    Label {
                        text: camera_manager.images_model.curImgSciName
                        Layout.alignment: Qt.AlignLeft
                    }
                }
                */
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: 'Project:'
                        Layout.alignment: Qt.AlignRight
                    }
                    Label {
                        text: camera_manager.images_model.curImgProject
                        Layout.alignment: Qt.AlignLeft
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: 'Tag/Barcode #:'
                        Layout.alignment: Qt.AlignRight
                    }
                    Label {
                        text: camera_manager.images_model.curImgBioLabel
                        Layout.alignment: Qt.AlignLeft
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: 'Captured Date & Time:'
                        Layout.alignment: Qt.AlignRight
                    }
                    Label {
                        text: camera_manager.images_model.curImgCaptureDt
                        Layout.alignment: Qt.AlignLeft
                    }
                }
                Label {
                    text: "Notes"
                    font.underline: true
                    font.italic: true
                    font.bold: true
                }
                TextArea {
                    Layout.preferredWidth: parent.width
                    Layout.preferredHeight: 50
                }
                RowLayout {
                    Layout.preferredWidth: parent.width
                    Layout.preferredHeight: 50
                    FramCamButton {
                        Layout.preferredWidth: parent.width * 0.25
                        text: "Save & Close"
                        Layout.preferredHeight: 75
                    }
                    FramCamButton {
                        text: "Delete"
                        Layout.preferredWidth: parent.width * 0.25
                        Layout.preferredHeight: 75
                    }
                    FramCamButton {
                        text: "Sync"
                        Layout.preferredWidth: parent.width * 0.25
                        Layout.preferredHeight: 75
                    }
                }
            }
        }
        Rectangle {
            id: rectKeyboardArea
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: parent.height * 0.5 - 5
            Layout.columnSpan: 2
            opacity: 0.1
            color: "#ffffff"
            radius: 8
            InputPanel  {
                id: keyboard
                anchors {
                    left: parent.left
                    right: parent.right
                    leftMargin: 50
                    rightMargin: 50
                }

            }
        }
    }

}
