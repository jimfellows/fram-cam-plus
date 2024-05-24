
import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Dialogs

import 'qrc:/controls'

Dialog {
    id: dlg

    x: (parent.width - width) / 2
    y: (parent.height - height) / 2

    modal: false

    implicitWidth: 700
    implicitHeight: 500

    title: "Logging Console"

    contentItem: Rectangle {
        color: appStyle.elevatedSurface_L9
        radius: 10
        ColumnLayout {
            spacing: 5
            anchors {
                fill: parent
                topMargin: 5
                leftMargin: 5
                bottomMargin: 5
                rightMargin: 5
            }
            Label {
                id: lblTitle
                Layout.fillWidth: true
                color: appStyle.secondaryFontColor
                font.pixelSize: 16
                font.underline: true
                font.italic: true
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                text: "FRAMCam App Log"
            }
            TextArea {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: dlg.height * 0.8
            }
            FramCamButton {
                id: btnClose
                text: "Close"
                Layout.alignment: Qt.AlignHCenter
                onClicked: dlg.close()
            }
        }
    }

}