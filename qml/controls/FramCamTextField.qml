import QtQuick 2.15
import QtQuick.Controls.Material
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.3
import Qt5Compat.GraphicalEffects



TextField {
    id: root

    //custom props
    property int radius: 12
    property color fontColor: appStyle.secondaryFontColor
    property int fontSize: 16
    property color backgroundColor: appStyle.elevatedSurface_L9
    property color borderColor: appStyle.iconColor
    property color focusedColor: appStyle.accentColor

    placeholderText: qsTr("This is placeholder text")
    placeholderTextColor: displayText || activeFocus ? "transparent" : appStyle.disabledFontColor
    font.family: appStyle.fontFamily

    color: root.fontColor
    font.pixelSize: fontSize

    background: Rectangle {
        implicitHeight: root.implicitHeight
        implicitWidth: root.implicitWidth
        radius: root.radius
        color: root.backgroundColor
        border.color: root.activeFocus ? root.focusedColor : root.borderColor
        border.width: root.activeFocus ? 2 : 1

    }

}