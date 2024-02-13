import QtQuick 2.15
//import QtQuick3D 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Controls 6.0

Button {
    id: btnWindowControl
    implicitWidth: 35
    implicitHeight: 35
    flat:true  //allows dynamic color to work properly
    highlighted: false  //allows dyanmic color to work

    //custom props
    property color colorDefault: '#55aaff';
    property color colorMouseOver: '#0085CA';
    property color colorPressed: '#55aaff';
    property color iconColor: '#000000';

    property url iconSource: "../../resources/images/svgs/minimize_icon.svg"

    QtObject {
        id: internal
        property var dynamicColor: if (btnWindowControl.down) {
                                       btnWindowControl.down ? colorPressed : colorDefault
                                   } else {
                                       btnWindowControl.hovered ? colorMouseOver : colorDefault
                                   }
    }
    background: Rectangle {
        id: rectBg
        color: internal.dynamicColor

        Image {
            id: imgMenuIcon
            source: btnWindowControl.iconSource
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
            height: 16
            width: 16
            fillMode: Image.PreserveAspectFit
        }

        ColorOverlay {
            anchors.fill: imgMenuIcon
            source: imgMenuIcon
            color: btnWindowControl.iconColor  // make image like it lays under red glass
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
