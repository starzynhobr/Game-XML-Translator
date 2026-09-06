import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.FluentWinUI3

Pane {
    id: root

    property string query: ""
    property int resultCount: 0
    property int totalCount: 0
    property int selectedCount: 0
    property bool busy: false

    signal searchRequested(string query)
    signal translateSelectionRequested()
    signal approveSelectionRequested()
    signal clearSelectionRequested()

    onQueryChanged: {
        if (searchField.text !== query)
            searchField.text = query
    }

    function focusSearch() {
        if (selectedCount > 1)
            clearSelectionRequested()
        Qt.callLater(function() {
            searchField.forceActiveFocus()
            searchField.selectAll()
        })
    }

    implicitHeight: 42
    Layout.minimumHeight: implicitHeight
    Layout.preferredHeight: implicitHeight
    Layout.maximumHeight: implicitHeight
    padding: 0

    background: Rectangle {
        color: Theme.bgSurface1
        radius: 6
        border.color: Theme.borderSubtle
        border.width: 1
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: root.selectedCount > 1 ? 1 : 0

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            RowLayout {
                anchors.fill: parent
                anchors.topMargin: 6
                anchors.bottomMargin: 6
                spacing: 8

                TextField {
                id: searchField
                objectName: "tableSearchField"
                Layout.fillWidth: true
                Layout.minimumWidth: 180
                Layout.maximumWidth: 480
                Layout.leftMargin: 6
                Layout.alignment: Qt.AlignVCenter
                Layout.preferredHeight: 30
                Layout.maximumHeight: 30
                leftPadding: 10
                rightPadding: 10
                placeholderText: vm.strings["table_search_placeholder"]
                    ?? "Search original, translation, tag or context"
                color: Theme.textInput
                placeholderTextColor: Theme.textDisabled
                selectByMouse: true

                background: Rectangle {
                    color: Theme.bgInput
                    radius: 4
                    border.color: searchField.activeFocus
                        ? Theme.primary : Theme.borderInput
                    border.width: 1
                }

                onTextEdited: root.searchRequested(text)
                Component.onCompleted: text = root.query
                onVisibleChanged: {
                    if (visible && text !== root.query)
                        text = root.query
                }
                }

                Label {
                Layout.alignment: Qt.AlignVCenter
                text: (vm.strings["table_search_results"] ?? "%1 of %2")
                    .replace("%1", root.resultCount)
                    .replace("%2", root.totalCount)
                color: Theme.textSecondary
                font.pixelSize: 11
                }

                ModernToolbarButton {
                objectName: "clearTableSearchButton"
                visible: root.query !== ""
                text: vm.strings["clear_search"] ?? "Clear"
                Layout.preferredWidth: 72
                Layout.rightMargin: 6
                Layout.alignment: Qt.AlignVCenter
                onClicked: root.searchRequested("")
                }

                Item {
                visible: root.query === ""
                Layout.preferredWidth: 1
                Layout.rightMargin: 5
                Layout.alignment: Qt.AlignVCenter
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            RowLayout {
                anchors.fill: parent
                anchors.topMargin: 6
                anchors.bottomMargin: 6
                spacing: 8

                Rectangle {
                Layout.preferredWidth: 3
                Layout.fillHeight: true
                color: Theme.primary
                radius: 2
                }

                Label {
                text: (vm.strings["selection_count"] ?? "%1 selected")
                    .replace("%1", root.selectedCount)
                color: Theme.textPrimary
                font.pixelSize: 12
                font.weight: Font.DemiBold
                }

                Item { Layout.fillWidth: true }

                ModernToolbarButton {
                objectName: "translateSelectionButton"
                text: vm.strings["translate_selection"] ?? "Translate selection"
                accented: true
                enabled: !root.busy
                Layout.preferredWidth: 152
                onClicked: root.translateSelectionRequested()
                }

                ModernToolbarButton {
                objectName: "approveSelectionButton"
                text: vm.strings["confirm_selection"] ?? "Confirm selection"
                enabled: !root.busy
                Layout.preferredWidth: 146
                onClicked: root.approveSelectionRequested()
                }

                ModernToolbarButton {
                objectName: "clearTableSelectionButton"
                text: vm.strings["clear_selection"] ?? "Clear selection"
                Layout.preferredWidth: 116
                Layout.rightMargin: 6
                onClicked: root.clearSelectionRequested()
                }
            }
        }
    }

    Shortcut {
        sequences: [StandardKey.Find]
        context: Qt.WindowShortcut
        onActivated: root.focusSearch()
    }

    Shortcut {
        sequence: "Escape"
        context: Qt.WindowShortcut
        onActivated: {
            if (root.selectedCount > 1)
                root.clearSelectionRequested()
            else if (root.query !== "")
                root.searchRequested("")
            else
                searchField.focus = false
        }
    }
}
