import QtQuick 2.0
import QtQuick.Layouts 6.3

Rectangle {
    id: root
    color: "#121212"
    implicitHeight: 417
    implicitWidth: 480
    radius: 8
    ColumnLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredWidth: 500
            Rectangle {
                id: rectImageArea
                opacity: 0.1
                color: "#ffffff"
                radius: 8
                implicitWidth: 50
                implicitHeight: 50
                anhohrs
                Image {
                    id: imgPreview
                    anchors.fill: parent
                    source: "qrc:/svgs/down_arrow.svg"
                    anchors.rightMargin: 5
                    anchors.leftMargin: 5
                    anchors.bottomMargin: 5
                    anchors.topMargin: 5
                    fillMode: Image.PreserveAspectFit
                }
            }

            Rectangle {
                id: rectEditArea
                x: 272
                width: 200
                opacity: 0.1
                color: "#ffffff"
                radius: 8
            }

        }
        RowLayout {
            Rectangle {
                id: rectKeyboardArea
                y: 217
                height: 192
                opacity: 0.1
                color: "#ffffff"
                radius: 8
            }
        }

    }




}
