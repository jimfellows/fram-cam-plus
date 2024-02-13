import QtQuick 2.0

Item {
    Rectangle {
        id: rectangle
        color: "#8413a2"
        anchors.fill: parent

        Image {
            id: image
            width: 100
            height: 100
            anchors.verticalCenter: parent.verticalCenter
            source: "../../resources/images/svgs/magnifying_glass.svg"
            anchors.horizontalCenter: parent.horizontalCenter
            fillMode: Image.PreserveAspectFit
        }
    }

}
