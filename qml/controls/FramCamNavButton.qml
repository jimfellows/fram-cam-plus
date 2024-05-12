import QtQuick 2.15
//import QtQuick3D 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Controls 6.0
import QtQuick.Controls.Material

Button {
    Material.theme: Material.Dark

    id: btnLeftMenu
    font.family: appStyle.fontFamily
    font.italic: true
    text: qsTr("Left Menu Button Text")
    implicitWidth: 250
    implicitHeight: 60
    flat:true  //allows dynamic color to work properly
    highlighted: false  //allows dyanmic color to work

    //custom props
    property color colorDefault: '#55aaff';
    property color colorMouseOver: appStyle.primaryColor;
    property color colorPressed: '#55aaff';
    property color hoveredIconColor: appStyle.primaryFontColor
    property int iconWidth: 35;
    property int iconHeight: 35;
    property url iconSource: 'qrc:/svgs/menu_icon.svg'
    property color activeColor: '#12cb06'
    property bool isActive: true


    QtObject {
        id: internal
        property var dynamicColor: if (btnLeftMenu.down) {
                                       btnLeftMenu.down ? colorPressed : colorDefault
                                   } else {
                                       btnLeftMenu.hovered ? colorMouseOver : colorDefault
                                   }
    }
    background: Rectangle {
        id: rectBg
        color: internal.dynamicColor
        anchors.fill: parent

        Rectangle {
            id: rectHighlightBarLeft
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            width: 8
            visible: btnLeftMenu.isActive
            color: appStyle.primaryColor
        }
        Rectangle {
            id: rectHighlightBarRight
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            width: 6
            visible: btnLeftMenu.isActive
            color: appStyle.elevatedSurface_L5
        }
    }
    contentItem: Item{
        Image {
            id: imgMenuIcon
            source: btnLeftMenu.iconSource
            sourceSize.height: iconHeight
            sourceSize.width: iconWidth
            anchors.leftMargin: 18
            anchors.left: parent.left
            height: iconHeight
            anchors.verticalCenter: parent.verticalCenter
            width: iconWidth
            fillMode: Image.PreserveAspectFit
            antialiasing: true
            mipmap: true
        }

        ColorOverlay {
            anchors.fill: imgMenuIcon
            source: imgMenuIcon
            color: btnLeftMenu.hovered ? hoveredIconColor : appStyle.iconColor
            anchors.verticalCenter: parent.verticalCenter
            antialiasing: true
            width: iconWidth
            height: iconHeight
        }

        Text {
            id: txtButtonLabel
            text: btnLeftMenu.text
            anchors.verticalCenter: parent.verticalCenter
            font: btnLeftMenu.font

            anchors.left: imgMenuIcon.right
            anchors.leftMargin: 40
            color: appStyle.secondaryFontColor
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
