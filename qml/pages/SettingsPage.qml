import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects

import 'qrc:/qml'

Item {

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
        ColumnLayout {
            id: columnLayout
            anchors.fill: parent
            anchors.leftMargin: 5
            anchors.rightMargin: 5
            FramCamGroupBox {
                id: gbNetwork
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: 200
                title: 'Network'
                property int labelWidth: 200
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
                            Layout.preferredWidth: 400
                            Layout.preferredHeight: 50
                            backgroundColor: appstyle.elevatedSurface_L5
                            model: ['192.254.243', '192.254.242', '127.0.0.1']
                            placeholderText: 'Select a vessel subnet...'
                            onCurrentIndexChanged: {
                                settings.curVesselSubnet = model[currentIndex]
                            }
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
                            Layout.preferredHeight: 50
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
                        FramCamButton {
                            text: 'Browse'
                            Layout.preferredHeight: 50
                        }
                    }
                }

            }
            FramCamGroupBox {
                id: gbUi
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: 200
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
                            Layout.preferredHeight: 50
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
