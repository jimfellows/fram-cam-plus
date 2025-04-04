
import QtQuick.Controls 6.3
import QtQuick 2.15
import Qt5Compat.GraphicalEffects
import QtMultimedia 6.3
import 'qrc:/controls'


Rectangle {
    id: root
    implicitHeight: 75
    implicitWidth: 500
    color: appStyle.elevatedSurface_L5
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: parent.top
    anchors.leftMargin: 0
    anchors.rightMargin: 0
    anchors.topMargin: 0

    function flashAllMenus() {
        comboHauls.startFlash()
        comboCatch.startFlash()
        comboProject.startFlash()
        comboBiolabel.startFlash()
    }

    Connections {
        target: dataSelector
        function onNewDropDownRows(dropdown) {
            if (dropdown === 'hauls') comboHauls.startGlow();
            if (dropdown === 'catches') comboCatch.startGlow();
            if (dropdown === 'projects') comboProject.startGlow();
            if (dropdown === 'bios') comboBiolabel.startGlow();
        }
        function onHaulSelectionRequired() {
            comboHauls.startGlow(appStyle.errorColor)
        }
    }

    Row {
        anchors.fill: parent
        anchors.verticalCenter: parent.verticalCenter
        spacing: 10
        anchors.top: parent.top
        anchors.topMargin: -5
        anchors.rightMargin: 50
        FramCamComboBox {
            id: comboHauls
            fontColor: appStyle.secondaryFontColor
            borderColor: appStyle.iconColor
            height: parent.height
            maxPopupHeight: windowMain.height * 0.65
            width: parent.width * 0.15
            fontSize: 12
            model: dataSelector.hauls_model
            textRole: "haul_number"
            placeholderText: dataSelector.hauls_model.row_count === 0 ? 'N/A' : 'Select Haul...'
            onCurrentIndexChanged: {
                model.selectedIndex = currentIndex
            }
            Component.onCompleted: {  // set ix based on settings saved value
                comboHauls.currentIndex = model.selectedIndex
            }
            Connections {
                target: dataSelector.hauls_model
                function onSelectIndexInUI(index) {
                    comboHauls.currentIndex = index
                }
            }
        }

        FramCamComboBox {
            id: comboCatch
            fontColor: appStyle.secondaryFontColor
            borderColor: appStyle.iconColor
            height: parent.height
            maxPopupHeight: windowMain.height * 0.65
            width: parent.width * 0.225
            model: dataSelector.catches_proxy
            textRole: "catch_display_name"
            placeholderText: dataSelector.catches_model.row_count === 0 ? 'N/A' : 'Select Catch...'
            fontSize: 12
            onCurrentIndexChanged: {
                model.proxyIndex = currentIndex
            }
            Component.onCompleted: {  // set ix based on settings saved value
                comboCatch.currentIndex = model.getProxyRowFromSource(dataSelector.catches_model.selectedIndex)
            }
            Connections {
                target: dataSelector.catches_proxy
                function onSelectIndexInUI(index) {
                    comboCatch.currentIndex = index
                }
            }
        }
        FramCamComboBox {
            id: comboProject
            fontColor: appStyle.secondaryFontColor
            borderColor: appStyle.iconColor
            height: parent.height
            maxPopupHeight: windowMain.height * 0.65
            width: parent.width * 0.225
            model: dataSelector.projects_proxy
            textRole: "project_name"
            fontSize: 12
            placeholderText: dataSelector.projects_model.row_count === 0 ? 'N/A' : 'Select Project...'
            onCurrentIndexChanged: {
                model.proxyIndex = currentIndex
            }
            Component.onCompleted: {  // set ix based on settings saved value
                comboProject.currentIndex = model.getProxyRowFromSource(dataSelector.projects_model.selectedIndex)
            }
            Connections {
                target: dataSelector.projects_proxy
                function onSelectIndexInUI(index) {
                    comboProject.currentIndex = index
                }
            }
        }
        FramCamComboBox {
            id: comboBiolabel
            fontColor: appStyle.secondaryFontColor
            borderColor: appStyle.iconColor
            height: parent.height
            maxPopupHeight: windowMain.height * 0.65
            width: parent.width * 0.2
            model: dataSelector.bios_proxy
            textRole: "bio_label"
            fontSize: 12
            placeholderText: dataSelector.bios_model.row_count === 0 ? 'N/A' : 'Select Bio Label...'
            onCurrentIndexChanged: {
                model.proxyIndex = currentIndex
            }
            Component.onCompleted: {  // set ix based on settings saved value
                comboBiolabel.currentIndex = model.getProxyRowFromSource(dataSelector.bios_model.selectedIndex)
            }
            Connections {
                target: dataSelector.bios_proxy
                function onSelectIndexInUI(index) {
                    comboBiolabel.currentIndex = index
                }
            }
        }
        FramCamButton {
            id: btnClear
            implicitWidth: 75
            implicitHeight: 75
            radius: 20
            iconSource: 'qrc:/svgs/sweep.svg'
            onClicked: {
                comboHauls.currentIndex = -1
                camControls.clearBarcode()
            }
        }
        FramCamButton {
            id: btnDownloadData
            implicitWidth: 75
            implicitHeight: 75
            radius: 20
            iconSource: 'qrc:/svgs/download.svg'
            onClicked: dataSelector.getBackdeckBios()
        }
    }
}