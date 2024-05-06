
import QtQuick 2.0
import QtQuick.Layouts 6.3
import QtQuick.Controls 6.3
import Qt5Compat.GraphicalEffects
import QtQuick.Dialogs
import QtQuick.Controls.Material

import 'qrc:/controls'

Dialog {
    id: dlg

    implicitWidth: 500
    implicitHeight: 350
    Material.theme: Material.Dark
    title: "Enter your credentials..."

    property string defaultUserName;
    property alias btnLogin: btnLogin;
    property alias tfPassword: tfPassword
    property alias tfUsername: tfUsername

    property string loginDestination;

    onLoginDestinationChanged: {
        dlg.title = 'Enter credentials for ' + loginDestination
        tfUsername.text = defaultUserName
        tfPassword.text = ''
    }

    signal loginAttempt(string username, string password)

    SequentialAnimation {
        id: shake
        property int pos
        property int startPos
        property int speed: 75
        property int margin: 40
        NumberAnimation { target: dlg; property: "x"; to: (dlg.x + shake.margin * 0.5); duration: shake.speed * 0.5;}
        NumberAnimation { target: dlg; property: "x"; to: (dlg.x - shake.margin); duration: shake.speed}
        NumberAnimation { target: dlg; property: "x"; to: (dlg.x + shake.margin); duration: shake.speed}
        NumberAnimation { target: dlg; property: "x"; to: (dlg.x - shake.margin * 0.5); duration: shake.speed * 0.5;}
        NumberAnimation { target: dlg; property: "x"; to: shake.startPos; duration: shake.speed;}

        onRunningChanged: {
            // stash original pos of dlg so we always shake back to that value
            // had some weirdness when the shake back and forth didnt return it to its old pos, this hacks it
            if (running) {
                startPos = dlg.x
            }
        }
    }

    function loginFailed() {
        shake.running = true
        tfUsername.borderColor = appStyle.errorColor
        tfPassword.borderColor = appStyle.errorColor
    }

    contentItem: Rectangle {
        color: appStyle.elevatedSurface_L9
        radius: 10
        ColumnLayout {
            spacing: 5
            anchors {
                fill: parent
                topMargin: 10
                leftMargin: 10
                bottomMargin: 10
                rightMargin: 10
            }
            FramCamTextField {
                id: tfUsername
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredHeight: 65
                placeholderText: "Enter Username..."
            }
            FramCamTextField {
                id: tfPassword
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredHeight: 65
                placeholderText: "Enter password..."
                passwordCharacter: "*"
                echoMode: TextInput.Password
            }
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignHCenter
                FramCamButton {
                    id: btnLogin
                    text: "Login"
                    Layout.preferredHeight: 75
                    Layout.preferredWidth: 150
                    onClicked: {
                        dlg.loginFailed()
                        if (!tfUsername.text | !tfPassword.text) {
                            console.info("Please enter user/pw")
                        } else {
                            //loginAttempt(tfUsername.text, tfPassword.text)
                        }
                    }
                }
                FramCamButton {
                    text: "Cancel"
                    Layout.preferredHeight: 75
                    Layout.preferredWidth: 150
                    pressedColor: appStyle.errorColor
                    onClicked: dlg.close()
                }
            }
        }
    }

}