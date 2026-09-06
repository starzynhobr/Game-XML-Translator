import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.FluentWinUI3

import "components"

ApplicationWindow {
    id: root
    title: (vm.strings["window_title"] ?? "STZ XML Translator") + " v" + vm.appVersion
    width: 1280
    height: 760
    minimumWidth: 1024
    minimumHeight: 620
    visible: true

    // ---------------------------------------------------------------
    // Global palette (forced dark independent of system theme)
    // ---------------------------------------------------------------
    palette.window:          Theme.bgBase
    palette.windowText:      Theme.textPrimary
    palette.base:            Theme.bgSurface2
    palette.alternateBase:   Theme.bgSurface1
    palette.text:            Theme.textPrimary
    palette.button:          Theme.secondary
    palette.buttonText:      Theme.onSecondary
    palette.highlight:       Theme.primary
    palette.highlightedText: Theme.onPrimary
    palette.toolTipBase:     Theme.bgSurface2
    palette.toolTipText:     Theme.textPrimary

    // ---------------------------------------------------------------
    // Log accumulator
    // ---------------------------------------------------------------
    property string logText: ""
    property int    progressDone: 0
    property int    progressTotal: 0
    property string selectedXpath: ""
    property string selectedOriginal: ""
    property string selectedTranslation: ""
    property string selectedSourceTag: ""
    property var selectedEntryContext: ({})

    Connections {
        target: vm

        function onLogAppended(msg) {
            var ts = new Date().toLocaleTimeString("pt-BR", {hour:'2-digit', minute:'2-digit', second:'2-digit'})
            root.logText += "[" + ts + "] " + msg + "\n"
        }
        function onProgressChanged(done, total) {
            root.progressDone = done
            root.progressTotal = total
        }
        function onEntrySelected(xpath, original, translation) {
            root.selectedXpath       = xpath
            root.selectedOriginal    = original
            root.selectedTranslation = translation
        }
        function onEntryMetadataSelected(sourceTag, context) {
            root.selectedSourceTag = sourceTag
            root.selectedEntryContext = context
        }
        function onXmlLoaded(count) {
            logPanel.clear()
            root.logText = ""
            root.selectedXpath = ""
            root.selectedOriginal = ""
            root.selectedTranslation = ""
            root.selectedSourceTag = ""
            root.selectedEntryContext = ({})
        }
        function onErrorOccurred(msg) {
            root.logText += "[ERRO] " + msg + "\n"
        }
        function onLanguageChanged() {
            root.title = (vm.strings["window_title"] ?? "STZ XML Translator")
                + " v" + vm.appVersion
        }
    }

    // ---------------------------------------------------------------
    // Main layout: Left | Center | Right
    // ---------------------------------------------------------------
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 6
        spacing: 6

        UpdateBanner {
            Layout.fillWidth: true
            Layout.maximumHeight: implicitHeight
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 6

            LeftSidebar {
                id: leftPanel
                Layout.preferredWidth: 290
                Layout.fillHeight: true

                logText:       root.logText
                progressDone:  root.progressDone
                progressTotal: root.progressTotal
            }

            // Center: Table + Log stacked
            ColumnLayout {
                Layout.fillWidth:  true
                Layout.fillHeight: true
                spacing: 6

                TranslationTable {
                    id: mainTable
                    Layout.fillWidth:  true
                    Layout.fillHeight: true

                    onRowClicked: (row) => vm.selectRow(row)
                    onSelectedRowsChanged: (rows) => vm.setSelectedRows(rows)
                    onEditRequested: rightPanel.focusTranslation()
                }

                LogPanel {
                    id: logPanel
                    Layout.fillWidth:  true
                    Layout.preferredHeight: 110
                    logText: root.logText
                }
            }

            EditPanel {
                id: rightPanel
                Layout.preferredWidth: 330
                Layout.fillHeight: true

                xpath:          root.selectedXpath
                originalText:   root.selectedOriginal
                translationText: root.selectedTranslation
                sourceTag: root.selectedSourceTag
                entryContext: root.selectedEntryContext

                onTranslationEdited: (text) => {
                    root.selectedTranslation = text
                }
                onPreviousRequested: mainTable.selectRelative(-1)
                onNextRequested: mainTable.selectRelative(1)
            }
        }
    }
}
