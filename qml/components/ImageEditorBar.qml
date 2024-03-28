import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 2.15
//import QtQuick.Controls.Material

import 'qrc:/controls'
import QtQuick.VirtualKeyboard 2.1

Rectangle {
    id: root
    color: appStyle.surfaceColor
    border.color: appStyle.iconColor
    implicitHeight: 417
    implicitWidth: 480
    radius: 8
    clip: true

    property string imageSource;
    property int labelWidth: 80;

    //Material.theme: Material.Dark

    // make sure notes are active so keyboard knows where to go
    onWidthChanged: if (width > 0) {
        taNotes.forceActiveFocus()
    } else {
        lblTitle.forceActiveFocus()  // just need to make sure we unselect our notes
    }

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
            Layout.preferredHeight: parent.height * 0.40
            color: '#556a75'
            radius: 8
            Label {
                id: lblTitle
                fontSizeMode: Text.Fit
                text: imageManager.imagesModel.curImgFileName
                color: appStyle.primaryFontColor
                font.bold: true
                anchors {
                    top: parent.top
                    left: parent.left
                    topMargin: 10
                    leftMargin: 8
                }

            }
            RowLayout {  // inside our edit rectangle, we have a row containing our labels + text area for notes
                anchors {
                    top: lblTitle.bottom
                    bottom: parent.bottom
                    left: parent.left
                    right: parent.right
                    bottomMargin: 10
                    leftMargin: 10
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
                        Label { text: 'Haul #:'; Layout.alignment: Qt.AlignRight; Layout.preferredWidth: root.labelWidth; font.bold: true; font.underline: true; color: appStyle.secondaryFontColor }
                        Label { text: imageManager.imagesModel.curImgHaulNum; Layout.alignment: Qt.AlignLeft; color: appStyle.secondaryFontColor}
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        visible: false
                        Label {
                            text: 'File:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                        Label {
                            text: imageManager.imagesModel.curImgFileName
                            Layout.alignment: Qt.AlignLeft
                            color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Catch:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                        Label {
                            text: imageManager.imagesModel.curImgSciName ? imageManager.imagesModel.curImgCatch+' ('+imageManager.imagesModel.curImgSciName+')' : imageManager.imagesModel.curImgCatch
                            Layout.alignment: Qt.AlignLeft
                            color: appStyle.secondaryFontColor
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
                            font.bold: true; font.underline: true; color: appStyle.secondaryFontColor
                        }
                        Label {
                            text: imageManager.imagesModel.curImgProject
                            Layout.alignment: Qt.AlignLeft
                            color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Tag/Barcode:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                        Label {
                            text: imageManager.imagesModel.curImgBioLabel
                            Layout.alignment: Qt.AlignLeft
                            color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Captured:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                        Label {
                            text: imageManager.imagesModel.curImgCaptureDt
                            Layout.alignment: Qt.AlignLeft
                            color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        Label {
                            text: 'Is Synced?:'
                            Layout.alignment: Qt.AlignRight
                            Layout.preferredWidth: root.labelWidth
                            font.bold: true; font.underline: true; color: appStyle.secondaryFontColor
                            fontSizeMode: Text.Fit
                            //Layout.fillWidth: true
                        }
                        FramCamCheckBox {
                            id: cbIsSynced
                            Layout.preferredWidth: 25
                            Layout.preferredHeight: 25
                            enabled: false
                            checked: imageManager.imagesModel.isImgBackedUp
                            Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                        }
                        FramCamProgressBar {
                            id: progressCopy
                            value: imageManager.imagesModel.isImgBackedUp ? to : 0
                            visible: imageManager.imagesModel.isImgBackedUp
                            indeterminate: false
                            Layout.preferredHeight: 15
                            Layout.preferredWidth: 200
                            Layout.alignment: Qt.AlignRight
                            Layout.fillWidth: false
                            Layout.leftMargin: 10
                            Layout.rightMargin: 10
                            Connections {
                                target: imageManager
                                function onCopyStarted(no_of_files) {
                                    progressCopy.visible =  true
                                    progressCopy.value = 0
                                    progressCopy.runningColor = appStyle.primaryColor
                                    animateProgress.running = true
                                }
                                function onFileCopied(path, new_path, success) {
                                    if (!success) progressCopy.runningColor = appStyle.errorColor
                                }
                                function onCurrentImageChanged() {
                                    console.info("IMAGE CHANGED, is it backed up? " + imageManager.imagesModel.isImgBackedUp)
                                }
                            }
                            PropertyAnimation{
                                id: animateProgress
                                target: progressCopy
                                property: "value"
                                to: 1
                                duration:400
                                easing.type: Easing.InOutQuint
                            }
                        }
                    }
                }  // end column for image info
                ColumnLayout {  // col layout for notes text area
                    Layout.preferredWidth: parent.width * 0.4
                    Layout.fillHeight: true
                    spacing: 3
                    TextArea {
                        id: taNotes
                        text: imageManager.imagesModel.curImgNotes ? imageManager.imagesModel.curImgNotes : ""
                        background: Rectangle {
                            color: appStyle.iconColor
                            anchors.fill: taNotes
                            radius: 8
                        }
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        Layout.rightMargin: 10
                        placeholderText: "Take notes using the keyboard below..."
                        focus: root.width > 0
                        color: appStyle.surfaceColor
                        onTextChanged: imageManager.imagesModel.curImgNotes = text
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
                        onClicked: {
                            capturePage.lvThumbnails.currentIndex = -1
                        }
                    }
                    FramCamButton {
                        text: 'Delete'
                        Layout.preferredHeight: 75
                        Layout.preferredWidth: 90
                        pressedColor: appStyle.errorColor
                        onClicked: {
                            imageManager.imagesModel.removeImage(imageManager.imagesModel.currentIndex)
                        }
                    }
                    FramCamButton {
                        text: 'Sync to\nWH'
                        Layout.preferredHeight: 75
                        Layout.preferredWidth: 90
                        onClicked: {
                            imageManager.copyCurImageToWheelhouse()
                        }
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
