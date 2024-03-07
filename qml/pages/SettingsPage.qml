import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects

Item {
    Rectangle {
        id: rectBg
        color: appstyle.elevatedSurface_L5
        anchors.fill: parent
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 5
        anchors.topMargin: 5
        /*
        ColumnLayout {
            id: columnLayout
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 100
            anchors.topMargin: 0
            anchors.leftMargin: 0
            anchors.rightMargin: 0

            RowLayout {
                id: rowLayout
                width: 100
                height: 100
                Layout.fillWidth: true

                Label {
                    id: label
                    text: qsTr("")
                }
            }
        }
        */
        Image {
            id: image
            width: 100
            height: 100
            anchors.verticalCenter: parent.verticalCenter
            source: "qrc:/svgs/construction_sign.svg"
            anchors.horizontalCenter: parent.horizontalCenter
            fillMode: Image.PreserveAspectFit
            layer {
                enabled: true
                effect: ColorOverlay {
                    color: appstyle.iconColor
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
