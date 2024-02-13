
import QtQuick.Controls 6.3
import QtQuick.Layouts 1.3
import QtQuick 2.15

//https://www.youtube.com/watch?v=RUWMHhPqwnw&t=751s

ComboBox {
    id: root
    implicitWidth: 400
    implicitHeight: 55
    model: [
        '202303008001',
        '202303008002',
        '202303008003',
        '202303008004'
    ]

    //custo props
    property color backgroundColor: "transparent";
    property color borderColor: "black"
    property color textColor: "white"
    property int textSize: 18
    property real radius: 12;


    delegate: ItemDelegate {
        id: itemDelegate
        height: root.implicitHeight
        width: root.implicitWidth

        background: Rectangle {
            color: root.backgroundColor
            anchors.fill: parent
            radius: root.radius
        }
        RowLayout {
            Layout.alignment: Qt.AlignVCenter
            width: itemDelegate.width
            height: itemDelegate.height
            anchors.fill: parent
            Layout.leftMargin: 10
            Layout.rightMargin: 10
            spacing: 10

            Label {
                id: mylbl
                opacity: 0.9
                text: modelData
                color: root.textColor
                font.bold: true
                font.pixelSize: root.textSize
//                Layout.fillWidth: true
//                horizontalAlignment: Text.AlignLeft
//                verticalAlignment: Text.AlignVCenter
                Layout.leftMargin: 10
            }
            Image {
                id: imgSelected
                fillMode: Image.PreserveAspectFit
                visible: root.currentIndex === index
//                anchors.right: parent.right
                sourceSize.height: 50
                sourceSize.width: 50
                anchors.left: mylbl.right
//                verticalAlignment: Image.AlignVCenter
//                horizontalAlignment: Image.AlignRight

//                Layout.alignment: Qt.AlignVCenter
//                Layout.rightMargin: 10
                source: "../../resources/images/svgs/check_basic.svg"
            }
/*
            ColorOverlay {
                source: imgSelected
                color: root.textColor
                anchors.top: imgSelected.top
                anchors.bottom: imgSelected.bottom
                antialiasing: true
                width: imgSelected.width
                height: imgSelected.height
            }
            */
        }

    }
    background: Rectangle {
        implicitWidth: root.implicitWidth
        implicitHeight: root.implicitHeight
        color: root.backgroundColor
        radius: root.radius
    }
    contentItem: Item {
        width: root.background.width - root.indicator.width - 10
        height: root.background.height
        RowLayout {
            anchors.fill: parent
            spacing: 10
            Label {
                opacity: 0.9
                text: root.displayText
                color: "white"
                font.bold: true
                font.pixelSize: root.fontSize
                Layout.fillWidth: true
                verticalAlignment: Image.AlignVCenter
                Layout.leftMargin: 10
            }
        }
    }
    popup: Popup {
        y: root.height + 2
        width: root.implicitWidth > 250 ? 250 : contentItem.implicitHeight
        padding: 4
        contentItem: ListView {
            leftMargin: 5
            implicitHeight: contentHeight
            model: root.popup.visible? root.delegateModel: null
            clip:true
            currentIndex: root.highlightedIndex
        }
        background: Rectangle {
            anchors.fill: parent
            color: root.backgroundColor
            radius: 6

        }
    }

}
