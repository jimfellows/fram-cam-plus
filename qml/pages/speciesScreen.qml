import QtQuick 2.0

Item {
    Rectangle {
        id: rectangle
        color: "#f29a14"
        anchors.fill: parent

        Image {
            id: image
            width: 100
            height: 100
            anchors.verticalCenter: parent.verticalCenter
            source: "../../resources/images/svgs/coral_1.svg"
            anchors.horizontalCenter: parent.horizontalCenter
            fillMode: Image.PreserveAspectFit
        }
    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
