
import QtQuick.Controls 6.3
import QtQuick.Layouts 1.3
import QtQuick 2.15
import Qt5Compat.GraphicalEffects

//https://www.youtube.com/watch?v=RUWMHhPqwnw&t=751s

ComboBox {
    id: root
    implicitWidth: 200
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
    property color fontColor: "white"
    property int fontSize: 18
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
            width: itemDelegate.width
            height: itemDelegate.height
            anchors.fill: parent
            spacing: 2
            Label {
                id: mylbl
                opacity: 0.9
                text: modelData
                color: root.fontColor
                font.bold: true
                font.pixelSize: root.fontSize
                Layout.leftMargin: 10
                Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
            }
            Image {
                id: imgSelected
                fillMode: Image.PreserveAspectFit
                visible: root.currentIndex === index
                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                sourceSize.height: 20
                sourceSize.width: 20
                source: "qrc:/svgs/fish.svg"
                layer {
                    enabled: true
                    effect: ColorOverlay {
                        color: root.fontColor
                    }
                }

            }
        }
    }
    background: Rectangle {
        implicitWidth: root.implicitWidth
        implicitHeight: root.implicitHeight
        color: root.backgroundColor
        radius: root.radius
    }
    contentItem: Item {
        width: root.background.width // - root.indicator.width - 10
        height: root.background.height
        anchors.fill: parent
        RowLayout {
            anchors.fill: parent
            spacing: 10
            Label {
                opacity: 0.9
                text: root.displayText
                color: root.fontColor
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
        width: root.implicitWidth
        //width: root.implicitWidth > 250 ? 250 : contentItem.implicitHeight
        padding: 4
        contentItem: ListView {
            leftMargin: 5
            implicitHeight: contentHeight
            model: root.popup.visible? root.delegateModel: null
            //clip:true
            currentIndex: root.highlightedIndex
        }
        background: Rectangle {
            anchors.fill: parent
            color: root.backgroundColor
            radius: 6

        }
    }

}
