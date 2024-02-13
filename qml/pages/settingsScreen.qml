import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3

Item {
    Rectangle {
        id: rectBg
        color: "#0008680f"
        anchors.fill: parent

        ColumnLayout {
            id: columnLayout
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 100
            anchors.topMargin: 0
            anchors.leftMargin: 0
            anchors.rightMargin: 0

            RowLayout {
                id: rowLayout
                width: 100
                height: 100
                Layout.fillWidth: true

                Label {
                    id: label
                    text: qsTr("")
                }
            }
        }
    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
