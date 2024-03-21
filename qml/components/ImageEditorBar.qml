import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 2.15

import 'qrc:/controls'
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

    ColumnLayout {  // col to hold all things, top to bottom
        id: columnLayout
        anchors {
            fill: parent
            leftMargin: 10
            rightMargin: 20
            topMargin: 10
            bottomMargin: 10
        }
        Rectangle {  // area with image info + notes field
            id: rectEditArea
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: parent.height * 0.35 - 5
            color: '#556a75'
            radius: 8
            Label {
                id: lblTitle
                fontSizeMode: Text.Fit
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
            RowLayout {  // inside our edit rectangle, we have a row containing our labels + text area for notes
                anchors {
                    top: lblTitle.bottom
                    bottom: parent.bottom
                    left: parent.left
                    right: parent.right
                    bottomMargin: 10
                    leftMargin: 20
                    topMargin: 10
                }
                ColumnLayout {  // column for image info
                    id: colImageInfo
                    Layout.preferredWidth: parent.width * 0.5
                    Layout.fillHeight: true
                    Layout.fillWidth: true
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
                            fontSizeMode: Text.Fit
                        }
                        Label {
                            text: camera_manager.images_model.curImgFileName
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Catch:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                        Label {
                            text: camera_manager.images_model.curImgSciName ? camera_manager.images_model.curImgCatch+' ('+camera_manager.images_model.curImgSciName+')' : camera_manager.images_model.curImgCatch
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Project:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            fontSizeMode: Text.Fit
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                        }
                        Label {
                            text: camera_manager.images_model.curImgProject
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Tag/Barcode:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                        Label {
                            text: camera_manager.images_model.curImgBioLabel
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Captured:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appstyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                        Label {
                            text: camera_manager.images_model.curImgCaptureDt
                            Layout.alignment: Qt.AlignLeft
                            color: appstyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                }  // end column for image info
                ColumnLayout {  // col layout for notes text area
                    Layout.preferredWidth: parent.width * 0.4
                    Layout.fillHeight: true
                    spacing: 3
                    TextArea {
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        Layout.rightMargin: 10
                        placeholderText: "Take notes using the keyboard below..."
                        focus: root.width > 0
                        color: appstyle.iconColor
                    }
                }  // end col layout for notes text area
            }  //rowlayout for image info
        }
        Rectangle {
            id: rectKeyboardArea
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: parent.height * 0.5 - 5
            Layout.columnSpan: 2
            color: 'black'
            radius: 8
            RowLayout {
                anchors.fill: parent
                InputPanel  {
                    Layout.preferredWidth: parent.width * 0.85
                    id: keyboard
                    implicitWidth: rectKeyboardArea.width * 0.85
                }
                ColumnLayout {
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                    Layout.fillWidth: true
                    FramCamButton {
                        text: 'Save\n& Close'
                        Layout.preferredHeight: 75
                        Layout.preferredWidth: 90
                    }
                    FramCamButton {
                        text: 'Delete'
                        Layout.preferredHeight: 75
                        Layout.preferredWidth: 90
                        pressedColor: appstyle.errorColor
                        onClicked: {
                            camera_manager.images_model.removeImage(camera_manager.images_model.currentIndex)
                        }
                    }
                    FramCamButton {
                        text: 'Sync to\nWH'
                        Layout.preferredHeight: 75
                        Layout.preferredWidth: 90
                    }
                }
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
