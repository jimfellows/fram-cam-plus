import QtQuick 2.0
import Qt5Compat.GraphicalEffects
import QtQuick.Layouts 6.3

import 'qrc:/controls'

Item {
    Component.onCompleted: cloudUploader.checkAvailableNetworks();
    Rectangle {
        id: rectangle
        color: appStyle.elevatedSurface_L5
        anchors.fill: parent
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 5
        anchors.topMargin: 5

        ColumnLayout {
            anchors.fill: parent
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
                FramCamComboBox {
                    Layout.preferredWidth: 400
                    Layout.preferredHeight: 75
                    placeholderText: "Select a Wifi Network..."
                    model: cloudUploader.wifiNetworks
                }
                FramCamTextField {
                    Layout.preferredWidth: 300
                    Layout.preferredHeight: 65
                    placeholderText: "Enter Wifi password..."
                    passwordCharacter: "*"
                    echoMode: TextInput.Password
                }
                FramCamButton {
                    text: "Test Connection"
                    Layout.preferredHeight: 75
                    Layout.preferredWidth: 150
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
