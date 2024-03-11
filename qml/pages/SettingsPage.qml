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
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: 200
                title: 'Network'
                ColumnLayout {
                    RowLayout {
                        spacing: 10

                        Label {
                            text: "Vessel Subnet"
                            color: appstyle.secondaryFontColor
                            font.pixelSize: 18
                            font.family: appstyle.fontFamily
                        }

                        FramCamComboBox {
                            Layout.preferredWidth: 200
                            Layout.preferredHeight: 200
                            //implicitHeight: 400
                            model: ['192.254.243', '192.254.242', '127.0.0.1 (test)']
                        }

                    }
                }
            }
            FramCamGroupBox {
                Layout.preferredWidth: parent.width
                Layout.preferredHeight: 200
                title: 'UI'
                ColumnLayout {
                    RowLayout {
                        spacing: 10
                        Label {
                            text: "Color Mode"
                            color: appstyle.secondaryFontColor
                            font.pixelSize: 18
                            font.family: appstyle.fontFamily
                        }
                        FramCamComboBox {
                            width: 200
                            height: 200
                            model: ['Dark', 'Light', 'Gray']
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
