import QtQuick
import QtQuick.Controls
import QtQuick.Controls.FluentWinUI3

AppButton {
    id: control

    property bool accented: false

    implicitHeight: 36
    font.pixelSize: 12
    font.weight: accented ? Font.DemiBold : Font.Medium

    background: Rectangle {
        color: !control.enabled
            ? Theme.bgBase
            : control.accented
                ? (control.hovered ? Theme.primaryHover : Theme.primary)
                : (control.hovered ? Theme.bgSurface3 : Theme.bgSurface2)
        radius: 5
        border.color: !control.enabled
            ? Theme.borderSubtle
            : control.accented ? "transparent" : Theme.borderModerate
        border.width: 1
        Behavior on color { ColorAnimation { duration: 100 } }
    }

    contentItem: Label {
        text: control.text
        color: !control.enabled
            ? Theme.textDisabled
            : control.accented ? Theme.onPrimary : Theme.textPrimary
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
}
