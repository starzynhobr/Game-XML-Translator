import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.FluentWinUI3

// Searchable multi-tag selector. Selection state remains owned by the ViewModel;
// this component only renders chips and emits add/remove intents.
Item {
    id: root

    property var suggestions: []
    property var selectedValues: []
    property var excludedValues: []
    property string placeholderText: ""
    property string roleMarker: "T"
    property string roleDescription: "Target"
    property string removeText: "Remove"
    property color accentColor: Theme.primary

    signal addRequested(string tag)
    signal removeRequested(string tag)

    implicitHeight: content.implicitHeight

    function _contains(values, candidate) {
        if (!values)
            return false
        for (var i = 0; i < values.length; i++) {
            if (values[i] === candidate)
                return true
        }
        return false
    }

    function _availableSuggestions() {
        var result = []
        for (var i = 0; i < root.suggestions.length; i++) {
            var tag = root.suggestions[i]
            if (!root._contains(root.selectedValues, tag)
                    && !root._contains(root.excludedValues, tag))
                result.push(tag)
        }
        return result
    }

    ColumnLayout {
        id: content
        width: parent.width
        spacing: 6

        Flow {
            id: chipFlow
            visible: root.selectedValues.length > 0
            Layout.fillWidth: true
            Layout.preferredHeight: visible ? childrenRect.height : 0
            spacing: 5

            Repeater {
                model: root.selectedValues

                delegate: Rectangle {
                    id: chip
                    required property string modelData
                    width: chipContent.implicitWidth + 12
                    height: 27
                    radius: 5
                    color: Theme.bgSurface3
                    border.color: root.accentColor
                    border.width: 1

                    RowLayout {
                        id: chipContent
                        anchors { fill: parent; leftMargin: 7; rightMargin: 2 }
                        spacing: 4

                        Label {
                            text: root.roleMarker
                            color: root.accentColor
                            font.pixelSize: 10
                            font.weight: Font.Bold
                            Accessible.name: root.roleDescription
                        }

                        Label {
                            text: chip.modelData
                            color: Theme.textPrimary
                            font.pixelSize: 12
                        }

                        ToolButton {
                            id: removeButton
                            text: "×"
                            implicitWidth: 22
                            implicitHeight: 22
                            focusPolicy: Qt.StrongFocus
                            Accessible.name: root.removeText + " " + chip.modelData
                            ToolTip.visible: hovered
                            ToolTip.delay: 400
                            ToolTip.text: Accessible.name
                            onClicked: root.removeRequested(chip.modelData)

                            background: Rectangle {
                                color: removeButton.hovered || removeButton.activeFocus
                                    ? Theme.bgSurface2 : "transparent"
                                radius: 4
                            }
                            contentItem: Label {
                                text: removeButton.text
                                color: removeButton.hovered || removeButton.activeFocus
                                    ? root.accentColor : Theme.textSecondary
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 15
                            }
                        }
                    }
                }
            }
        }

        TagComboBox {
            id: picker
            Layout.fillWidth: true
            suggestions: root._availableSuggestions()
            placeholderText: root.placeholderText
            commitOnTyping: false
            enabled: root.enabled
            Accessible.name: root.roleDescription

            onCommitted: function(tag) {
                var cleanTag = tag.trim()
                if (cleanTag !== "" && !root._contains(root.selectedValues, cleanTag)
                        && !root._contains(root.excludedValues, cleanTag)) {
                    root.addRequested(cleanTag)
                    picker.value = ""
                }
            }
        }
    }
}
