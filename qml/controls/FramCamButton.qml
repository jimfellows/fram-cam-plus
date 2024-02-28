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
 property color backgroundColor: '#55aaff';
 property color textColor: "black"
 property color hoverColor: '#55aaff';
 property color pressedColor: 'green';
 property color pressedTextColor: "black"

 property string rightIconSource;

 text: qsTr('Custom Button')

 // text styling
 contentItem: Row {
    anchors.fill: parent
    anchors.horizontalCenter: parent.horizontalCenter
    spacing: 10
    Text {
        id: buttonText
        text: root.text
        color: root.textColor
        font.pixelSize: 12
        font.family: 'Arial'
        font.weight: Font.Thin
        anchors.verticalCenter: parent.verticalCenter
        //anchors.horizontalCenter: parent.horizontalCenter
        //horizontalAlignment: Text.AlignHCenter
        elide: Text.ElideRight
    }
    Image {
        id: imgRightIcon
        source: root.rightIconSource
        fillMode: Image.PreserveAspectFit
        anchors.left: buttonText.right
        anchors.verticalCenter: buttonText.verticalCenter
        sourceSize.height: 30
        sourceSize.width: 30
    }
 }

 // background styling
 background: Rectangle {
    implicitWidth: root.width
    implicitHeight: root.height
    color: root.down ? root.pressedColor : root.backgroundColor
    radius: 5
    layer.enabled: true
    layer.effect: DropShadow {
        transparentBorder: true
        color: root.down ? root.pressedColor : root.backgroundColor
        samples: 20
    }
 }
}
