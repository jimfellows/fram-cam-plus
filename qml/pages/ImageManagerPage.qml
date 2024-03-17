import QtQuick.Controls 6.3
import QtQuick 2.15
import QtQuick.Layouts 6.3
import Qt5Compat.GraphicalEffects

import 'qrc:/controls'
import 'qrc:/components'

Item {
    Rectangle {
        id: rectParent
        color: appstyle.elevatedSurface_L5
        anchors.fill: parent
        anchors.rightMargin: 5
        anchors.leftMargin: 5
        anchors.bottomMargin: 5
        anchors.topMargin: 5

        DataSelectorBar {
            id: dataSelectorBar
            anchors {
                right: parent.right
                left: parent.left

            }
            height: 75
        }
        ListView {
            id: lvImages
            //Layout.preferredHeight: 200
            model: camera_manager.images_proxy

            function updateAllChecks(doCheck) {
                for(var i = 0; i < lvImages.model.rowCount(); i++) {
                    lvImages.itemAtIndex(i).isChecked = doCheck
                }
            }

            anchors {
                top: dataSelectorBar.bottom
                bottom: parent.bottom
                left: parent.left
                bottomMargin: 100
                right: parent.right
            }
            delegate: ItemDelegate {
                id: delegate
                width: rectParent.width
                height: 75
                property alias isChecked: check.checked;
                contentItem: Item {
                    anchors.fill: parent
                    Rectangle {
                        anchors.fill: parent
                        color: '#556a75'
                        border.color: appstyle.iconColor
                        radius: 8
                        RowLayout {
                            anchors.fill: parent
                            FramCamCheckBox {
                                id: check
                                Layout.preferredHeight: 50
                                Layout.preferredWidth: 50
                            }
                            Image {
                                id: imgPhotoIcon
                                fillMode: Image.PreserveAspectFit
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                Layout.leftMargin: 10
                                sourceSize.height: 40
                                sourceSize.width: 40
                                source: "file:///" + model.full_path
                                cache: true
                            }
                            Label {
                                text: model.file_name
                                font.family: appstyle.fontFamily
                                font.pixelSize: 16
                                color: appstyle.secondaryFontColor
                            }
                            FramCamButton {
                                id: btnDelete
                                text: "Delete X"
                                Layout.preferredHeight: delegate.height
                                Layout.preferredWidth: 100
                                onClicked: {
                                    camera_manager.images_model.removeImage(index)
                                }
                            }
                            FramCamButton {
                                id: btnEdit
                                text: "Edit >>"
                                Layout.preferredHeight: delegate.height
                                Layout.preferredWidth: 100
                                onClicked: {
                                    windowMain.stackView.push(Qt.resolvedUrl('qrc:/pages/CapturePage.qml'))
                                    camera_manager.images_model.sendIndexToProxy(index)
                                }
                            }
                        }
                    }
                }
            }
        }  // listview
        Rectangle {
            anchors {
                top: lvImages.bottom
                //bottom: parent.bottom
                left: parent.left
                right: parent.right

            }
            height: 100
            color: appstyle.elevatedSurface_L5
            RowLayout {
                spacing: 20
                anchors {
                    leftMargin: 10
                    rightMargin: 10
                    horizontalCenter: parent.horizontalCenter
                    verticalCenter: parent.verticalCenter
                }

                FramCamButton {
                    id: btnSelectAll
                    text: "Select All"
                    Layout.preferredHeight: 75
                    onClicked: lvImages.updateAllChecks(true)
                }
                FramCamButton {
                    id: btnClearSelection
                    text: "Clear\nSelection"
                    Layout.preferredHeight: 75
                    onClicked: lvImages.updateAllChecks(false)
                }
                FramCamButton {
                    id: btnDeleteSeletion
                    text: "Delete\nSelected"
                    Layout.preferredHeight: 75
                }
                FramCamButton {
                    id: btnSyncSelection
                    text: "Sync\nSelected"
                    Layout.preferredHeight: 75
                }
            }
        }
    }

}
