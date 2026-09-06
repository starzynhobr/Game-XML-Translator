import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.FluentWinUI3

Pane {
    id: root

    property string loadedFileName: ""
    property int progressDone: 0
    property int progressTotal: 0
    property bool translating: false
    property bool xmlBusy: false
    property int entryCount: 0
    property var targetLocaleNames: []
    property var targetLocaleCodes: []
    property string targetLocaleCode: ""

    signal loadRequested()
    signal targetLocaleRequested(string localeCode)
    signal translateRequested()
    signal glossaryRequested()
    signal settingsRequested()
    signal exportRequested()

    readonly property bool compact: width < 1120
    readonly property int targetLocaleIndex: {
        var idx = targetLocaleCodes.indexOf(targetLocaleCode)
        return idx >= 0 ? idx : 0
    }
    readonly property real progressRatio: progressTotal > 0
        ? Math.min(1, progressDone / progressTotal) : 0

    implicitHeight: compact ? 112 : 66
    implicitWidth: 0
    padding: 0

    background: Rectangle {
        color: Theme.bgSurface1
        radius: 7
        border.color: Theme.borderSubtle
        border.width: 1
    }

    GridLayout {
        anchors.fill: parent
        anchors.margins: 8
        columns: root.compact ? 2 : 3
        columnSpacing: 12
        rowSpacing: 8

        RowLayout {
            id: fileGroup
            Layout.row: 0
            Layout.column: 0
            Layout.fillWidth: true
            Layout.preferredWidth: 260
            spacing: 8

            ModernToolbarButton {
                objectName: "topBarLoadButton"
                text: vm.strings["topbar_load_xml"] ?? "Load XML"
                enabled: !root.translating && !root.xmlBusy
                Layout.preferredWidth: 132
                onClicked: root.loadRequested()
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 1

                Label {
                    text: vm.strings["loaded_file_label"] ?? "Loaded file"
                    color: Theme.textDisabled
                    font.pixelSize: 9
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
                Label {
                    text: root.loadedFileName !== ""
                        ? root.loadedFileName
                        : (vm.strings["topbar_no_file"] ?? "No XML selected")
                    color: root.loadedFileName !== ""
                        ? Theme.textPrimary : Theme.textSecondary
                    font.pixelSize: 11
                    font.weight: root.loadedFileName !== "" ? Font.Medium : Font.Normal
                    Layout.fillWidth: true
                    elide: Text.ElideMiddle
                }
            }
        }

        RowLayout {
            id: statusGroup
            Layout.row: 0
            Layout.column: 1
            Layout.fillWidth: true
            Layout.preferredWidth: 350
            spacing: 12

            ColumnLayout {
                Layout.preferredWidth: 176
                spacing: 2

                Label {
                    text: vm.strings["translate_to_label"] ?? "Translate to"
                    color: Theme.textSecondary
                    font.pixelSize: 10
                }
                StyledComboBox {
                    id: targetLocaleCombo
                    objectName: "topBarTargetLocale"
                    model: root.targetLocaleNames
                    currentIndex: root.targetLocaleIndex
                    Layout.fillWidth: true
                    implicitHeight: 32
                    enabled: !root.xmlBusy
                    onActivated: {
                        if (currentIndex >= 0 && currentIndex < root.targetLocaleCodes.length)
                            root.targetLocaleRequested(root.targetLocaleCodes[currentIndex])
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 3

                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: vm.strings["progress_label"] ?? "Progress"
                        color: Theme.textSecondary
                        font.pixelSize: 10
                    }
                    Item { Layout.fillWidth: true }
                    Label {
                        text: root.progressDone + " / " + root.progressTotal
                        color: Theme.textPrimary
                        font.pixelSize: 10
                        font.weight: Font.Medium
                    }
                }
                ProgressBar {
                    id: topProgress
                    objectName: "topBarProgress"
                    value: root.progressRatio
                    Layout.fillWidth: true
                    implicitHeight: 5

                    background: Rectangle {
                        color: Theme.bgSurface3
                        radius: 3
                    }
                    contentItem: Rectangle {
                        width: topProgress.visualPosition * parent.width
                        height: parent.height
                        radius: 3
                        color: Theme.primary
                        Behavior on width { NumberAnimation { duration: 120 } }
                    }
                }
            }
        }

        RowLayout {
            id: actionGroup
            Layout.row: root.compact ? 1 : 0
            Layout.column: root.compact ? 0 : 2
            Layout.columnSpan: root.compact ? 2 : 1
            Layout.fillWidth: root.compact
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            spacing: 8

            Item {
                visible: root.compact
                Layout.fillWidth: true
            }

            ModernToolbarButton {
                objectName: "topBarTranslateButton"
                text: root.translating
                    ? (vm.strings["cancel_button"] ?? "Cancel")
                    : (vm.strings["topbar_translate_pending"] ?? "Translate pending")
                accented: !root.translating
                enabled: (root.entryCount > 0 || root.translating) && !root.xmlBusy
                Layout.preferredWidth: 188
                Layout.minimumWidth: 160
                Layout.maximumWidth: 200
                onClicked: root.translateRequested()
            }
            ModernToolbarButton {
                objectName: "topBarGlossaryButton"
                text: vm.strings["topbar_glossary"] ?? "Glossary"
                Layout.preferredWidth: 92
                onClicked: root.glossaryRequested()
            }
            ModernToolbarButton {
                objectName: "topBarSettingsButton"
                text: vm.strings["topbar_settings"] ?? "Settings"
                Layout.preferredWidth: 104
                onClicked: root.settingsRequested()
            }
            ModernToolbarButton {
                objectName: "topBarExportButton"
                text: vm.strings["topbar_export"] ?? "Export XML"
                enabled: root.progressDone > 0 && !root.translating && !root.xmlBusy
                Layout.preferredWidth: 104
                onClicked: root.exportRequested()
            }
        }
    }
}
