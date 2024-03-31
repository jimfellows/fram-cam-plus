import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

ProgressBar {
    id: control
    value: 0.5
    padding: 2

    Material.theme: Material.Dark

    property color runningColor: appStyle.primaryColor;

    implicitHeight: 10
    implicitWidth: 200

    background: Rectangle {
        implicitWidth: control.width
        implicitHeight: control.height
        color: appStyle.iconColor
        radius: 3
    }

    contentItem: Item {
        implicitWidth: control.width
        implicitHeight: control.height * 0.97

        // Progress indicator for determinate state.
        Rectangle {
            width: control.visualPosition * parent.width
            height: parent.height
            radius: 2
            color: control.runningColor
            visible: !control.indeterminate
        }

        // Scrolling animation for indeterminate state.
        Item {
            anchors.fill: parent
            visible: control.indeterminate
            clip: true

            Row {
                spacing: 20

                Repeater {
                    model: control.width / 40 + 1

                    Rectangle {
                        color: "#17a81a"
                        width: 20
                        height: control.height
                    }
                }
                XAnimator on x {
                    from: 0
                    to: -40
                    loops: Animation.Infinite
                    running: control.indeterminate
                }
            }
        }
    }
}