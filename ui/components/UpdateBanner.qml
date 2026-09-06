import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.FluentWinUI3

Rectangle {
    id: root
    objectName: "updateBanner"

    implicitHeight: vm.updateStatus === "downloading" ? 60 : 48
    color: Theme.bgSurface1
    radius: 6
    border.color: Theme.primary
    border.width: 1
    visible: vm.updateAvailable

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 8
        anchors.topMargin: 6
        anchors.bottomMargin: 6
        spacing: 8

        Label {
            text: "↻"
            color: Theme.primary
            font.pixelSize: 20
            font.weight: Font.DemiBold
            Layout.alignment: Qt.AlignVCenter
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            Label {
                text: (vm.strings["update_banner_title"] ?? "Update %1 available")
                    .arg(vm.updateVersion)
                color: Theme.textPrimary
                font.pixelSize: 12
                font.weight: Font.DemiBold
                elide: Text.ElideRight
                Layout.fillWidth: true
            }

            Label {
                visible: vm.updateStatus !== "downloading"
                text: vm.updateStatus === "ready"
                    ? (vm.strings["update_ready_hint"] ?? "Ready to install.")
                    : (vm.strings["update_banner_hint"] ?? "Download and install the new version.")
                color: Theme.textSecondary
                font.pixelSize: 10
                elide: Text.ElideRight
                Layout.fillWidth: true
            }

            ProgressBar {
                objectName: "updateProgressBar"
                visible: vm.updateStatus === "downloading"
                from: 0
                to: 100
                value: vm.updateProgress
                Layout.fillWidth: true
                Layout.preferredHeight: 5
            }
        }

        ModernToolbarButton {
            objectName: "updateNotesButton"
            text: vm.strings["update_release_notes"] ?? "What's new"
            Layout.preferredWidth: 92
            implicitHeight: 30
            onClicked: vm.openUpdateRelease()
        }

        ModernToolbarButton {
            objectName: "updateSkipButton"
            text: vm.strings["update_skip"] ?? "Skip"
            Layout.preferredWidth: 72
            implicitHeight: 30
            enabled: vm.updateStatus !== "downloading"
            onClicked: vm.skipUpdate()
        }

        ModernToolbarButton {
            objectName: "updateLaterButton"
            text: vm.strings["update_later"] ?? "Later"
            Layout.preferredWidth: 72
            implicitHeight: 30
            enabled: vm.updateStatus !== "downloading"
            onClicked: vm.remindUpdateLater()
        }

        ModernToolbarButton {
            objectName: "updatePrimaryButton"
            accented: true
            text: vm.updateStatus === "ready"
                ? (vm.strings["update_install_restart"] ?? "Install and restart")
                : vm.updateStatus === "downloading"
                    ? (vm.strings["update_downloading"] ?? "Downloading…")
                    : (vm.strings["update_download"] ?? "Download update")
            Layout.preferredWidth: 142
            implicitHeight: 30
            enabled: vm.updateStatus !== "downloading"
                && !vm.isTranslating && !vm.isSingleTranslating && !vm.isXmlBusy
            onClicked: vm.updateStatus === "ready" ? vm.installUpdate() : vm.downloadUpdate()
        }
    }
}
