import QtQuick 2.15
import QtQuick.Window
import QtQuick.Controls 6.0
import Qt5Compat.GraphicalEffects
//import QtGraphicalEffects 1.15
import QtQuick.Controls.Material

import "./pages"
import "./controls"

Window {
    Material.theme: Material.Dark
    Material.accent: Material.Purple
    id: windowMain
    width: 1200
    height: 700
    visible: true
    color: "#00ffffff"
    title: qsTr("FramCam")

    //props
    property bool isWindowMaximized: false;
    property int windowMargin: 10;

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
        color: "#0085ca"
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
            color: "#00ffffff"
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
                    colorMouseOver: "#0085ca"
                    colorDefault: "#003087"
                    anchors.topMargin: 0
                    anchors.leftMargin: 0
                    onClicked: animationLeftMenu.running = true
                }

                Rectangle {
                    id: rectTitle
                    color: "#003087"
                    anchors.left: btnToggleNavBar.right
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: rectTitleDescr.top
                    anchors.bottomMargin: 0
                    anchors.rightMargin: 0
                    anchors.topMargin: 0
                    anchors.leftMargin: 0

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
                        text: qsTr("FRAMCam+")
                        color: 'white'
                        anchors.left: imgAppLogo.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        font.bold: true
                        font.italic: true
                        font.pointSize: 12
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
                            onClicked: windowMain.close()
                        }
                    }
                }

                Rectangle {
                    id: rectTitleDescr
                    y: 32
                    height: 25
                    color: "#cfcfcf"
                    anchors.left: btnToggleNavBar.right
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.rightMargin: 0
                    anchors.leftMargin: 0

                    Label {
                        id: lblDescr
                        y: 5
                        color: "#242424"
                        text: qsTr("Specimen photo capture for NOAA West Coast Bottom Trawy Research Survey")
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
                    color: "#003087"
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
                        duration:500
                        easing.type: Easing.InOutQuint
//                        easing.type: Easing.OutBounce
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
                            colorDefault: "#003087"
                            font.bold: true
                            font.pointSize: 13
                            iconSource: "qrc:/svgs/aperture.svg"

                            onClicked: {
                                if (!isActive) {
                                    isActive = true;
                                    btnSpeciesSelect.isActive = false;
                                    btnSettingsMenu.isActive = false;
                                    btnSummary.isActive = false;
                                    stackView.push(Qt.resolvedUrl('qrc:/qml/CapturePage.qml'))
                                }

                            }
                        }

                        FramCamNavButton {
                            id: btnSpeciesSelect
                            width: rectLeftNavBar.width
                            text: 'Species Select'
                            height: 75
                            colorDefault: "#003087"
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
                                    stackView.push(Qt.resolvedUrl('qrc:/qml/SpeciesPage.qml'))
                                }
                            }
                        }
                        FramCamNavButton {
                            id: btnSummary
                            width: rectLeftNavBar.width
                            text: "Image Summary"
                            height: 75
                            colorDefault: "#003087"
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
                                    stackView.push(Qt.resolvedUrl('qrc:/qml/ImageManagerPage.qml'))
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
                        colorDefault: "#003087"
                        anchors.leftMargin: 0
                        anchors.bottomMargin: 25
                        font.bold: true
                        font.pointSize: 13
                        isActive: false
                        iconSource: "qrc:/svgs/settings.svg"
                        onClicked: {
                            if (!isActive) {
                            isActive = true;
                            btnSpeciesSelect.isActive = false;
                            btnSummary.isActive = false;
                            btnCaptureScreen.isActive = false;
                            stackView.push(Qt.resolvedUrl('qrc:/qml/SettingsPage.qml'))
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
                        initialItem: Qt.resolvedUrl('qrc:/qml/CapturePage.qml')
                        Component.onCompleted: push(Qt.resolvedUrl('qrc:/qml/CapturePage.qml'))
                    }
                }

                Rectangle {
                    id: rectBottomBar
                    color: "#cfcfcf"
                    anchors.left: rectLeftNavBar.right
                    anchors.right: parent.right
                    anchors.top: rectScreens.bottom
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.topMargin: 0
                    anchors.rightMargin: 5
                    anchors.leftMargin: 0
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
