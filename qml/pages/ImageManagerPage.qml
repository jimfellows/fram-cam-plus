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
            model: camera_manager.images_proxy
            anchors {
                top: dataSelectorBar.bottom
                bottom: parent.bottom
                left: parent.left
                right: parent.right
            }
            delegate: ItemDelegate {
                id: delegate
                width: rectParent.width
                height: 75
                contentItem: Item {
                    anchors.fill: parent
                    Rectangle {
                        anchors.fill: parent
                        color: '#556a75'
                        border.color: appstyle.iconColor
                        radius: 8
                        RowLayout {
                            anchors.fill: parent
                            Image {
                                id: imgPhotoIcon
                                fillMode: Image.PreserveAspectFit
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                Layout.leftMargin: 10
                                sourceSize.height: 20
                                sourceSize.width: 20
                                source: "file:///" + model.full_path
                                cache: true
                            }
                            Label {
                                text: model.file_name
                                font.family: appstyle.fontFamily
                                font.pixelSize: 18
                                color: appstyle.secondaryFontColor
                            }
                            FramCamButton {
                                id: btnSelect
                                text: "Select"
                                implicitHeight: delegate.height
                                checkable: true
                            }
                            FramCamButton {
                                id: btnDelete
                                text: "Delete X"
                                implicitHeight: delegate.height
                                onClicked: {
                                    camera_manager.images_model.removeImage(index)
                                }
                            }
                            FramCamButton {
                                id: btnEdit
                                text: "Edit >>"
                                implicitHeight: delegate.height
                                onClicked: {
                                    windowMain.stackView.push(Qt.resolvedUrl('qrc:/qml/CapturePage.qml'))
                                    camera_manager.images_model.sendIndexToProxy(index)
                                }
                            }
                        }
                    }

                }
            }
        }
    }

}
