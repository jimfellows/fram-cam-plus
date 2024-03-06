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
 property color textColor: appstyle.primaryFontColor
 property color hoverColor: '#55aaff';
 property color pressedColor: appstyle.primaryColor
 property color pressedTextColor: appstyle.primaryFontColor
 property color borderColor: appstyle.iconColor
 property color iconColor: appstyle.iconColor
 property int radius: 5
 property string iconSource


 text: qsTr('Custom Button')

 // text styling
 contentItem:
    Image {

        source: root.iconSource
        anchors.fill: root
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: 10
        anchors.bottomMargin: 10
        layer {
            enabled: true
            effect: ColorOverlay {
                color: root.checked || root.down ? root.pressedTextColor : root.iconColor
            }
        }
    }
    Text {
        id: buttonText
        text: root.text
        color: root.textColor
        font.pixelSize: 12
        font.family: 'Arial'
        font.weight: Font.Thin
        elide: Text.ElideRight
        verticalAlignment: Text.AlignVCenter
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
