import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.FluentWinUI3

Pane {
    id: root

    required property string logText
    property bool expanded: false

    function clear() {}
    function expand() { expanded = true }
    function lastMessage() {
        var lines = logText.trim().split("\n")
        return lines.length && lines[0] !== ""
            ? lines[lines.length - 1]
            : (vm.strings["activity_empty"] ?? "No recent activity")
    }

    implicitHeight: expanded ? 136 : 34
    padding: 0

    background: Rectangle {
        color: Theme.bgSurface1
        radius: 6
        border.color: Theme.borderSubtle
        border.width: 1
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            id: activityHeader
            activeFocusOnTab: true
            Accessible.role: Accessible.Button
            Accessible.name: (vm.strings["activity_log"] ?? "Activity")
            Keys.onSpacePressed: root.expanded = !root.expanded
            Keys.onReturnPressed: root.expanded = !root.expanded
            Layout.fillWidth: true
            implicitHeight: 34
            color: activityMouse.containsMouse ? Theme.bgSurface2 : "transparent"
            border.color: activeFocus ? Theme.primary : "transparent"
            border.width: 1
            radius: 6

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                spacing: 10

                Label {
                    text: root.expanded ? "⌄" : "›"
                    color: Theme.textSecondary
                    font.pixelSize: 15
                }

                Label {
                    text: vm.strings["activity_log"] ?? "Activity"
                    color: Theme.textPrimary
                    font.pixelSize: 11
                    font.weight: Font.DemiBold
                }

                Label {
                    Layout.fillWidth: true
                    text: root.lastMessage()
                    color: Theme.textSecondary
                    font.pixelSize: 10
                    elide: Text.ElideRight
                }

                RowLayout {
                    visible: root.width >= 650
                    spacing: 12

                    Label {
                        text: "Ctrl+F  " + (vm.strings["shortcut_search"] ?? "Search")
                        color: Theme.textDisabled
                        font.pixelSize: 9
                    }
                    Label {
                        text: "↑↓  " + (vm.strings["shortcut_navigate"] ?? "Navigate")
                        color: Theme.textDisabled
                        font.pixelSize: 9
                    }
                    Label {
                        text: "Enter  " + (vm.strings["shortcut_edit"] ?? "Edit")
                        color: Theme.textDisabled
                        font.pixelSize: 9
                    }
                    Label {
                        text: "Ctrl+Enter  " + (vm.strings["shortcut_confirm"] ?? "Confirm")
                        color: Theme.textDisabled
                        font.pixelSize: 9
                    }
                    Label {
                        text: "Ctrl+S  " + (vm.strings["shortcut_save"] ?? "Save")
                        color: Theme.textDisabled
                        font.pixelSize: 9
                    }
                }
            }

            MouseArea {
                id: activityMouse
                objectName: "activityToggle"
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                Accessible.name: root.expanded
                    ? (vm.strings["collapse_activity"] ?? "Collapse activity")
                    : (vm.strings["expand_activity"] ?? "Expand activity")
                onClicked: root.expanded = !root.expanded
            }
        }

        LogPanel {
            objectName: "activityLogPanel"
            visible: root.expanded
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 1
            logText: root.logText
        }
    }
}
