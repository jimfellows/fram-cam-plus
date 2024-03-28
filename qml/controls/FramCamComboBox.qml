
import QtQuick.Controls 6.3
import QtQuick.Layouts 1.3
import QtQuick 2.15
import Qt5Compat.GraphicalEffects
import QtQuick.Controls.Material


//https://www.youtube.com/watch?v=RUWMHhPqwnw&t=751s

ComboBox {
    id: root
    implicitWidth: 200
    implicitHeight: 50
    currentIndex: -1

    Material.theme: Material.Dark

    //custom props
    property color backgroundColor: appStyle.elevatedSurface_L5;
    property color borderColor: appStyle.iconColor
    property color fontColor: appStyle.secondaryFontColor
    property color hoveredColor: appStyle.elevatedSurface_L5.darker(0.7)
    property int fontSize: 18
    property real radius: 12;
    property string placeholderText: "";
    property bool italicDisplay: false;
    property int maxPopupHeight: 10000;

    /*
    delegate here represents each item in the popup aka the drop down,
    but not the actual backdrop of the popup
    */
    delegate: ItemDelegate {
        id: popupRow
        implicitHeight: root.height
        implicitWidth: root.width
        anchors.leftMargin: -30

        // popup row background rectangle
        background: Rectangle {
            color: root.currentIndex === index || popupRow.hovered ? root.backgroundColor.darker(0.7) : root.backgroundColor
            anchors.fill: parent
            anchors.leftMargin: -50
            anchors.rightMargin: -20
            radius: root.radius
        }
        // row layout for the popup row
        RowLayout {
            anchors.fill: parent
            spacing: 2
            Rectangle {
                Layout.preferredWidth: 5
                Layout.fillHeight: true
                radius: root.radius
                visible: root.currentIndex === index
                color: appStyle.accentColor
            }
            Label {
                id: popupLabel
                //opacity: 0.9
                text: model[root.textRole]
                color: popupRow.hovered ? appStyle.primaryFontColor : root.fontColor
                font.bold: true
                font.pixelSize: root.fontSize
                font.family: appStyle.fontFamily
                Layout.leftMargin: 10
                Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
            }
            Image {
                id: imgSelected
                fillMode: Image.PreserveAspectFit
                visible: root.currentIndex === index
                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                sourceSize.height: 20
                sourceSize.width: 20
                source: "qrc:/svgs/circle_selection.svg"
                layer {
                    enabled: true
                    effect: ColorOverlay {
                        color: appStyle.accentColor
                    }
                }
            }
        }
    }  // popup row item delegate

    indicator: Canvas {
        id: canvas
        x: root.width - width - root.rightPadding
        y: root.topPadding + (root.availableHeight - height) * 0.8
        width: 12
        height: 8
        contextType: "2d"

        Connections {
            target: root
            function onPressedChanged() { canvas.requestPaint(); }
        }

        onPaint: {
            context.reset();
            context.strokeStyle = root.fontColor
            context.lineWidth = 1
            context.beginPath()
            context.moveTo(0, 0);
            context.lineTo(width / 2, height);
            context.lineTo(width, 0);
            context.closePath();
            context.stroke()
        }
    }

    /*
    background here represents that of the button independent of the
    popup/drop down that is displayed, displayed when combobox is collapsed
    */
    background: Rectangle {
        id: rectButton
        implicitWidth: root.width
        implicitHeight: root.height
        color: root.backgroundColor
        radius: root.radius
        border.color: root.borderColor
    }
    /*
    contentItem represents content of button shown when combobox is collapsed
    */
    contentItem: Item {
        id: ciButton
        anchors.fill: parent
        RowLayout {
            anchors.fill: parent
            spacing: 10
            Label {
                opacity: 0.9
                text: root.currentIndex === -1 ? root.placeholderText : root.displayText
                font.italic: root.currentIndex === -1
                color: root.fontColor
                font.bold: true
                font.pixelSize: root.fontSize
                font.family: appStyle.fontFamily
                Layout.fillWidth: true
                verticalAlignment: Image.AlignVCenter
                Layout.leftMargin: 10
            }
        }
    }
    /*
    popup represents the backdrop of the dropdown menu
    */
    popup: Popup {
        id: popup
        y: root.height + 2 // set drop down just below main button
        width: root.width + 20  // bump out drop down slightly
        implicitHeight: contentItem.implicitHeight
        padding: 4
        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight > root.maxPopupHeight ? root.maxPopupHeight : contentHeight
            model: root.popup.visible ? root.delegateModel : null
            currentIndex: root.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator { }
        }
        background: Rectangle {
            id: rectPopup
            anchors.fill: parent
            color: root.backgroundColor
            radius: root.radius
            visible: true
            border.color: root.borderColor
        }
        /*
        enter: Transition {
            NumberAnimation {
                property: "height";
                from: 0;
                to: root.implicitHeight
                easing.type: Easing.InOutQuint;
                duration: 300;
            }
        }
        exit: Transition {
            NumberAnimation {
                property: "height";
                from: root.implicitHeight;
                to: 0
                easing.type: Easing.InOutQuint;
                duration: 300;
            }
        }
        */
    }
}
