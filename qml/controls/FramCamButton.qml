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
 property color backgroundColor: appstyle.elevatedSurface_L9
 property color fontColor: appstyle.primaryFontColor
 property color disabledFontColor: appstyle.disabledFontColor
 property color hoverColor: '#55aaff';
 property color pressedColor: appstyle.primaryColor
 property color pressedFontColor: appstyle.primaryFontColor
 property color borderColor: appstyle.iconColor
 property color iconColor: appstyle.iconColor
 property int fontSize: 16
 property int radius: 5
 property string iconSource
 property alias img: img;


 text: qsTr('Custom Button')

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
        font.family: appstyle.fontFamily
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
    color: root.down || root.checked ? root.pressedColor : root.backgroundColor
    radius: root.radius
    layer.enabled: true
    border.color: root.borderColor
    layer.effect: DropShadow {
        transparentBorder: true
        color: root.down ? root.pressedColor : root.backgroundColor
        samples: 20
    }
 }
}
