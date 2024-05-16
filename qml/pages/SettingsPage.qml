import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Dialogs

import 'qrc:/controls'
import 'qrc:/components'

Item {
    id: root
    
    // sizing props
    property int labelWidth: 140
    property int widgetHeight: 75
    property int buttonWidth: 80
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

    CredentialsDialog {
        id: dlgDriveMapper
        property string driveLetter;
        onLoginAttempt: {
            if (driveLetter === 'W') settings.mapDrive(driveLetter, tfUsername.text, tfPassword.text);
            if (driveLetter === 'V') settings.mapDrive(driveLetter, tfUsername.text, tfPassword.text);
        }
        Connections {
            target: settings
            function onDriveMapAttempted(success, msg, drive_letter) {
                if (success) {
                    dlgDriveMapper.close()
                } else {
                    dlgDriveMapper.loginFailed()
                }
            }
        }
    }

    LoggingDialog {
        id: dlgLogs
    }

    Connections {
        target: settings
        function onBackdeckPinged(pingStatus) {
            console.info("PINGED BACKDECK, status = " + pingStatus)
        }
    }
    Rectangle {
        id: rectBg
        color: appStyle.elevatedSurface_L5
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
                Layout.preferredHeight: parent.height * 0.6
                title: 'App'

                ColumnLayout {
                    spacing: 15
                    RowLayout {
                        spacing: 23
                        RowLayout {
                            FramCamComboBox {
                                id: cbSubnet
                                titleLabelText: 'Vessel Subnet'
                                Layout.preferredWidth: 200
                                Layout.preferredHeight: root.widgetHeight
                                backgroundColor: appStyle.elevatedSurface_L5
                                model: ['192.254.253', '192.254.254', '127.0.0.1']
                                placeholderText: 'Select a vessel subnet...'
                                onCurrentIndexChanged: settings.curVesselSubnet = model[currentIndex]
                                Component.onCompleted: cbSubnet.currentIndex = cbSubnet.model.indexOf(settings.curVesselSubnet)

                                Connections {
                                    target: settings
                                    function onBackdeckPinged(status) {
                                        cbSubnet.borderColor = status ? appStyle.accentColor : appStyle.errorColor
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
                        } // subnet row
                        RowLayout {
                            FramCamComboBox {
                                id: cbLogLevels
                                Layout.alignment: Qt.AlignLeft
                                Layout.preferredWidth: 200
                                Layout.preferredHeight: 75
                                titleLabelText: "Logging Level"
                                model: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                                backgroundColor: appStyle.elevatedSurface_L5
                                placeholderText: 'Select log level...'
                                Component.onCompleted: cbLogLevels.currentIndex = cbLogLevels.model.indexOf(settings.curLogLevel)
                                onCurrentIndexChanged: {
                                    settings.curLogLevel = model[currentIndex]
                                }
                            }
                            FramCamButton {
                                text: "Launch\nConsole"
                                Layout.preferredHeight: 75
                                Layout.preferredWidth: 75
                                onClicked: dlgLogs.open()
                            }
                        }
                        FramCamComboBox {
                            id: cbUiMode
                            Layout.alignment: Qt.AlignLeft
                            Layout.preferredWidth: 200
                            Layout.preferredHeight: 75
                            titleLabelText: "UI Color Mode"
                            model: ['Wheelhouse', 'Backdeck', 'NOAA']
                            backgroundColor: appStyle.elevatedSurface_L5
                            placeholderText: 'Select UI mode...'
                            Component.onCompleted: cbUiMode.currentIndex = cbUiMode.model.indexOf(settings.curUiMode)
                            onCurrentIndexChanged: {
                                settings.curUiMode = model[currentIndex]
                            }
                        }

                    }
                    RowLayout {
                        spacing: 10
                        FramCamTextField {
                            id: tfWheelhouseDir
                            fontSize: 12
                            titleLabelText: 'Wheelhouse Data Dir. (Image Backup Path)'
                            Layout.preferredWidth: 475
                            Layout.preferredHeight: root.widgetHeight - 10  // not sure why text field comes out bigger than the rest
                            placeholderText: "Browse to PyCollector data folder over the network..."
                            Component.onCompleted: {
                                tfWheelhouseDir.text = settings.curWheelhouseDataDir
                                settings.verifyWheelhouseDataDir()
                            }
                            onTextChanged: settings.curWheelhouseDataDir = text
                            Connections {
                                target: settings
                                function onWheelhouseDataDirVerified(status) {
                                    tfWheelhouseDir.borderColor = status ? appStyle.accentColor : appStyle.errorColor
                                }
                            }
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
                            onClicked: settings.verifyWheelhouseDataDir()
                        }
                        FramCamButton {
                            text: 'Map W:'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            onClicked: {
                                dlgDriveMapper.loginDestination = 'Wheelhouse CPU'
                                dlgDriveMapper.driveLetter = 'W'
                                dlgDriveMapper.open()
                            }
                        }
                        FramCamButton {
                            text: 'Map V:'
                            Layout.preferredHeight: root.widgetHeight
                            Layout.preferredWidth: root.buttonWidth
                            onClicked: {
                                dlgDriveMapper.loginDestination = 'Backdeck CPU'
                                dlgDriveMapper.driveLetter = 'V'
                                dlgDriveMapper.open()
                            }
                        }
                    }
                }
            }
            RowLayout {
                Layout.preferredWidth: parent.width
                FramCamGroupBox {
                    id: gbCamera
                    Layout.preferredWidth: parent.width
                    title: 'Camera'
                    RowLayout {
                        FramCamComboBox {
                            id: cbCameraResolution
                            enabled: false
                            Layout.alignment: Qt.AlignLeft
                            Layout.preferredWidth: 300
                            Layout.preferredHeight: 75
                            titleLabelText: "Image Resolution"
                            // https://doc.qt.io/qt-6/qimagecapture.html#Quality-enum
                            model: ["Very High", "Normal", "Low", "Very Low"]
                            backgroundColor: appStyle.elevatedSurface_L5
                            placeholderText: 'Select Image Size'
                            Component.onCompleted: cbCameraQuality.currentIndex = cbCameraQuality.model.indexOf(settings.curImageQuality)
                            onCurrentIndexChanged: {
                                var selected = model[currentIndex]
                                console.info("Resolution selected: " + selected);
                                if (selected === "Very High") {
                                    camControls.curCameraResolution = {"width": 1280, "height": 720}
                                } else {
                                    camControls.curCameraResolution = {"width": 640, "height": 480}
                                }
                            }
                        }
                    }
                }  // camera group box end
            }
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
