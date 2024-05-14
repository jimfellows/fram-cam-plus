

import QtQuick 2.15
import QtQuick.Layouts 6.3
import QtQuick.Controls 2.15
import QtMultimedia 6.3

import 'qrc:/controls'
import QtQuick.VirtualKeyboard 2.1

Rectangle {
    id: root
    color: appStyle.elevatedSurface_L9
    border.color: appStyle.primaryColor
    border.width: 5

    implicitHeight: 417
    implicitWidth: 480
    radius: 8
    clip: true

    property string imageSource: imageManager.imagesModel.curImgFilePath ? "file:///" + imageManager.imagesModel.curImgFilePath : null;

    SoundEffect {
        id: syncChime
        source: "qrc:/sounds/forward_chime.wav"
    }

    SoundEffect {
        id: deleteTone
        source: "qrc:/sounds/negative_tone.wav"
    }

    Image {
        id: img
        source: root.imageSource
        anchors.fill: parent
        anchors.leftMargin: 5
        anchors.rightMargin: 5
        anchors.topMargin: 5
        anchors.bottomMargin: 5
        fillMode: Image.PreserveAspectFit
        cache: true
    }
    Rectangle {
        id: rectImgName
        radius: 8
        opacity: 0.7
        color: appStyle.surfaceColor
        height: 30
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            topMargin: 10
            leftMargin: 10
            rightMargin: 10
        }
        Label {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            text: imageManager.imagesModel.curImgFileName
            color: appStyle.primaryFontColor
            font.bold: true
            font.underline: true
        }
    }

    Rectangle {
        id: rectImageInfo
        radius: 8
        opacity: 0.7
        color: appStyle.surfaceColor
        height: parent.height * 0.4
        width: parent.width * 0.4

        anchors {
            top: rectImgName.bottom
            left: rectImgName.left
            topMargin: 5
            //leftMargin: 15
        }

        ColumnLayout {

            id: colImageInfo
            anchors.fill: parent
            anchors.leftMargin: 5
            anchors.bottomMargin: 5
            anchors.rightMargin: 5
            anchors.topMargin: 5

            property int labelWidth: 80

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Label {
                    id: lblHaul
                    text: "Haul:"
                    font.bold: true;
                    font.underline: true;
                    color: appStyle.primaryFontColor;
                    Layout.preferredWidth: colImageInfo.labelWidth
                    Layout.alignment: Qt.AlignRight;
                }
                Label {
                    id: lblHaulValue
                    text: imageManager.imagesModel.curImgHaulNum
                    color: appStyle.primaryFontColor;
                    Layout.alignment: Qt.AlignLeft;
                    font.bold: true;
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Label {
                    id: lblCatch
                    text: "Catch:"
                    font.bold: true;
                    font.underline: true;
                    color: appStyle.primaryFontColor;
                    Layout.preferredWidth: colImageInfo.labelWidth
                }
                Label {
                    id: lblCatchValue
                    text: imageManager.imagesModel.curImgCatch
                    color: appStyle.primaryFontColor;
                    Layout.alignment: Qt.AlignLeft;
                    font.bold: true;
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Label {
                    id: lblProject
                    text: "Project:"
                    font.bold: true;
                    font.underline: true;
                    color: appStyle.primaryFontColor;
                    Layout.preferredWidth: colImageInfo.labelWidth
                }
                Label {
                    id: lblProjectValue
                    text: imageManager.imagesModel.curImgProject
                    color: appStyle.primaryFontColor;
                    Layout.alignment: Qt.AlignLeft;
                    font.bold: true;
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Label {
                    id: lblTag
                    text: "Tag/Barcode:"
                    font.bold: true;
                    font.underline: true;
                    color: appStyle.primaryFontColor;
                    Layout.preferredWidth: colImageInfo.labelWidth
                }
                Label {
                    id: lblTagValue
                    text: imageManager.imagesModel.curImgBioLabel
                    color: appStyle.primaryFontColor;
                    Layout.alignment: Qt.AlignLeft;
                    font.bold: true;
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Label {
                    id: lblCaptured
                    text: "Captured @:"
                    font.bold: true;
                    font.underline: true;
                    color: appStyle.primaryFontColor;
                    Layout.preferredWidth: colImageInfo.labelWidth
                }
                Label {
                    id: lblCapturedValue
                    text: imageManager.imagesModel.curImgCaptureDt
                    color: appStyle.primaryFontColor;
                    Layout.alignment: Qt.AlignLeft;
                    font.bold: true;
                }
            }
            TextArea {
                id: taNotes
                text: imageManager.imagesModel.curImgNotes ? imageManager.imagesModel.curImgNotes : ""
                wrapMode: Text.WrapAnywhere
                background: Rectangle {
                    color: appStyle.secondaryFontColor
                    anchors.fill: taNotes
                    radius: 8
                }
                Layout.fillHeight: true
                Layout.fillWidth: true

                placeholderText: "Take notes record notes here.\nTouch here to activate keyboard..."
                color: appStyle.surfaceColor
                onTextChanged: imageManager.imagesModel.curImgNotes = text
            }
            FramCamProgressBar {
                id: progressCopy
                value: 0  // start at 0
                runningColor: appStyle.accentColor
                indeterminate: false
                height: 8
                Layout.fillWidth: true
                Layout.fillHeight: true
                Connections {
                    target: imageManager
                    function onCopyStarted(no_of_files) {
                        progressCopy.visible =  true
                        progressCopy.value = 0
                        progressCopy.runningColor = appStyle.accentColor
                        animateProgress.running = true
                    }
                    function onFileCopied(path, new_path, success) {
                        if (!success) {
                            progressCopy.runningColor = appStyle.errorColor
                        } else {
                            syncChime.play()
                        }
                    }
                }
                Connections {
                    target: imageManager.imagesModel
                    function onCurrentImageValChanged(role_name, value) {
                        if (role_name === 'is_backed_up' && value === 0) animateProgressUndo.running = true
                    }
                    function onCurrentImageChanged() {  // TODO: could probably bind this value?
                        progressCopy.value = imageManager.imagesModel.isImgBackedUp
                    }
                }
                PropertyAnimation{
                    id: animateProgress
                    target: progressCopy
                    property: "value"
                    to: 1
                    duration: 1000
                    easing.type: Easing.InOutQuint
                }
                PropertyAnimation{
                    id: animateProgressUndo
                    target: progressCopy
                    property: "value"
                    to: 0
                    duration: 700
                    easing.type: Easing.InOutQuint
                }
            }
        }  // col layout for image info ends here
    }  // rectangle containing image info ends here

    InputPanel  {
        id: keyboard
        implicitWidth: root.width * 0.9
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 5
        opacity: 0.6
        visible: taNotes.focus
        Connections {
            target: Qt.inputMethod
            //https://stackoverflow.com/questions/69814505/how-to-capture-hide-key-event-in-qt-virtualkeyboard
            function onVisibleChanged() { keyboard.visible = Qt.inputMethod.visible }
        }
    }
    HandwritingInputPanel {
        inputPanel: keyboard
        active: true
        available: true
    }
    Rectangle {
        id: rectButtons
        width: 260
        height: 90
        anchors {
            right: rectImgName.right
            top: rectImgName.bottom
            topMargin: 5
            //rightMargin: 15
        }
        color: appStyle.surfaceColor
        opacity: 0.7
        radius: 8
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 9
            anchors.rightMargin: 9
            anchors.horizontalCenter: parent.horizontalCenter
            FramCamButton {
                text: 'Save'
                Layout.preferredHeight: 75
                Layout.preferredWidth: 70
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                onClicked: {
                    capturePage.lvThumbnails.currentIndex = -1
                }
            }
            FramCamButton {
                text: 'Delete'
                Layout.preferredHeight: 75
                Layout.preferredWidth: 70
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                pressedColor: appStyle.errorColor
                onClicked: {
                    imageManager.imagesModel.removeImage(imageManager.imagesModel.currentIndex)
                    deleteTone.play()
                }
            }
            FramCamButton {
                text: 'Sync'
                Layout.preferredHeight: 75
                Layout.preferredWidth: 70
                Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                onClicked: {
                    imageManager.copyCurImageToWheelhouse()
                }
            }
        }
    }

}  // entire rectangle of area ends here