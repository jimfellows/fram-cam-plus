import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Dialogs

import 'qrc:/qml'

Item {

    FolderDialog {
        id: dlgFolders
        onAccepted: {
            tfWheelhouseDir.text = selectedFolder
        }
    }
    FileDialog {
        id: dlgFiles
        onAccepted: {
            tfBackdeckDb.text = selectedFile
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
            FramCamGroupBox {
                id: gbNetwork
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: parent.height * 0.7
                title: 'Network'
                property int labelWidth: 200
                property int widgetHeight: 75
                property int buttonWidth: 100
                ColumnLayout {
                    RowLayout {
                        spacing: 10
                        Label {
                            text: "Vessel Subnet"
                            color: appstyle.secondaryFontColor
                            font.pixelSize: 18
                            font.family: appstyle.fontFamily
                            Layout.preferredWidth: gbNetwork.labelWidth
                        }
                        FramCamComboBox {
                            id: cbSubnet
                            Layout.preferredWidth: 500
                            Layout.preferredHeight: gbNetwork.widgetHeight
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
                            Layout.preferredHeight: gbNetwork.widgetHeight
                            Layout.preferredWidth: gbNetwork.buttonWidth
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
                            color: appstyle.secondaryFontColor
                            font.pixelSize: 18
                            font.family: appstyle.fontFamily
                            Layout.preferredWidth: gbNetwork.labelWidth
                        }
                        FramCamTextField {
                            id: tfWheelhouseDir
                            Layout.preferredWidth: 500
                            Layout.preferredHeight: gbNetwork.widgetHeight - 10  // not sure why text field comes out bigger than the rest
                            placeholderText: "Browse to PyCollector data folder over the network..."
                            Component.onCompleted: tfWheelhouseDir.text = settings.curWheelhouseDataDir
                        }
                        FramCamButton {
                            text: 'Browse'
                            Layout.preferredHeight: gbNetwork.widgetHeight
                            Layout.preferredWidth: gbNetwork.buttonWidth
                            onClicked: dlgFolders.open()
                        }
                        FramCamButton {
                            text: 'Verify'
                            Layout.preferredHeight: gbNetwork.widgetHeight
                            Layout.preferredWidth: gbNetwork.buttonWidth
                            onClicked: console.info("DOES THIS FOLDER EXIST????")
                        }
                        FramCamButton {
                            text: 'Map\nWheelhouse'
                            Layout.preferredHeight: gbNetwork.widgetHeight
                            Layout.preferredWidth: gbNetwork.buttonWidth
                            onClicked: console.info("NEED TO IMPLEMENT FUNC THAT MAPS TO WH MACHINE")
                        }
                    }
                    RowLayout {
                        spacing: 10
                        Label {
                            text: "Backdeck DB File"
                            color: appstyle.secondaryFontColor
                            font.pixelSize: 18
                            font.family: appstyle.fontFamily
                            Layout.preferredWidth: gbNetwork.labelWidth
                        }
                        FramCamTextField {
                            id: tfBackdeckDb
                            Layout.preferredWidth: 500
                            Layout.preferredHeight: gbNetwork.widgetHeight - 10  // not sure why text field comes out bigger than the rest
                            placeholderText: "Browse to trawl_backdeck.db over the network..."
                            Component.onCompleted: tfBackdeckDb.text = settings.curBackdeckDb
                        }
                        FramCamButton {
                            text: 'Browse'
                            Layout.preferredHeight: gbNetwork.widgetHeight
                            Layout.preferredWidth: gbNetwork.buttonWidth
                            onClicked: dlgFiles.open()
                        }
                        FramCamButton {
                            text: 'Verify'
                            Layout.preferredHeight: gbNetwork.widgetHeight
                            Layout.preferredWidth: gbNetwork.buttonWidth
                            onClicked: console.info("DOES THIS FILE EXIST????")
                        }
                        FramCamButton {
                            text: 'Map\nBackdeck'
                            Layout.preferredHeight: gbNetwork.widgetHeight
                            Layout.preferredWidth: gbNetwork.buttonWidth
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
                    RowLayout {
                        spacing: 10
                        Label {
                            text: "Color Mode"
                            color: appstyle.secondaryFontColor
                            font.pixelSize: 18
                            font.family: appstyle.fontFamily
                            Layout.preferredWidth: gbUi.labelWidth
                        }
                        FramCamComboBox {
                            Layout.preferredWidth: 400
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
