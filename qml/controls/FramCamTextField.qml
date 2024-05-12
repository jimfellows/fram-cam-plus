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
    property string titleLabelText;

    placeholderText: qsTr("This is placeholder text")
    placeholderTextColor: displayText || activeFocus ? "transparent" : appStyle.disabledFontColor
    font.family: appStyle.fontFamily

    color: root.fontColor
    font.pixelSize: fontSize

    SequentialAnimation {
        id: glow
        property int duration: 800
        property int maxGlow: 15
        PropertyAnimation { target: rectGlow; property: "visible"; to: true; }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: glow.maxGlow; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: 0; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: glow.maxGlow; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: 0; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: glow.maxGlow; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: 0; duration: glow.duration }
        PropertyAnimation { target: rectGlow; property: "visible"; to: false; }
    }
    function startGlow(color) {
        if (color === undefined) color = appStyle.accentColor
        rectBackground.color = color;
        glow.running = true;
    }
    Label {
        visible: root.titleLabelText
        text: root.titleLabelText
        anchors.bottom: parent.top
        font.family: appStyle.fontFamily
        font.underline: true
        anchors.bottomMargin: 2
        anchors.left: parent.left
        anchors.leftMargin: 3
        color: root.fontColor
        font.italic: true
        font.pixelSize: 14
    }

    background: Rectangle {
        color: "transparent"
        implicitHeight: root.implicitHeight
        implicitWidth: root.implicitWidth
        RectangularGlow {
            id: rectGlow
            anchors.fill: rectBackground
            glowRadius: 0
            spread: 0.5
            color: appStyle.accentColor
            cornerRadius: rectBackground.radius + glowRadius
            visible: false
        }
        Rectangle {
            id: rectBackground
            anchors.fill: parent
            radius: root.radius
            color: root.backgroundColor
            border.color: root.activeFocus ? root.focusedColor : root.borderColor
            border.width: root.activeFocus ? 2 : 1
        }
    }

}