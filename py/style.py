
from PySide6.QtCore import QObject, Property, Slot, Signal
from PySide6.QtGui import QColor


# https://m2.material.io/design/color/dark-theme.html
# https://stackoverflow.com/questions/36915508/what-are-the-material-design-dark-theme-colors
class Style(QObject):

    modeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

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
        return QColor('#121212')

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
        return QColor("#FFFFFFFF")

    @Property(QColor, notify=modeChanged)
    def secondaryFontColor(self):
        return QColor('#B3FFFFFF')

    @Property(QColor, notify=modeChanged)
    def iconColor(self):
        return QColor("#80FFFFFF")

    @Property(QColor, notify=modeChanged)
    def fontFamily(self):
        return 'roboto'

    @Property(float)
    def fontOpacityHE(self):
        return 0.87

    @Property(float)
    def fontOpacityME(self):
        return 0.6

    @Property(float)
    def disabledFontOpacity(self):
        return 0.38

    @Property(QColor, notify=modeChanged)
    def errorColor(self):
        return QColor('#CF6679')


if __name__ == '__main__':
    pass



