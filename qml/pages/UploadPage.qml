import QtQuick 2.0
import Qt5Compat.GraphicalEffects

Item {
    Rectangle {
        id: rectangle
        color: appStyle.elevatedSurface_L5
        anchors.fill: parent
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 5
        anchors.topMargin: 5
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
                    color: appStyle.iconColor
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
