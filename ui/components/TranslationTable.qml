import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels
import QtQuick.Controls.FluentWinUI3

Pane {
    id: root

    signal rowClicked(int row)
    signal selectedRowsChanged(var rows)
    signal editRequested()

    readonly property int rowNumberColumnWidth: 44
    readonly property int minimumContentColumnWidth: 160
    property real originalColumnRatio: 0.45

    background: Rectangle { color: Theme.bgBase; radius: 6 }

    function statusColor(status, hovered, selected) {
        if (selected)                  return Theme.rowSelected
        if (status === "confirmed") return hovered ? Theme.rowDoneHover : Theme.rowDone
        if (status === "error") return Theme.dangerSubtle
        if (status === "translating")  return hovered ? Theme.rowTranslatingHover : Theme.rowTranslating
        return hovered ? Theme.rowDefaultHover : "transparent"
    }

    function contentColumnWidths() {
        var available = Math.max(0, tableView.width - rowNumberColumnWidth)
        if (available <= minimumContentColumnWidth * 2)
            return [available * 0.5, available * 0.5]
        var originalWidth = Math.round(available * originalColumnRatio)
        originalWidth = Math.max(
            minimumContentColumnWidth,
            Math.min(available - minimumContentColumnWidth, originalWidth)
        )
        return [originalWidth, available - originalWidth]
    }

    function setOriginalColumnWidth(width) {
        var available = tableView.width - rowNumberColumnWidth
        if (available <= minimumContentColumnWidth * 2)
            return
        var bounded = Math.max(
            minimumContentColumnWidth,
            Math.min(available - minimumContentColumnWidth, width)
        )
        originalColumnRatio = bounded / available
        tableView.forceLayout()
    }

    function resetColumnWidths() {
        originalColumnRatio = 0.45
        tableView.forceLayout()
    }

    // ---------------------------------------------------------------
    // Header
    // ---------------------------------------------------------------
    RowLayout {
        id: activeStatus
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: visible ? 38 : 0
        visible: vm.statusFilter !== "all"
        Label {
            Layout.fillWidth: true
            Layout.leftMargin: 2
            Layout.alignment: Qt.AlignVCenter
            text: (vm.strings["state_" + vm.statusFilter] ?? "") + " · " + vm.filteredEntryCount
            color: Theme.textPrimary
            elide: Text.ElideRight
        }
        ModernToolbarButton {
            text: vm.strings["filter_all"]
            Layout.preferredHeight: 30
            Layout.maximumHeight: 30
            Layout.alignment: Qt.AlignVCenter
            Layout.rightMargin: 2
            onClicked: vm.setStatusFilter("all")
        }
    }

    HorizontalHeaderView {
        id: header
        syncView: tableView
        anchors.top: activeStatus.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 32

        delegate: Rectangle {
            required property int column
            implicitHeight: 32
            color: Theme.bgHeader
            border.color: Theme.borderHeader
            border.width: 1

            Label {
                anchors.centerIn: parent
                text: column === 0 ? "#"
                    : column === 1 ? (vm.strings["original_text_label"] ?? "Original")
                    :                (vm.strings["translation_label"]   ?? "Translation")
                font.pixelSize: 12
                font.weight: Font.Medium
                color: Theme.textHeader
            }
        }
    }

    Item {
        id: columnResizeHandle
        objectName: "columnResizeHandle"
        x: root.rowNumberColumnWidth + root.contentColumnWidths()[0] - width / 2
        y: header.y
        width: 9
        height: header.height
        z: 10

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: columnResizeMouse.containsMouse || columnResizeMouse.pressed ? 2 : 1
            height: parent.height
            color: columnResizeMouse.containsMouse || columnResizeMouse.pressed
                ? Theme.primary : Theme.borderHeader
        }

        MouseArea {
            id: columnResizeMouse
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.SplitHCursor
            Accessible.name: vm.strings["resize_columns_hint"]
                ?? "Drag to resize columns. Double-click to reset."
            property real dragStartX: 0
            property real originalStartWidth: 0

            onPressed: function(mouse) {
                dragStartX = mapToItem(root, mouse.x, mouse.y).x
                originalStartWidth = root.contentColumnWidths()[0]
            }
            onPositionChanged: function(mouse) {
                if (!pressed)
                    return
                var currentX = mapToItem(root, mouse.x, mouse.y).x
                root.setOriginalColumnWidth(originalStartWidth + currentX - dragStartX)
            }
            onDoubleClicked: root.resetColumnWidths()
        }

        ToolTip.visible: columnResizeMouse.containsMouse
        ToolTip.delay: 500
        ToolTip.text: columnResizeMouse.Accessible.name
    }

    // ---------------------------------------------------------------
    // Table
    // ---------------------------------------------------------------
    property int _selectedRow: -1
    property int _anchorRow: -1
    property var _selectedRows: []

    function _containsRow(row) {
        return _selectedRows.indexOf(row) !== -1
    }

    function _applySelection() {
        tableView.selectionModel.clearSelection()
        for (var i = 0; i < _selectedRows.length; i++) {
            tableView.selectionModel.select(
                tableView.model.index(_selectedRows[i], 0),
                ItemSelectionModel.Select | ItemSelectionModel.Rows
            )
        }
        selectedRowsChanged(_selectedRows.slice())
    }

    function clearSelection() {
        _selectedRow = -1
        _anchorRow = -1
        _selectedRows = []
        tableView.selectionModel.clearSelection()
        selectedRowsChanged([])
    }

    function selectSingleRow(row) {
        if (tableView.rows <= 0)
            return
        var bounded = Math.max(0, Math.min(tableView.rows - 1, row))
        _selectedRow = bounded
        _anchorRow = bounded
        _selectedRows = [bounded]
        _applySelection()
        rowClicked(bounded)
        tableView.positionViewAtRow(bounded, TableView.Contain)
    }

    function selectRelative(offset) {
        selectSingleRow(_selectedRow >= 0 ? _selectedRow + offset : 0)
        tableView.forceActiveFocus()
    }

    TableView {
        id: tableView
        objectName: "translationTableView"
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: scrollBar.left
        anchors.bottom: parent.bottom

        model: vm.tableModel
        clip: true
        reuseItems: true
        activeFocusOnTab: true
        columnWidthProvider: function(col) {
            if (col === 0)
                return root.rowNumberColumnWidth
            var widths = root.contentColumnWidths()
            return col === 1 ? widths[0] : widths[1]
        }

        ScrollBar.vertical: scrollBar

        selectionModel: ItemSelectionModel {
            model: vm.tableModel
        }

        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Up) {
                root.selectRelative(-1)
                event.accepted = true
            } else if (event.key === Qt.Key_Down) {
                root.selectRelative(1)
                event.accepted = true
            } else if (event.key === Qt.Key_Home) {
                root.selectSingleRow(0)
                event.accepted = true
            } else if (event.key === Qt.Key_End) {
                root.selectSingleRow(tableView.rows - 1)
                event.accepted = true
            } else if (event.key === Qt.Key_PageUp) {
                root.selectRelative(-15)
                event.accepted = true
            } else if (event.key === Qt.Key_PageDown) {
                root.selectRelative(15)
                event.accepted = true
            } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                if (root._selectedRow >= 0)
                    root.editRequested()
                event.accepted = true
            }
        }

        delegate: Rectangle {
            id: cell
            required property int    row
            required property int    column
            required property bool   selected
            required property string display
            required property string entryStatus
            required property string sourceTag

            implicitHeight: 28
            clip: true
            color: root.statusColor(entryStatus, cellMouse.containsMouse, selected)

            Behavior on color { ColorAnimation { duration: 80 } }

            Label {
                visible: cell.column !== 1
                anchors {
                    left: parent.left; right: parent.right
                    verticalCenter: parent.verticalCenter
                    leftMargin: cell.column === 0 ? 0 : 8
                    rightMargin: cell.column === 0 ? 0 : 8
                }
                text: cell.column === 2
                    ? (vm.strings["state_" + cell.entryStatus] ?? cell.entryStatus) + (cell.display ? " · " + cell.display : "")
                    : cell.display
                elide: Text.ElideRight
                font.pixelSize: cell.column === 0 ? 11 : 13
                horizontalAlignment: cell.column === 0 ? Text.AlignHCenter : Text.AlignLeft
                color: cell.column === 0
                    ? (cell.selected ? Theme.textCellSelected : Theme.textSecondary)
                    : (cell.selected ? Theme.textCellSelected : Theme.textCell)
                wrapMode: Text.NoWrap
            }

            RowLayout {
                visible: cell.column === 1
                anchors {
                    left: parent.left; right: parent.right
                    verticalCenter: parent.verticalCenter
                    leftMargin: 8; rightMargin: 8
                }
                spacing: 6

                Rectangle {
                    visible: cell.sourceTag !== ""
                    implicitWidth: sourceTagLabel.implicitWidth + 12
                    implicitHeight: 20
                    radius: 4
                    color: Theme.bgSurface2
                    border.color: Theme.primary
                    border.width: 1
                    Accessible.name: (vm.strings["source_tag_label"] ?? "Source tag")
                        + ": " + cell.sourceTag

                    Label {
                        id: sourceTagLabel
                        anchors.centerIn: parent
                        text: cell.sourceTag
                        color: Theme.primary
                        font.pixelSize: 10
                        font.weight: Font.Medium
                    }

                    HoverHandler { id: sourceTagHover }
                    ToolTip.visible: sourceTagHover.hovered
                    ToolTip.delay: 400
                    ToolTip.text: parent.Accessible.name
                }

                Label {
                    Layout.fillWidth: true
                    text: cell.display
                    elide: Text.ElideRight
                    font.pixelSize: 13
                    color: cell.selected ? Theme.textCellSelected : Theme.textCell
                }
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: Theme.borderSubtle
            }

            MouseArea {
                id: cellMouse
                anchors.fill: parent
                hoverEnabled: true
                onClicked: function(mouse) {
                    tableView.forceActiveFocus()
                    root._selectedRow = cell.row
                    if ((mouse.modifiers & Qt.ShiftModifier) && root._anchorRow >= 0) {
                        var range = []
                        var first = Math.min(root._anchorRow, cell.row)
                        var last = Math.max(root._anchorRow, cell.row)
                        for (var r = first; r <= last; r++)
                            range.push(r)
                        root._selectedRows = range
                    } else if (mouse.modifiers & Qt.ControlModifier) {
                        var updated = root._selectedRows.slice()
                        var pos = updated.indexOf(cell.row)
                        if (pos >= 0)
                            updated.splice(pos, 1)
                        else
                            updated.push(cell.row)
                        root._selectedRows = updated
                        root._anchorRow = cell.row
                    } else {
                        root._selectedRows = [cell.row]
                        root._anchorRow = cell.row
                    }
                    root._applySelection()
                    root.rowClicked(cell.row)
                }
                onDoubleClicked: root.editRequested()
            }
        }
    }

    Rectangle {
        id: xmlWorkState
        objectName: "xmlWorkState"
        anchors {
            top: header.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        z: 5
        color: Theme.bgBase
        visible: vm.isXmlBusy
            || (vm.entryCount === 0 && vm.tagPreviewLines > 0)
            || ((vm.searchQuery !== "" || vm.statusFilter !== "all") && vm.filteredEntryCount === 0)

        Column {
            anchors.centerIn: parent
            width: Math.min(parent.width - 48, 420)
            spacing: 10

            BusyIndicator {
                anchors.horizontalCenter: parent.horizontalCenter
                running: vm.isXmlBusy
                visible: running
                implicitWidth: 32
                implicitHeight: 32
            }

            Label {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                color: Theme.textSecondary
                font.pixelSize: 12
                text: vm.isXmlBusy
                    ? vm.xmlBusyMessage
                    : ((vm.searchQuery !== "" || vm.statusFilter !== "all") && vm.filteredEntryCount === 0)
                        ? (vm.strings["filter_empty"]
                            ?? "No entries match this search.")
                    : (vm.strings["structure_preview_ready"]
                        ?? "%1 lines found. Apply the structure to load them.")
                        .replace("%1", vm.tagPreviewLines)
            }
        }
    }

    Connections {
        target: vm
        function onXmlLoaded() { root.clearSelection() }
        function onSelectionInvalidated() { root.clearSelection() }
    }

    ScrollBar {
        id: scrollBar
        anchors.top: header.bottom
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        policy: ScrollBar.AsNeeded
    }
}
