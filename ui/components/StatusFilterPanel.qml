import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    spacing: 4
    Label {
        text: vm.strings["filter_status_title"]
        color: Theme.textSecondary
        wrapMode: Text.Wrap
        Layout.fillWidth: true
    }
    ComboBox {
        id: selector
        objectName: "statusFilterSelector"
        Layout.fillWidth: true
        readonly property var states: ["all", "pending", "translating", "translated", "confirmed", "error"]
        model: states.map(function(state) {
            return (state === "all" ? vm.strings["filter_all"] : vm.strings["state_" + state])
                + " · " + (vm.stateCounts[state] || 0)
        })
        currentIndex: states.indexOf(vm.statusFilter)
        Accessible.name: vm.strings["filter_status_title"]
        onActivated: function(index) { vm.setStatusFilter(states[index]) }

        contentItem: Text {
            leftPadding: 10
            rightPadding: 30
            text: selector.displayText
            font: selector.font
            color: Theme.textInput
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
        indicator: Text {
            x: selector.width - width - 10
            y: (selector.height - height) / 2
            text: "⌄"
            color: Theme.textSecondary
            font.pixelSize: 13
        }
        background: Rectangle {
            color: selector.enabled ? Theme.bgInput : Theme.bgBase
            border.color: selector.activeFocus || selector.popup.visible
                ? Theme.borderFocus : Theme.borderInput
            border.width: selector.activeFocus || selector.popup.visible ? 2 : 1
            radius: 4
        }

        delegate: ItemDelegate {
            required property int index
            required property string modelData
            width: selector.popup.availableWidth
            text: modelData
            highlighted: selector.highlightedIndex === index
            hoverEnabled: true
            contentItem: Text {
                text: parent.text
                font: selector.font
                color: Theme.textPrimary
                elide: Text.ElideRight
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle {
                radius: 4
                color: parent.highlighted || parent.hovered ? Theme.bgSurface3 : Theme.bgSurface2
                border.width: parent.highlighted ? 1 : 0
                border.color: Theme.borderFocus
            }
        }
        popup: Popup {
            objectName: "statusFilterPopup"
            y: selector.height
            width: selector.width
            implicitHeight: contentItem.implicitHeight + topPadding + bottomPadding
            padding: 4
            background: Rectangle {
                color: Theme.bgInput
                border.color: Theme.borderModerate
                radius: 6
            }
            contentItem: ListView {
                clip: true
                implicitHeight: contentHeight
                model: selector.popup.visible ? selector.delegateModel : null
                currentIndex: selector.highlightedIndex
                ScrollIndicator.vertical: ScrollIndicator { }
            }
        }
    }
}
