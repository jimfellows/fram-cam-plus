import QtQuick 2.0

Rectangle {
    id: root
    color: "#121212"
    implicitHeight: 417
    implicitWidth: 480

    Rectangle {
        id: rectImageArea
        opacity: 0.1
        color: "#ffffff"
        radius: 8
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: rectKeyboardArea.top
        anchors.bottomMargin: 8
        anchors.rightMargin: 216
        anchors.topMargin: 8
        anchors.leftMargin: 8

        Image {
            id: imgPreview
            anchors.fill: parent
            source: "qrc:/qtquickplugin/images/template_image.png"
            anchors.rightMargin: 5
            anchors.leftMargin: 5
            anchors.bottomMargin: 5
            anchors.topMargin: 5
            fillMode: Image.PreserveAspectFit
        }
    }

    Rectangle {
        id: rectEditArea
        width: 200
        opacity: 0.1
        color: "#ffffff"
        radius: 8
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: rectKeyboardArea.top
        anchors.leftMargin: 272
        anchors.bottomMargin: 8
        anchors.topMargin: 8
    }

    Rectangle {
        id: rectKeyboardArea
        y: 217
        height: 192
        opacity: 0.1
        color: "#ffffff"
        radius: 8
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 8
        anchors.rightMargin: 8
        anchors.leftMargin: 8
    }

}
