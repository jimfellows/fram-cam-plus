
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
    property color backgroundColor: appStyle.elevatedSurface_L9;
    property color borderColor: appStyle.iconColor
    property color fontColor: appStyle.secondaryFontColor
    property color hoveredColor: appStyle.elevatedSurface_L5.darker(0.7)
    property int fontSize: 18
    property real radius: 12;
    property string placeholderText: "";
    property bool italicDisplay: false;
    property int maxPopupHeight: 10000;
    property string titleLabelText;

    SequentialAnimation {
        id: glow
        property int duration: 800
        property int maxGlow: 15
        PropertyAnimation { target: rectGlow; property: "visible"; to: true; }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: glow.maxGlow; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: 0; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: glow.maxGlow; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: 0; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: glow.maxGlow; duration: glow.duration }
        NumberAnimation { target: rectGlow; property: "glowRadius"; to: 0; duration: glow.duration }
        PropertyAnimation { target: rectGlow; property: "visible"; to: false; }
    }

    SequentialAnimation {
        id: flash
        property int duration: 100
        property int maxSize: 7
        PropertyAnimation { target: rectButton; property: "color"; to: root.fontColor; duration: 50 }
        PropertyAnimation { target: rectButton; property: "color"; to: root.backgroundColor; duration: 100 }
        PropertyAnimation { target: rectButton; property: "color"; to: root.fontColor; duration: 50 }
        PropertyAnimation { target: rectButton; property: "color"; to: root.backgroundColor; duration: 3000}
    }

    function startFlash() {
        flash.running = true;
    }

function startGlow(color) {
        if (color === undefined) color = appStyle.accentColor
        rectGlow.color = color;
        glow.running = true;
    }

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
            //color: "green"
            color: root.currentIndex === index || popupRow.hovered ? root.backgroundColor.darker(0.7) : root.backgroundColor
            anchors.fill: popupRow
            anchors.leftMargin: -50
            anchors.rightMargin: -20
            radius: root.radius
        }
        // row layout for the popup row
        RowLayout {
            anchors.fill: parent
            spacing: 2
            Rectangle {
                Layout.leftMargin: -2
                Layout.topMargin: -2
                Layout.bottomMargin: -2
                Layout.preferredWidth: 8
                Layout.fillHeight: true
                radius: root.radius
                visible: root.currentIndex === index
                color: appStyle.primaryColor
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
                        color: appStyle.primaryColor
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
        color: "transparent"
            implicitWidth: root.width
            implicitHeight: root.height
            RectangularGlow {
                id: rectGlow
                anchors.fill: rectButton
                glowRadius: 0
                spread: 0.5
                color: appStyle.accentColor
                cornerRadius: rectButton.radius + glowRadius
                visible: false
            }
            Rectangle {
                id: rectButton
                anchors.fill: parent
                color: root.backgroundColor
                radius: root.radius
                border.color: root.borderColor
            }
    }



    /*
    contentItem represents content of button shown when combobox is collapsed
    */
    contentItem: Item {
        id: ciButton
        anchors.fill: parent
        // optional label to show above combobox
        Label {
            visible: root.titleLabelText
            text: root.titleLabelText
            anchors.bottom: parent.top
            font.family: appStyle.fontFamily
            font.underline: true
            anchors.left: parent.left
            anchors.leftMargin: root.radius / 2
            color: root.fontColor
            font.italic: true
            font.pixelSize: 14
            anchors.bottomMargin: -2  // make things nice and tight
        }
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
