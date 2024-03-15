
from PySide6.QtCore import QObject, Property, Slot, Signal
from PySide6.QtGui import QColor


# https://m2.material.io/design/color/dark-theme.html
# https://stackoverflow.com/questions/36915508/what-are-the-material-design-dark-theme-colors
class Style(QObject):

    modeChanged = Signal()

    def __init__(self, app=None, parent=None):
        super().__init__(parent)
        self._app = app
        self._ui_mode = "Dark"
        self._app.settings.uiModeChanged.connect(self._set_ui_mode)

    def _set_ui_mode(self, new_mode):
        print(f"UI MODE CHANGED TO {new_mode}")
        if self._ui_mode != new_mode:
            self._ui_mode = new_mode
            self.modeChanged.emit()

    @Property(QColor, notify=modeChanged)
    def primaryColor(self):
        return QColor('#0085CA')  #NOAA Pantone (light blue)

    @Property(QColor, notify=modeChanged)
    def onPrimaryColor(self):
        pass

    @Property(QColor, notify=modeChanged)
    def prirmaryColorVariant(self):
        pass

    @Property(QColor, notify=modeChanged)
    def accentColor(self):
        # return QColor('#f69833')  # orange
        return QColor('#FF00E676')

    @Property(QColor)
    def secondaryColor(self):
        pass

    @Property(QColor)
    def onSecondaryColor(self):
        pass

    @Property(QColor)
    def backgroundColor(self):
        pass

    @Property(QColor)
    def onBackgroundColor(self):
        pass

    @Property(QColor, notify=modeChanged)
    def surfaceColor(self):
        if self._ui_mode == 'Dark':
            return QColor('#121212')  # default surface base for dark material ui
        if self._ui_mode == 'Light':
            return QColor('white')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L1(self):
        return QColor('#1e1e1e')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L2(self):
        return QColor('#222222')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L3(self):
        return QColor('#242424')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L4(self):
        return QColor('#272727')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L5(self):
        return QColor('#2c2c2c')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L6(self):
        return QColor('#2e2e2e')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L7(self):
        return QColor('#333333')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L8(self):
        return QColor('#343434')

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L9(self):
        return QColor('#383838')

    @Property(QColor)
    def onSurfaceColor(self):
        pass

    @Property(QColor, notify=modeChanged)
    def primaryFontColor(self):
        if self._ui_mode == 'Dark':
            return QColor("#FFFFFFFF")
        if self._ui_mode == 'Light':
            return QColor("Black")

    @Property(QColor, notify=modeChanged)
    def secondaryFontColor(self):
        if self._ui_mode == 'Dark':
            return QColor('#B3FFFFFF')
        if self._ui_mode == 'Light':
            return QColor('Gray')

    @Property(QColor, notify=modeChanged)
    def disabledFontColor(self):
        return QColor('#7c7c7d')

    @Property(QColor, notify=modeChanged)
    def iconColor(self):
        return QColor("#80FFFFFF")

    @Property(QColor, notify=modeChanged)
    def fontFamily(self):
        return 'roboto'

    @Property(QColor, notify=modeChanged)
    def errorColor(self):
        return QColor('#CF6679')


if __name__ == '__main__':
    pass



