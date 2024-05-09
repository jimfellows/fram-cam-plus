
import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Dialogs
import QtQuick.Controls.Material

import 'qrc:/controls'

Dialog {
    id: dlg

    x: (parent.width - width) / 2
    y: (parent.height - height) / 2

    implicitWidth: 500
    implicitHeight: 300
    Material.theme: Material.Dark
    title: "Yes/No"

    signal accepted;
    signal declined;

    property string message;
    property string action;
    property string acceptButtonText: "Accept"
    property string declineButtonText: "Decline"

    property alias lblMessage : lblMessage
    property alias lblAction : lblAction
    property alias btnAccept: btnAccept;
    property alias btnDecline: btnDecline;

    contentItem: Rectangle {
        color: appStyle.elevatedSurface_L9
        radius: 10
        ColumnLayout {
            spacing: 10
            anchors {
                fill: parent
                topMargin: 10
                leftMargin: 10
                bottomMargin: 10
                rightMargin: 10
            }
            Label {
                id: lblMessage
                Layout.fillWidth: true
                color: appStyle.secondaryFontColor
                font.pixelSize: 16
                horizontalAlignment: Text.AlignHCenter
                text: dlg.message
            }
            Label {
                id: lblAction
                Layout.fillWidth: true
                color: appStyle.secondaryFontColor
                font.pixelSize: 16
                horizontalAlignment: Text.AlignHCenter
                text: dlg.action
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                FramCamButton {
                    id: btnAccept
                    text: dlg.acceptButtonText
                    Layout.preferredHeight: 75
                    Layout.preferredWidth: 150
                    onClicked: dlg.accepted()

                }
                FramCamButton {
                    id: btnDecline
                    text: dlg.declineButtonText
                    Layout.preferredHeight: 75
                    Layout.preferredWidth: 150
                    pressedColor: appStyle.errorColor
                    onClicked: dlg.declined()
                }
            }
        }
    }

}