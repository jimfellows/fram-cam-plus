
import QtQuick.Controls 6.3
import QtQuick 2.15
import Qt5Compat.GraphicalEffects
import QtMultimedia 6.3
import 'qrc:/controls'


Rectangle {
    id: root
    implicitHeight: 60
    implicitWidth: 500
    color: "#00ffffff"
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: parent.top
    anchors.leftMargin: 0
    anchors.rightMargin: 0
    anchors.topMargin: 0

    Row {
        anchors.fill: parent
        spacing: 10
        anchors.rightMargin: 50
        FramCamComboBox {
            id: comboHauls
            backgroundColor: appstyle.elevatedSurface_L5
            fontColor: appstyle.secondaryFontColor
            borderColor: appstyle.iconColor
            height: parent.height
            maxPopupHeight: windowMain.height * 0.65
            width: parent.width * 0.15
            fontSize: 12
            model: data_selector.hauls_model
            textRole: "haul_number"
            placeholderText: data_selector.hauls_model.row_count === 0 ? 'N/A' : 'Select Haul...'
            onCurrentIndexChanged: {
                model.currentIndex = currentIndex
            }
            Component.onCompleted: {  // set ix based on settings saved value
                comboHauls.currentIndex = model.currentIndex
            }
            Connections {
                target: data_selector.hauls_model
                function onIndexSetSilently(new_index) {
                    comboHauls.currentIndex = new_index
                }
            }
        }

        FramCamComboBox {
            id: comboCatch
            backgroundColor: appstyle.elevatedSurface_L5
            fontColor: appstyle.secondaryFontColor
            borderColor: appstyle.iconColor
            height: parent.height
            maxPopupHeight: windowMain.height * 0.65
            width: parent.width * 0.225
            model: data_selector.catches_proxy
            textRole: "display_name"
            placeholderText: data_selector.catches_model.row_count === 0 ? 'N/A' : 'Select Catch...'
            fontSize: 12
            onCurrentIndexChanged: {
                model.proxyIndex = currentIndex
            }
            Component.onCompleted: {  // set ix based on settings saved value
                comboCatch.currentIndex = model.getProxyRowFromSource(data_selector.catches_model.currentIndex)
            }
            Connections {
                target: data_selector.catches_model
                function onIndexSetSilently(new_index) {
                    comboCatch.currentIndex = model.getProxyRowFromSource(new_index)
                }
            }
        }
        FramCamComboBox {
            id: comboProject
            backgroundColor: appstyle.elevatedSurface_L5
            fontColor: appstyle.secondaryFontColor
            borderColor: appstyle.iconColor
            height: parent.height
            maxPopupHeight: windowMain.height * 0.65
            width: parent.width * 0.225
            model: data_selector.projects_proxy
            textRole: "project_name"
            fontSize: 12
            placeholderText: data_selector.projects_model.row_count === 0 ? 'N/A' : 'Select Project...'
            onCurrentIndexChanged: {
                model.proxyIndex = currentIndex
            }
            Component.onCompleted: {  // set ix based on settings saved value
                comboProject.currentIndex = model.getProxyRowFromSource(data_selector.projects_model.currentIndex)
            }
            Connections {
                target: data_selector.projects_model
                function onIndexSetSilently(new_index) {
                    comboProject.currentIndex = data_selector.projects_proxy.getProxyRowFromSource(new_index)
                }
            }
        }
        FramCamComboBox {
            id: comboBiolabel
            backgroundColor: appstyle.elevatedSurface_L5
            fontColor: appstyle.secondaryFontColor
            borderColor: appstyle.iconColor
            height: parent.height
            maxPopupHeight: windowMain.height * 0.65
            width: parent.width * 0.2
            model: data_selector.bios_proxy
            textRole: "bio_label"
            fontSize: 12
            placeholderText: data_selector.bios_model.row_count === 0 ? 'N/A' : 'Select Bio Label...'
            onCurrentIndexChanged: {
                model.proxyIndex = currentIndex
            }
            Component.onCompleted: {  // set ix based on settings saved value
                comboBiolabel.currentIndex = model.getProxyRowFromSource(data_selector.bios_model.currentIndex)
            }
            Connections {
                target: data_selector.bios_model
                function onIndexSetSilently(new_index) {
                    comboBiolabel.currentIndex = model.getProxyRowFromSource(new_index)
                }
            }
        }
        FramCamButton {
            id: btnClear
            implicitWidth: 60
            implicitHeight: 60
            radius: 20
            iconSource: 'qrc:/svgs/sweep.svg'
            onClicked: {
                comboHauls.currentIndex = -1
            }
        }
        FramCamButton {
            id: btnDownloadData
            implicitWidth: 60
            implicitHeight: 60
            radius: 20
            iconSource: 'qrc:/svgs/download.svg'
        }
    }
}