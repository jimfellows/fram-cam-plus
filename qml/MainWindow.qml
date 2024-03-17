import QtQuick 2.15
import QtQuick.Window
import QtQuick.Controls 6.0
import Qt5Compat.GraphicalEffects
//import QtGraphicalEffects 1.15
import QtQuick.Controls.Material

import 'qrc:/controls'
import 'qrc:/pages'


Window {
    Material.theme: Material.Dark

    id: windowMain
    width: 1200
    height: 700
    visible: true
    color: "transparent"
    title: qsTr("FramCam+")

    //props
    property bool isWindowMaximized: false;
    property int windowMargin: 10;
    property alias stackView: stackView

    //removing default title bar
    flags: Qt.Window | Qt.FramelessWindowHint

    // internal object to hold funcs
    QtObject {
        id: internal
        function maximizeRestore(){
            if(isWindowMaximized === false) {
                isWindowMaximized = true
                hideMargins()
                windowMain.showMaximized()
                btnMaximize.iconSource = 'qrc:/svgs/restore.svg'
            }else {
                isWindowMaximized = false
                restoreMargins()
                windowMain.showNormal()
                btnMaximize.iconSource = 'qrc:/svgs/maximize.svg'
            }

        }
        function restoreWindowFromMax(){
            if(isWindowMaximized) {
                windowMain.showNormal()
                isWindowMaximized = false
                restoreMargins()
                btnMaximize.iconSource = 'qrc:/svgs/maximize.svg'
            }
        }

        function minimizeWindow() {
            restoreMargins()
            isWindowMaximized = false
            windowMain.showMinimized()
            btnMaximize.iconSource = 'qrc:/svgs/maximize.svg'
        }

        function hideMargins() {
            windowMargin = 0
        }

        function restoreMargins() {
            windowMargin = 10
        }
    }

    Rectangle {
        id: rectBg
        //color: "#0085ca"
        color: appstyle.surfaceColor
        border.color: "#003087"
        border.width: 1
        anchors.fill: parent
        anchors.rightMargin: windowMargin
        anchors.leftMargin: windowMargin
        anchors.bottomMargin: windowMargin
        anchors.topMargin: windowMargin
        z: 1

        Rectangle {
            id: rectAppContainer
            //color: "#00ffffff"
            //color: appstyle.surfaceColor
            color: appstyle.elevatedSurface_L5
            border.width: 5
            anchors.fill: parent
            anchors.rightMargin: 1
            anchors.leftMargin: 1
            anchors.bottomMargin: 1
            anchors.topMargin: 1

            Rectangle {
                id: rectTopBar
                height: 60
                color: "#ffffff"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.rightMargin: 5
                anchors.leftMargin: 5
                anchors.topMargin: 5

                FramCamMenuButton {
                    id: btnToggleNavBar
                    width: 70
                    height: 60
                    anchors.left: parent.left
                    anchors.top: parent.top
                    colorMouseOver: appstyle.primaryColor
                    colorDefault: appstyle.surfaceColor
                    anchors.topMargin: 0
                    anchors.leftMargin: 0
                    onClicked: animationLeftMenu.running = true
                }

                Rectangle {
                    id: rectTitle
                    color: appstyle.surfaceColor
                    anchors.left: btnToggleNavBar.right
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: rectTitleDescr.top
                    anchors.bottomMargin: 0
                    anchors.rightMargin: 0
                    anchors.topMargin: 0
                    anchors.leftMargin: 0

                    //double click top bar to min/max window
                    MouseArea {
                        anchors.fill: parent
                        onDoubleClicked: internal.maximizeRestore()
                    }
                    //allow dragging of window from this bar
                    DragHandler {
                        onActiveChanged: if (active){
                                             windowMain.startSystemMove()
                                             internal.restoreWindowFromMax()
                                         }
                    }

                    Image {
                        id: imgAppLogo
                        width: 35
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        source: "qrc:/svgs/nautilus.svg"
                        sourceSize.width: 32
                        sourceSize.height: 32
                        anchors.bottomMargin: 3
                        anchors.leftMargin: 5
                        anchors.topMargin: 5
                        fillMode: Image.PreserveAspectFit
                        antialiasing: false
                        smooth: true
                    }

                    ColorOverlay {
                        source: imgAppLogo
                        color: 'white'
//                        anchors.verticalCenter: parent.verticalCenter
                        anchors.top: imgAppLogo.top
                        anchors.bottom: imgAppLogo.bottom
                        anchors.left: imgAppLogo.left
                        anchors.right: imgAppLogo.right
//                        anchors.horizontalCenter: parent.horizontalCenter
                        antialiasing: false
                        width: imgAppLogo.width
                        height: imgAppLogo.height
                    }

                    Label {
                        id: lblTitle
                        text: qsTr("FRAMCam") + "<font color=\"" + appstyle.accentColor + "\">+</font>"
                        color: appstyle.primaryFontColor
                        anchors.left: imgAppLogo.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        font.bold: true
                        font.italic: true
                        font.pointSize: 12
                        font.family: appstyle.fontFamily
                        anchors.bottomMargin: 8
                        anchors.topMargin: 11
                        //anchors.leftMargin: 1
                    }

                    Row {
                        id: rowWindowButtons
                        x: 978
                        width: 105
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.topMargin: 0
                        anchors.bottomMargin: 0
                        anchors.rightMargin: 0

                        FramCamWindowButton {
                            id: btnMinimize
                            width: 35
                            height: 35
                            iconSource: "qrc:/svgs/minimize.svg"
                            iconColor: "white"
                            colorDefault: "#00000000"
                            onClicked: internal.minimizeWindow()
                        }

                        FramCamWindowButton {
                            id: btnMaximize
                            width: 35
                            height: 35
                            iconSource: "qrc:/svgs/maximize.svg"
                            iconColor: "white"
                            colorDefault: "#00000000"
                            onClicked: internal.maximizeRestore()

                        }

                        FramCamWindowButton {
                            id: btnClose
                            width: 35
                            height: 35
                            iconSource: "qrc:/svgs/close.svg"
                            iconColor: "white"
                            colorDefault: "#00000000"
                            colorMouseOver: appstyle.errorColor
                            colorPressed: appstyle.errorColor.darker(0.75)
                            onClicked: windowMain.close()
                        }
                    }
                }

                Rectangle {
                    id: rectTitleDescr
                    y: 32
                    height: 25
                    color: appstyle.elevatedSurface_L1
                    anchors.left: btnToggleNavBar.right
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.rightMargin: 0
                    anchors.leftMargin: 0

                    Label {
                        id: lblDescr
                        y: 5
                        color: appstyle.secondaryFontColor
                        font.family: appstyle.fontFamily
                        text: qsTr("Intelligent image capture for NOAA West Coast Groundfish Bottom Trawl Survey")
                        anchors.left: parent.left
                        horizontalAlignment: Text.AlignLeft
                        verticalAlignment: Text.AlignVCenter
                        anchors.leftMargin: 5
                    }
                }

            }

            Rectangle {
                id: rectContent
                color: "#00ffffff"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: rectTopBar.bottom
                anchors.bottom: parent.bottom
                anchors.rightMargin: 0
                anchors.leftMargin: 5
                anchors.bottomMargin: 5
                anchors.topMargin: 0

                Rectangle {
                    id: rectLeftNavBar
                    width: 70
                    color: appstyle.surfaceColor
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    clip: true
                    anchors.bottomMargin: 0
                    anchors.topMargin: 0
                    anchors.leftMargin: 0

                    PropertyAnimation{
                        id: animationLeftMenu
                        target: rectLeftNavBar
                        property: "width"
                        to: if(rectLeftNavBar.width === 70) return 250; else return 70;
                        duration:400
                        easing.type: Easing.InOutQuint
                    }

                    Column {
                        id: colNavButtons
                        height: 506
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        clip: true
                        anchors.topMargin: 0
                        anchors.rightMargin: 0
                        anchors.leftMargin: 0
                        FramCamNavButton {
                            id: btnCaptureScreen
                            width: rectLeftNavBar.width
                            height: 75
                            text: "Image Capture"
                            colorDefault: "transparent"
                            font.bold: true
                            font.pointSize: 13
                            iconSource: "qrc:/svgs/aperture.svg"

                            onClicked: {
                                if (!isActive) {
                                    isActive = true;
                                    btnSpeciesSelect.isActive = false;
                                    btnSettingsMenu.isActive = false;
                                    btnSummary.isActive = false;
                                    stackView.push(Qt.resolvedUrl('qrc:/pages/CapturePage.qml'))
                                }

                            }
                        }
                        FramCamNavButton {
                            id: btnSummary
                            width: rectLeftNavBar.width
                            text: "File Manager"
                            height: 75
                            colorDefault: "transparent"
                            font.bold: true
                            font.pointSize: 13
                            isActive: false
                            iconSource: "qrc:/svgs/report.svg"
                            onClicked: {
                                if (!isActive) {
                                    isActive = true;
                                    btnSpeciesSelect.isActive = false;
                                    btnSettingsMenu.isActive = false;
                                    btnCaptureScreen.isActive = false;
                                    stackView.push(Qt.resolvedUrl('qrc:/pages/ImageManagerPage.qml'))
                                }
                            }
                        }
                        FramCamNavButton {
                            id: btnSpeciesSelect
                            width: rectLeftNavBar.width
                            text: 'Species Select'
                            height: 75
                            colorDefault: "transparent"
                            font.bold: true
                            font.pointSize: 13
                            isActive: false
                            iconSource: "qrc:/svgs/coral.svg"
                            onClicked: {
                                if (!isActive) {
                                    isActive = true;
                                    btnCaptureScreen.isActive = false;
                                    btnSettingsMenu.isActive = false;
                                    btnSummary.isActive = false;
                                    stackView.push(Qt.resolvedUrl('qrc:/pages/SpeciesPage.qml'))
                                }
                            }
                        }
                    }

                    FramCamNavButton {
                        id: btnSettingsMenu
                        y: 0
                        width: rectLeftNavBar.width
                        text: 'Settings'
                        anchors.left: parent.left
                        height: 75
                        anchors.bottom: parent.bottom
                        colorDefault: "transparent"
                        anchors.leftMargin: 0
                        anchors.bottomMargin: 25
                        font.bold: true
                        font.pointSize: 13
                        isActive: false
                        iconSource: "qrc:/svgs/helm.svg"
                        onClicked: {
                            if (!isActive) {
                            isActive = true;
                            btnSpeciesSelect.isActive = false;
                            btnSummary.isActive = false;
                            btnCaptureScreen.isActive = false;
                            stackView.push(Qt.resolvedUrl('qrc:/pages/SettingsPage.qml'))
                         }
                        }
                    }
                }

                Rectangle {
                    id: rectScreens
                    color: "#00ffffff"
                    anchors.left: rectLeftNavBar.right
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    clip: true
                    anchors.bottomMargin: 25
                    anchors.leftMargin: 0

                    StackView {
                        id: stackView
                        anchors.fill: parent
                        initialItem: Qt.resolvedUrl('qrc:/pages/CapturePage.qml')
                        Component.onCompleted: push(Qt.resolvedUrl('qrc:/pages/CapturePage.qml'))
                    }
                }

                Rectangle {
                    id: rectBottomBar
                    color: appstyle.elevatedSurface_L1
                    anchors.left: rectLeftNavBar.right
                    anchors.right: parent.right
                    anchors.top: rectScreens.bottom
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.topMargin: 0
                    anchors.rightMargin: 5
                    anchors.leftMargin: 0

                    Label {
                        id: lblActiveCamera
                        anchors.left: parent.left
                        anchors.leftMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Active Camera: " + camera_manager.active_camera_name
                        color: appstyle.secondaryFontColor
                        font.family: appstyle.fontFamily
                    }
                    Label {
                        id: lblBarcode
                        font.bold: true
                        font.family: appstyle.fontFamily
                        color: appstyle.accentColor
                        text: camera_manager.lastBarcodeDetected ? "Barcode Detected: " + camera_manager.lastBarcodeDetected : ''
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.rightMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
        }
    }

    DropShadow{
        anchors.fill: rectBg
        horizontalOffset: 0
        verticalOffset: 0
        radius: 10
        samples: 16
        color: '#80000000'
        source: rectBg
        z: 0
    }
}

/*##^##
Designer {
    D{i:0;formeditorZoom:0.33}
}
##^##*/
