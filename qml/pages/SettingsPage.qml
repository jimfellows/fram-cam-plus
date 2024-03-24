import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Dialogs

import 'qrc:/controls'

Item {
    id: root
    
    // sizing props
    property int labelWidth: 140
    property int widgetHeight: 75
    property int buttonWidth: 95
    property int labelSize: 14    
    
    FolderDialog {
        id: dlgFolders
        onAccepted: {
            tfWheelhouseDir.text = selectedFolder.toString().replace('file:///', '')
        }
    }
    FileDialog {
        id: dlgFiles
        onAccepted: {
            tfBackdeckDb.text = selectedFile.toString().replace('file:///', '')
        }
    }

    Connections {
        target: settings
        function onBackdeckPinged(pingStatus) {
            console.info("PINGED BACKDECK, status = " + pingStatus)
        }
    }
    Rectangle {
        id: rectBg
        color: appstyle.elevatedSurface_L5
        anchors.fill: parent
        anchors.topMargin: 10
        anchors.bottomMargin: 10
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        
        ColumnLayout {
            id: columnLayout
            anchors.fill: parent
            spacing: 15
            FramCamGroupBox {
                id: gbNetwork
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: parent.height * 0.65
                title: 'Network'

                ColumnLayout {
                    RowLayout {
                        spacing: 15
                        Label {
                            text: "Vessel Subnet"
                            color: appstyle.secondaryFontColor
                            font.pixelSize: root.labelSize
                            font.family: appstyle.fontFamily
                            Layout.preferredWidth: root.labelWidth
                        }
                        FramCamComboBox {
                            id: cbSubnet
                            Layout.preferredWidth: 200
                            Layout.preferredHeight: root.widgetHeight
                            backgroundColor: appstyle.elevatedSurface_L5
                            model: ['192.254.243', '192.254.242', '127.0.0.1']
                            placeholderText: 'Select a vessel subnet...'
                            onCurrentIndexChanged: settings.curVesselSubnet = model[currentIndex]
                            Component.onCompleted: cbSubnet.currentIndex = cbSubnet.model.indexOf(settings.curVesselSubnet)

                            Connections {
                                target: settings
                                function onBackdeckPinged(status) {
                                    cbSubnet.borderColor = status ? appstyle.accentColor : appstyle.errorColor
                                }
                            }
                        }
                        FramCamButton {
                            id: btnPing
                            text: 'Ping'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            iconSource: settings.isPingRunning ? 'qrc:/svgs/loading_gif_youtube.svg' : null
                            enabled: cbSubnet.currentIndex > -1
                            onClicked: {
                                settings.pingBackdeck()
                            }
                        }
                    }
                    RowLayout {
                        spacing: 10
                        Label {
                            text: "Wheelhouse Data Dir."
                            font.pixelSize: root.labelSize
                            color: appstyle.secondaryFontColor
                            font.family: appstyle.fontFamily
                            Layout.preferredWidth: root.labelWidth
                        }
                        FramCamTextField {
                            id: tfWheelhouseDir
                            Layout.preferredWidth: 400
                            Layout.preferredHeight: root.widgetHeight - 10  // not sure why text field comes out bigger than the rest
                            placeholderText: "Browse to PyCollector data folder over the network..."
                            Component.onCompleted: tfWheelhouseDir.text = settings.curWheelhouseDataDir
                            onTextChanged: settings.curWheelhouseDataDir = text

                        }
                        FramCamButton {
                            text: 'Browse'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            onClicked: dlgFolders.open()
                        }
                        FramCamButton {
                            text: 'Verify'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            onClicked: console.info("DOES THIS FOLDER EXIST????")
                        }
                        FramCamButton {
                            text: 'Map\nWheelhouse'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            onClicked: console.info("NEED TO IMPLEMENT FUNC THAT MAPS TO WH MACHINE")
                        }
                    }
                    RowLayout {
                        spacing: 10
                        Label {
                            text: "Backdeck DB File"
                            font.pixelSize: root.labelSize
                            color: appstyle.secondaryFontColor
                            font.family: appstyle.fontFamily
                            Layout.preferredWidth: root.labelWidth
                        }
                        FramCamTextField {
                            id: tfBackdeckDb
                            Layout.preferredWidth: 400
                            Layout.preferredHeight: root.widgetHeight - 10  // not sure why text field comes out bigger than the rest
                            placeholderText: "Browse to trawl_backdeck.db over the network..."
                            Component.onCompleted: tfBackdeckDb.text = settings.curBackdeckDb
                        }
                        FramCamButton {
                            text: 'Browse'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            onClicked: dlgFiles.open()
                        }
                        FramCamButton {
                            text: 'Verify'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            onClicked: console.info("DOES THIS FILE EXIST????")
                        }
                        FramCamButton {
                            text: 'Map\nBackdeck'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            onClicked: console.info("NEED TO IMPLEMENT FUNC THAT MAPS TO BD MACHINE")
                        }
                    }
                }

            }
            FramCamGroupBox {
                id: gbUi
                Layout.preferredWidth: parent.width
                //Layout.preferredHeight: parent.height * 0.2
                property int labelWidth: 200
                title: 'UI'
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        Label {
                            text: "Color Mode"
                            color: appstyle.secondaryFontColor
                            font.pixelSize: root.labelSize
                            font.family: appstyle.fontFamily
                            Layout.preferredWidth: gbUi.labelWidth
                        }
                        FramCamComboBox {
                            Layout.alignment: Qt.AlignLeft
                            Layout.preferredWidth: 300
                            Layout.preferredHeight: 75
                            model: ['Dark', 'Light', 'Grey']
                            backgroundColor: appstyle.elevatedSurface_L5
                            placeholderText: 'Select UI color mode...'
                            onCurrentIndexChanged: {
                                settings.curUiMode = model[currentIndex]
                            }
                        }
                    }
                }
            }
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
