
from PySide6.QtCore import QObject, Property, Slot, Signal
from PySide6.QtGui import QColor

class Style(QObject):

    styleChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    @Property(QColor)
    def primaryColor(self):
        pass

    @Property(QColor)
    def onPrimaryColor(self):
        pass

    @Property(QColor)
    def prirmaryColorVariant(self):
        pass

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

    @Property(QColor)
    def surfaceColor(self):
        pass

    @Property(QColor)
    def onSurfaceColor(self):
        pass

    @Property(QColor)
    def fontColor(self):
        return QColor("#FFFFFF")

    @Property(QColor)
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

    @Property(QColor)
    def errorColor(self):
        return QColor('#CF6679')


if __name__ == '__main__':
    s = Style
    print(s.errorColor)



