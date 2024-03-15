
import QtQuick 2.15
import QtQuick.Controls.Material
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.3
import Qt5Compat.GraphicalEffects


GroupBox {
    id: root
    title: qsTr("GroupBox")
    implicitWidth: 300
    implicitHeight: 150

    property color fontColor: appstyle.secondaryFontColor
    property string fontFamily: appstyle.fontFamily
    property int fontPixelSize: 16
    property color borderColor: appstyle.iconColor
    property real labelIndentation: 0.02  // percent into width that label is pushed

    label: Label {
        id: lbl
        font.family: root.fontFamily
        color: root.fontColor
        text: qsTr(root.title)
        anchors.left: root.left
        anchors.top: root.top
        anchors.leftMargin: root.width * root.labelIndentation
        anchors.topMargin: height * 0.5 * -1
        font.pixelSize: root.fontPixelSize
    }

    background: Item {
        id: box
        property string borderColor: appstyle.iconColor
        property int borderWidth: 2
        onWidthChanged: canvas.requestPaint()
        onHeightChanged: canvas.requestPaint()

        Canvas {
            id: canvas
            anchors.fill: parent
            antialiasing: true
            onPaint: {
                var ctx = canvas.getContext('2d')
                ctx.strokeStyle = box.borderColor
                ctx.lineWidth = box.borderWidth
                ctx.beginPath()
                ctx.moveTo(root.width * root.labelIndentation - 3, 0)  // start at 0.05 of width + 3 pixels of margin to left o label
                ctx.lineTo(0, 0)  // top left
                ctx.lineTo(0, height)  // draw to bottom left
                ctx.lineTo(width, height)  // draw to bottom right
                ctx.lineTo(width, 0)  // draw to top right
                ctx.lineTo(root.width * root.labelIndentation + 6 + lbl.width, 0)  // end on the other side of label (3 + 3 = 6 for both sides of margin)
                ctx.stroke()
            }
        }
    }
}