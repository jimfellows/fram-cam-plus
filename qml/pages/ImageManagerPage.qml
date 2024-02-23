import QtQuick.Controls 6.3
import QtQuick 2.15
import QtQuick.Layouts 6.3
import Qt5Compat.GraphicalEffects

Item {
    Rectangle {
        id: rectParent
        color: "#8413a2"
        anchors.fill: parent

        ListView {
            id: lvImages
            model: image_manager.model
            //model: [1, 2, 3]
            anchors.fill: parent
            delegate: ItemDelegate {
                id: delegate
                width: rectParent.width
                height: 50
                contentItem: Item {
                    Rectangle {
                        implicitHeight: delegate.height
                        implicitWidth: delegate.width
                        RowLayout {
                            Image {
                                id: imgPhotoIcon
                                fillMode: Image.PreserveAspectFit
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignLeft
                                sourceSize.height: 20
                                sourceSize.width: 20
                                source: "qrc:/svgs/image_file.svg"
                                layer {
                                    enabled: true
                                    effect: ColorOverlay {
                                        color: "black"
                                    }
                                }
                            }
                            Label {
                                text: model.file_name
                            }
                            Button {
                                id: btnDelete
                                text: "Delete X"
                            }
                            Button {
                                id: btnEdit
                                text: "Edit >>"
                            }
                        }
                    }

                }
            }
        }
    }

}
