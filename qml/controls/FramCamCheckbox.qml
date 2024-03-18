import QtQuick 2.15
import QtQuick.Controls.Material
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.3
import Qt5Compat.GraphicalEffects

CheckBox {
    id: control
    text: qsTr("")
    checked: false
    property color checkColor: appstyle.primaryColor

    indicator: Rectangle {
        width: control.width
        height: control.height
        x: control.leftPadding
        y: parent.height / 2 - height / 2
        radius: 3
        border.color: control.down ? appstyle.surfaceColor : appstyle.iconColor
        color: appstyle.elevatedSurface_L9

        Image {
            source: "qrc:/svgs/check.svg"
            width: parent.width * 0.8
            height: parent.height * 0.8
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            fillMode: Image.PreserveAspectFit
            visible: control.checked
            antialiasing: true
            smooth: true
            mipmap: true
            layer {
                enabled: true
                effect: ColorOverlay {
                    color: checkColor
                }
            }
        }
        /*
        Rectangle {
            width: parent.width * 0.6
            height: parent.height * 0.6
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            radius: 2
            color: control.down ? appstyle.surfaceColor : appstyle.primaryColor
            visible: control.checked
        }
        */
    }

    contentItem: Text {
        text: control.text
        font: control.font
        opacity: enabled ? 1.0 : 0.3
        color: control.down ? "#17a81a" : "#21be2b"
        verticalAlignment: Text.AlignVCenter
        leftPadding: control.indicator.width + control.spacing
    }
}