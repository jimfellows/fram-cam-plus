import QtQuick 2.15
import QtQuick.Controls.Material
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.3
import Qt5Compat.GraphicalEffects



TextField {
    id: root

    //custom props
    property int radius: 12
    property color fontColor: appstyle.secondaryFontColor
    property int fontSize: 16
    property color backgroundColor: appstyle.elevatedSurface_L9
    property color borderColor: appstyle.iconColor
    property color focusedColor: appstyle.accentColor

    placeholderText: qsTr("This is placeholder text")
    placeholderTextColor: displayText || activeFocus ? "transparent" : appstyle.disabledFontColor
    font.family: appstyle.fontFamily

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