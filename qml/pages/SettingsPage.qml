import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects

import 'qrc:/qml'

Item {
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
                            Layout.preferredWidth: 400
                            Layout.preferredHeight: 50
                            backgroundColor: appstyle.elevatedSurface_L5
                            model: ['192.254.243', '192.254.242', '127.0.0.1 (test)']
                            placeholderText: 'Select a vessel subnet...'
                        }
                        FramCamButton {
                            text: 'Ping'
                            Layout.preferredHeight: 50
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
