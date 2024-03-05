import QtQuick 2.0
import QtQuick.Layouts 6.3

Rectangle {
    id: root
    color: "#121212"
    border.color: "gray"
    implicitHeight: 417
    implicitWidth: 480
    radius: 8

    property string imageSource;

    GridLayout {
        id: gridLayout
        anchors {
            fill: parent
            leftMargin: 5
            rightMargin: 5
            topMargin: 5
            bottomMargin: 5
        }
        rows: 2
        columns: 2

        Rectangle {
            id: rectImageArea
            Layout.preferredWidth: parent.width * 0.6 - 5
            Layout.preferredHeight: parent.height * 0.5 - 5
            opacity: 0.1
            color: "#ffffff"
            radius: 8

            Image {
                id: imgPreview
                anchors.fill: parent
                source: "file:///" + root.imageSource
                fillMode: Image.PreserveAspectFit
            }
        }
        Rectangle {
            id: rectEditArea
            Layout.preferredWidth: parent.width * 0.4 - 5
            Layout.preferredHeight: parent.height * 0.5 - 5
            opacity: 0.1
            color: "#ffffff"
            radius: 8
        }
        Rectangle {
            id: rectKeyboardArea
            Layout.preferredWidth: parent.width
            Layout.preferredHeight: parent.height * 0.5 - 5
            Layout.columnSpan: 2
            opacity: 0.1
            color: "#ffffff"
            radius: 8
        }
    }

}
