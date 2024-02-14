import QtQuick 2.15

import QtQuick.Controls 6.0

Button {
 id: btnCustom
 text: qsTr('Custom Button')
 implicitWidth: 200
 implicitHeight: 40

 //custom props
 property color colorDefault: '#55aaff';
 property color colorMouseOver: '#55aaff';
 property color colorPressed: '#55aaff';

 QtObject {
     id: internal
     property var dynamicColor: if (btnCustom.down) {
                                    btnCustom.down ? colorPressed : colorDefault

                                } else {
                                    btnCustom.hovered ? colorMouseOver : colorDefault
                                }
 }



 background: Rectangle {
       color: internal.dynamicColor
           radius: 10
 }
 contentItem: Item {
    Text {
         id: textBtn
         text: btnCustom.text
         color: '#ffffff'
         anchors.verticalCenter: parent.verticalCenter
         anchors.horizontalCenter: parent.horizontalCenter
     }
 }
}
