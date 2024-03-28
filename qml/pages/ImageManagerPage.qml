import QtQuick.Controls 6.3
import QtQuick 2.15
import QtQuick.Layouts 6.3
import Qt5Compat.GraphicalEffects

import 'qrc:/controls'
import 'qrc:/components'

Item {
    Rectangle {
        id: rectParent
        color: appStyle.elevatedSurface_L5
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
        }
        ListView {
            id: lvImages
            //Layout.preferredHeight: 200
            model: imageManager.imagesProxy
            //color: black
            clip: true

            function updateAllChecks(doCheck) {
                for(var i = 0; i < lvImages.model.rowCount(); i++) {
                    lvImages.itemAtIndex(i).isChecked = doCheck
                }
            }

            function deleteSelected() {
                // iterate backwards so deletions dont affect subsequent indexes
                for (var i = lvImages.model.rowCount() - 1; i > -1; i--) {
                    if (lvImages.itemAtIndex(i).isChecked) {
                        var sourceIndex = imageManager.imagesProxy.getSourceRowFromProxy(i)
                        imageManager.imagesModel.removeImage(sourceIndex)
                    }
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
                //color: "blue"
                property alias isChecked: check.checked;
                contentItem: Item {
                    anchors.fill: parent
                    Rectangle {
                        anchors.fill: parent
                        anchors.topMargin: -2
                        anchors.bottomMargin: -2
                        color: index % 2 ? appStyle.elevatedSurface_L6 : appStyle.elevatedSurface_L9
                        border.color: "transparent"
                        RowLayout {
                            anchors.fill: parent
                            spacing: 5
                            Layout.leftMargin: 5
                            RowLayout {
                                spacing: 2
                                FramCamCheckBox {
                                    id: check
                                    Layout.preferredHeight: 50
                                    Layout.preferredWidth: 50
                                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                }
                                Image {
                                    id: imgPhotoIcon
                                    fillMode: Image.PreserveAspectFit
                                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                    Layout.preferredWidth: 100
                                    sourceSize.height: 45
                                    sourceSize.width: 45
                                    source: "file:///" + model.full_path
                                    cache: true
                                }
                                ColumnLayout {
                                    Layout.fillHeight: true
                                    Layout.fillWidth: true
                                    Label {
                                        id: lblFileName
                                        text: model.file_name
                                        font.family: appStyle.fontFamily
                                        font.pixelSize: 10
                                        font.bold: true
                                        color: appStyle.secondaryFontColor
                                        Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                    }
                                    FramCamProgressBar {
                                        id: progressCopy
                                        value: 0
                                        //Layout.fillWidth: true
                                        Layout.preferredWidth: lblFileName.width
                                    }
                                }
                                ColumnLayout {
                                    Layout.fillHeight: true
                                    Layout.fillWidth: true
                                    Layout.leftMargin: 50
                                    Image {
                                        id: imgSyncArrow
                                        fillMode: Image.PreserveAspectFit
                                        Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
                                        Layout.bottomMargin: -10
                                        sourceSize.height: 40
                                        sourceSize.width: 40
                                        source: "qrc:/svgs/right_arrow.svg"
                                        antialiasing: true
                                        smooth: true
                                        mipmap: true
                                        layer {
                                            enabled: true
                                            effect: ColorOverlay {
                                                color: appStyle.iconColor
                                            }
                                        }
                                    }
                                    Label {
                                        text: "To WH?"
                                        Layout.alignment: Qt.AlignTop | Qt.AlignHCenter
                                        Layout.topMargin: -5
                                        font.family: appStyle.fontFamily
                                        font.pixelSize: 8
                                        font.bold: true
                                        color: appStyle.secondaryFontColor
                                    }

                                }
                                FramCamCheckBox {
                                    id: cbSynced
                                    Layout.preferredHeight: 50
                                    Layout.preferredWidth: 50
                                    Layout.leftMargin: 10
                                    Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                    checkColor: appStyle.accentColor
                                    enabled: false
                                }
                            }
                            RowLayout {
                            FramCamButton {
                                id: btnDelete
                                text: "Delete\nX"
                                visible: false  // going to force user to select, then delete
                                pressedColor: appStyle.errorColor
                                Layout.preferredHeight: delegate.height
                                Layout.preferredWidth: 75
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                onClicked: {
                                    var sourceIndex = imageManager.imagesProxy.getSourceRowFromProxy(index)
                                    imageManager.imagesModel.removeImage(sourceIndex)
                                }
                            }
                            FramCamButton {
                                id: btnEdit
                                text: "Edit\n>>"
                                Layout.preferredHeight: delegate.height
                                Layout.preferredWidth: 75
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                onClicked: {
                                    windowMain.navigateToPage('capture')
                                    imageManager.imagesProxy.proxyIndex = index
                                }
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
            color: appStyle.elevatedSurface_L5
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
                    text: "Select\nAll"
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
                    id: btnDeleteSelection
                    text: "Delete\nSelected"
                    pressedColor: appStyle.errorColor
                    Layout.preferredHeight: 75
                    onClicked: lvImages.deleteSelected()
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
