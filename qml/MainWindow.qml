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
    width: 1000  // seems to be pretty close to panasonic size
    height: 650  // seems to be pretty close to panasonic size
    visible: true
    color: "transparent"
    title: qsTr("FramCam+")

    //props
    property bool isWindowMaximized: false;
    property int windowMargin: 10;
    property string activePage;
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

    function navigateToPage(pageName) {
        console.info("Navigating to " + pageName)
        windowMain.activePage = pageName;
        if (pageName.toLowerCase() === 'capture' && !btnCapturePage.isActive) {
            btnCapturePage.isActive = true;
            btnSpeciesPage.isActive = false;
            btnSettingsPage.isActive = false;
            btnImageManagerPage.isActive = false;
            btnUploadPage.isActive = false;
            stackView.push(Qt.resolvedUrl('qrc:/pages/CapturePage.qml'))
        }
        else if (pageName.toLowerCase() === 'imagemanager' && !btnImageManagerPage.isActive) {
            btnImageManagerPage.isActive = true;
            btnSpeciesPage.isActive = false;
            btnSettingsPage.isActive = false;
            btnCapturePage.isActive = false;
            btnUploadPage.isActive = false;
            stackView.push(Qt.resolvedUrl('qrc:/pages/ImageManagerPage.qml'))
        }
        else if (pageName.toLowerCase() === 'settings' && !btnSettingsPage.isActive) {
            btnImageManagerPage.isActive = false;
            btnSpeciesPage.isActive = false;
            btnSettingsPage.isActive = true;
            btnCapturePage.isActive = false;
            btnUploadPage.isActive = false;
            stackView.push(Qt.resolvedUrl('qrc:/pages/SettingsPage.qml'))
        }
        else if (pageName.toLowerCase() === 'species' && !btnSpeciesPage.isActive) {
            btnImageManagerPage.isActive = false;
            btnSpeciesPage.isActive = true;
            btnSettingsPage.isActive = false;
            btnCapturePage.isActive = false;
            btnUploadPage.isActive = false;
            stackView.push(Qt.resolvedUrl('qrc:/pages/SpeciesPage.qml'))
        }
        else if (pageName.toLowerCase() === 'upload' && !btnUploadPage.isActive) {
            btnUploadPage.isActive = true;
            btnImageManagerPage.isActive = false;
            btnSpeciesPage.isActive = false;
            btnSettingsPage.isActive = false;
            btnCapturePage.isActive = false;
            stackView.push(Qt.resolvedUrl('qrc:/pages/UploadPage.qml'))
        }
    }

    Rectangle {
        id: rectBg
        //color: "#0085ca"
        color: appStyle.surfaceColor
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
            //color: appStyle.surfaceColor
            color: appStyle.elevatedSurface_L5
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
                    width: 100
                    height: 60
                    anchors.left: parent.left
                    anchors.top: parent.top
                    colorMouseOver: appStyle.primaryColor
                    colorDefault: appStyle.surfaceColor
                    anchors.topMargin: 0
                    anchors.leftMargin: 0
                    onClicked: animationLeftMenu.running = true
                }

                Rectangle {
                    id: rectTitle
                    color: appStyle.surfaceColor
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
                        mipmap: true
                    }

                    ColorOverlay {
                        source: imgAppLogo
                        color: appStyle.primaryColor
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
                        text: qsTr("FRAMCam") + "<font color=\"" + appStyle.accentColor + "\">+</font>"
                        color: appStyle.primaryFontColor
                        anchors.left: imgAppLogo.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        verticalAlignment: Text.AlignVCenter
                        font.bold: true
                        font.italic: true
                        font.pointSize: 12
                        font.family: appStyle.fontFamily
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
                            colorMouseOver: appStyle.errorColor
                            colorPressed: appStyle.errorColor.darker(0.75)
                            onClicked: windowMain.close()
                        }
                    }
                }

                Rectangle {
                    id: rectTitleDescr
                    y: 32
                    height: 25
                    color: appStyle.elevatedSurface_L1
                    anchors.left: btnToggleNavBar.right
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 0
                    anchors.rightMargin: 0
                    anchors.leftMargin: 0
                    Label {
                        id: lblDescr
                        y: 5
                        color: appStyle.secondaryFontColor
                        font.family: appStyle.fontFamily
                        text: qsTr("Intelligent image capture for NOAA West Coast Groundfish Bottom Trawl Survey")
                        anchors.left: parent.left
                        font.italic: true
                        horizontalAlignment: Text.AlignLeft
                        verticalAlignment: Text.AlignVCenter
                        anchors.leftMargin: 5
                    }
                    Image {
                        id: imgNoaaLogo
                        //width: 35

                        anchors {
                            right: parent.right
                            rightMargin: 15
                            top: parent.top
                            topMargin: 3
                            bottom: parent.bottom
                            bottomMargin: 3
                        }

                        source: "qrc:/pngs/noaa_fisheries_small.png"
                        sourceSize.width: 32
                        sourceSize.height: 32
                        fillMode: Image.PreserveAspectFit
                        antialiasing: true
                        smooth: true
                        mipmap: true
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
                    width: 100
                    color: appStyle.surfaceColor
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
                        to: if(rectLeftNavBar.width === 100) return 250; else return 100;
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

                        property int buttonHeight: 80

                        FramCamNavButton {
                            id: btnCapturePage
                            width: rectLeftNavBar.width
                            height: colNavButtons.buttonHeight
                            text: "Image Capture"
                            colorDefault: "transparent"
                            font.bold: true
                            font.pointSize: 13
                            iconSource: "qrc:/svgs/aperture.svg"
                            onClicked: windowMain.navigateToPage('capture')
                        }
                        FramCamNavButton {
                            id: btnImageManagerPage
                            width: rectLeftNavBar.width
                            text: "File Manager"
                            height: colNavButtons.buttonHeight
                            colorDefault: "transparent"
                            font.bold: true
                            font.pointSize: 13
                            isActive: false
                            iconSource: "qrc:/svgs/report.svg"
                            onClicked: windowMain.navigateToPage('imagemanager')
                        }
                        FramCamNavButton {
                            id: btnSpeciesPage
                            width: rectLeftNavBar.width
                            text: 'Species Select'
                            height: colNavButtons.buttonHeight
                            colorDefault: "transparent"
                            font.bold: true
                            font.pointSize: 13
                            isActive: false
                            iconSource: "qrc:/svgs/coral.svg"
                            onClicked: windowMain.navigateToPage('species')
                        }
                        FramCamNavButton {
                            id: btnUploadPage
                            width: rectLeftNavBar.width
                            text: 'Cloud Upload'
                            height: colNavButtons.buttonHeight
                            colorDefault: "transparent"
                            font.bold: true
                            font.pointSize: 13
                            isActive: false
                            iconSource: "qrc:/svgs/cloud_upload.svg"
                            onClicked: windowMain.navigateToPage('upload')
                        }
                    }

                    FramCamNavButton {
                        id: btnSettingsPage
                        y: 0
                        width: rectLeftNavBar.width
                        text: 'Settings'
                        anchors.left: parent.left
                        height: colNavButtons.buttonHeight
                        anchors.bottom: parent.bottom
                        colorDefault: "transparent"
                        anchors.leftMargin: 0
                        anchors.bottomMargin: 25
                        font.bold: true
                        font.pointSize: 13
                        isActive: false
                        iconSource: "qrc:/svgs/helm.svg"
                        onClicked: windowMain.navigateToPage('settings')
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
                        onCurrentItemChanged: console.info("CURRENT ITEM CHANGED TO " + currentItem)
                    }
                }

                Rectangle {
                    id: rectBottomBar
                    color: appStyle.elevatedSurface_L1
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
                        anchors.leftMargin: 5
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Camera: " + camControls.curCameraName
                        color: appStyle.secondaryFontColor
                        font.family: appStyle.fontFamily
                        font.pixelSize: 12
                    }
                    Label {
                        id: lblWarning
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        text: ''
                        color: appStyle.errorColor
                        font.family: appStyle.fontFamily
                        font.pixelSize: 12
                        font.bold: true
                        Connections {
                            target: imageManager
                            function onBadDestinationPath(path) {
                                lblWarning.color = appStyle.errorColor
                                lblWarning.text = "Bad Sync Path: " + path
                            }
                            function onCopyStarted(no_of_files) {
                                lblWarning.text = ''
                            }
                        }
                        Connections {
                            target: dataSelector.backdeckBiosWorker
                            function onBackdeckResults(status, msg, rows) {
                                console.info("FOUND ONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                lblWarning.color = status ? appStyle.secondaryFontColor : appStyle.errorColor
                                lblWarning.text = msg
                                lblWarning.visible = true
                            }
                        }
                    }
                    Label {
                        id: lblBarcode
                        font.bold: true
                        font.family: appStyle.fontFamily
                        anchors.right: parent.right
                        anchors.rightMargin: 5
                        anchors.verticalCenter: parent.verticalCenter
                        font.pixelSize: 12
                        Connections {
                            target: camControls
                            function onBarcodeFound(barcode) {
                                lblBarcode.text = "Barcode: " + barcode
                                lblBarcode.color = appStyle.accentColor
                            }
                            function onBarcodeNotFound(barcode) {
                                lblBarcode.text = "Barcode missing: " + barcode
                                lblBarcode.color = appStyle.errorColor
                            }
                        }
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
