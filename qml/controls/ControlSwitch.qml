import QtQuick 2.15
import QtQuick.Controls 6.0


Switch {
    id: control



    //custom props
    property color checkedColor: "#17a81a";
    property color uncheckedColor: "#ffffff"
    property string onText: "ON"
    property string offText: "OFF"
    property string titleText: "MY CONTROL"
    property color titleColor: "white"
    property int titleFontSize: 20
    property int switchWidth: 100
    property int switchHeight: 35

    indicator: Rectangle {
        id: rectIndicator
        implicitWidth: control.switchWidth
        implicitHeight: control.switchHeight
//        x: control.leftPadding
        y: parent.height / 2 - height / 2
        radius: 13
        color: control.checked ? checkedColor : uncheckedColor
        border.color: control.checked ? checkedColor : "#cccccc"


        Rectangle {
            x: control.checked ? parent.width - width : 0
            width: 52
            height: 35
            radius: 13
            color: control.down ? "#cccccc" : "#ffffff"
            border.color: control.checked ? (control.down ? "#17a81a" : "#21be2b") : "#999999"
            Label {
                text: control.position === 1 ? control.onText : control.offText
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenter: parent.horizontalCenter
                font.bold: control.position === 1
                font.pixelSize: 20
            }
        }
    }

    contentItem: Text {
        id: title
        text: control.titleText
        font.pixelSize: control.titleFontSize
        opacity: enabled ? 1.0 : 0.3
        color: enabled ? control.titleColor: "grey"
        verticalAlignment: Text.AlignVCenter
//        anchors.left: parent.left
//        anchors.right: parent.right
        anchors.horizontalCenter: rectIndicator.horizontalCenter
        horizontalAlignment: Text.AlignHCenter
        bottomPadding: control.indicator.height + 20
    }
}
