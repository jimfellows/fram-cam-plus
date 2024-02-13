import QtQuick 2.15
//import QtQuick3D 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Controls 6.0

Button {
    id: btnToggle
    implicitWidth: 70
    implicitHeight: 60
    flat:true  //allows dynamic color to work properly
    highlighted: false  //allows dyanmic color to work
    //custom props
    property color colorDefault: '#55aaff';
    property color colorMouseOver: '#0085CA';
    property color colorPressed: '#55aaff';

    QtObject {
        id: internal
        property var dynamicColor: if (btnToggle.down) {
                                       btnToggle.down ? colorPressed : colorDefault
                                   } else {
                                       btnToggle.hovered ? colorMouseOver : colorDefault
                                   }
    }
//    flat:true
//    highlighted:true
    background: Rectangle {
        id: rectBg
        color: internal.dynamicColor

        Image {
            id: imgMenuIcon
            source: '../../resources/images/svgs/menu_icon.svg'
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            height: 40
            width: 40
            fillMode: Image.PreserveAspectFit
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
