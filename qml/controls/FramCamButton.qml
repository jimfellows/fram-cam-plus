import QtQuick 2.15
import QtQuick.Controls.Material
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.3
import Qt5Compat.GraphicalEffects

//https://www.youtube.com/watch?v=2CEyIeimruc
Button {
 id: root
 implicitWidth: 200
 implicitHeight: 40

 //custom props
 property color backgroundColor: appStyle.elevatedSurface_L9
 property color fontColor: appStyle.primaryFontColor
 property color disabledFontColor: appStyle.disabledFontColor
 property color disabledBackgroundColor: appStyle.disabledFontColor.darker(1.2)
 property color disabledBorderColor: appStyle.disabledFontColor.darker(1.2)
 property color hoverColor: '#55aaff';
 property color pressedColor: appStyle.primaryColor
 property color pressedFontColor: appStyle.primaryFontColor
 property color borderColor: appStyle.iconColor
 property int borderWidth: 1
 property color iconColor: appStyle.iconColor
 property int fontSize: 16
 property int radius: 5
 property string iconSource
 property alias img: img;


 text: qsTr('')

 // text styling
 contentItem:
    AnimatedImage {
        id: img
        source: root.iconSource
        anchors.fill: root
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: 10
        anchors.bottomMargin: 10
        antialiasing: true
        fillMode: Image.PreserveAspectFit
        smooth: true
        mipmap: true
        layer {
            enabled: true
            effect: ColorOverlay {
                color: root.checked || root.down ? root.pressedFontColor : root.iconColor
            }
        }
    }
    Text {
        id: buttonText
        text: root.text
        color: root.enabled ? root.fontColor : root.disabledFontColor
        font.pixelSize: root.fontSize
        font.family: appStyle.fontFamily
        font.weight: Font.Thin
        elide: Text.ElideRight
        anchors {
            verticalCenter: parent.verticalCenter
            horizontalCenter: parent.horizontalCenter
        }
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        visible: !root.iconSource
    }

 // background styling
 background: Rectangle {
    implicitWidth: root.width
    implicitHeight: root.height
    color: root.down || root.checked ? root.pressedColor : root.enabled ? root.backgroundColor : root.disabledBackgroundColor
    radius: root.radius
    layer.enabled: true
    border.color: root.enabled ? root.borderColor : root.disabledBorderColor
    border.width: root.borderWidth
    layer.effect: DropShadow {
        transparentBorder: true
        color: root.down ? root.pressedColor : root.backgroundColor
        samples: 20
    }
 }
}
