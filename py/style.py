
from PySide6.QtCore import QObject, Property, Slot, Signal
from PySide6.QtGui import QColor



class Noaa:
    # https://www.noaa.gov/office-of-communication/about-noaa-emblem-and-logo
    dark_blue = "#003087"  # Pantone 287 C
    dark_blue_alt_dark = '#00215e'
    dark_blue_alt_lite = '#33599f'
    light_blue = "#0085CA"  # Pantone Process Blue C
    light_blue_alt_dark = "#005d8d"  # Pantone Process Blue C
    light_blue_alt_lite = "#339dd4"  # Pantone Process Blue C


class DarkMode:
    # https://m2.material.io/design/color/dark-theme.html
    # https://stackoverflow.com/questions/36915508/what-are-the-material-design-dark-theme-colors

    # colors
    primary_color = Noaa.light_blue
    primary_color_alt_dark = Noaa.light_blue_alt_dark
    primary_color_alt_lite = Noaa.light_blue_alt_lite
    secondary_color = Noaa.dark_blue
    secondary_color_alt_dark = Noaa.dark_blue_alt_dark
    secondary_color_alt_lite = Noaa.dark_blue_alt_lite

    accent_color = '#FF00E676'  # vibrant green
    base_surface_color = '#121212'
    surface_color_l1 = '#1e1e1e'  # surface at 95% opacity / 01dp
    surface_color_l2 = '#222222'  # surface at 93% opacity / 02dp
    surface_color_l3 = '#242424'  # surface at 92% opacity / 03dp
    surface_color_l4 = '#272727'  # surface at 91% opacity / 04dp
    surface_color_l5 = '#2c2c2c'  # surface at 89% opacity / 05dp
    surface_color_l6 = '#2e2e2e'  # surface at 88% opacity / 06dp
    surface_color_l7 = '#333333'  # surface at 86% opacity / 07dp
    surface_color_l8 = '#343434'  # surface at 85% opacity / 08dp
    surface_color_l9 = '#383838'  # surface at 84% opacity / 09dp
    primary_font_color = '#FFFFFFFF'  # white
    secondary_font_color = '#B3FFFFFF'  # off white
    disabled_font_color = '#7c7c7d'  # disabled font color
    error_color = '#CF6679'
    icon_color = '#80FFFFFF'
    font_family = 'roboto'

class LiteMode:

    background = '#FFFFFF'
    error_color = '#B00020'
    accent_color = '#ff00ff'
    banner_color = Noaa.light_blue
    secondary_banner_color = Noaa.light_blue_alt_lite

    primary_color = Noaa.dark_blue
    surface_color_all = '#FFFFFFFF'
    primary_font_color = "#000000"  # black
    secondary_font_color = '#111111'  # tinted black
    icon_color = '#111111'  # light black

class GrayMode:
    # https://calcolor.co/palette/942409461

    primary_color = Noaa.dark_blue
    primary_color_alt_dark = Noaa.dark_blue_alt_dark
    primary_color_alt_lite = Noaa.dark_blue_alt_lite
    secondary_color = Noaa.light_blue
    secondary_color_alt_dark = Noaa.dark_blue_alt_dark
    secondary_color_alt_lite = Noaa.dark_blue_alt_lite

    # accent_cyan = '#00e5ff'  #
    accent_color = '#ff00ff'
    error_color = '#d32f2f'
    black = "#000000"
    primary_font_color = "#000000"  # black
    secondary_font_color = '#111111'  # tinted black
    base_surface_color = '#777777'  # medium gray
    surface_color_l1 = '#888888'  # tinted gray
    surface_color_l2 = '#999999'  # light gray
    surface_color_l3 = '#aaaaaa'  # pale gray
    surface_color_l4 = '#bbbbbb' # silver gray
    surface_color_l5 = '#cccccc'  # dark white
    surface_color_l6 = '#dddddd'  # shaded white
    surface_color_l7 = '#eeeeee'  # almost white
    icon_color = '#111111'  # light black



class Style(QObject):

    modeChanged = Signal()

    def __init__(self, app=None, parent=None):
        super().__init__(parent)
        self._app = app
        self._ui_mode = None
        self._set_ui_mode(self._app.settings.curUiMode)
        self._app.settings.uiModeChanged.connect(self._set_ui_mode)

    def _set_ui_mode(self, new_mode):
        print(f"UI MODE CHANGED TO {new_mode}")
        if new_mode.lower() == 'wheelhouse':
            new_mode = 'dark'

        if new_mode.lower() == 'backdeck':
            new_mode = 'gray'

        if new_mode.lower() == 'noaa':
            new_mode = 'lite'

        if self._ui_mode != new_mode:
            self._ui_mode = new_mode.lower()
            self.modeChanged.emit()

    @Property(QColor, notify=modeChanged)
    def primaryColor(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.primary_color)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.primary_color)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.primary_color)

        return QColor("white")

    @Property(QColor, notify=modeChanged)
    def primaryColorAltDark(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.primary_color_alt_dark)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.primary_color_alt_dark)
        if self._ui_mode == 'lite':
            return QColor(LiteMode.primary_color)

        return QColor("white")

    def onPrimaryColor(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.primary_color_alt_lite)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.primary_color_alt_lite)
        if self._ui_mode == 'lite':
            return QColor(LiteMode.primary_color)
        return QColor("white")
    @Property(QColor, notify=modeChanged)
    def accentColor(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.accent_color)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.accent_color)
        if self._ui_mode == 'lite':
            return QColor(LiteMode.accent_color)
        return QColor("white")

    @Property(QColor, notify=modeChanged)
    def surfaceColor(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.base_surface_color)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.base_surface_color)
        if self._ui_mode == 'lite':
            return QColor(LiteMode.banner_color)
        return QColor("white")

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L1(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l1)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l1)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L2(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l2)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l2)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L3(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l3)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l3)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L4(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l4)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l4)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L5(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l5)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l5)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L6(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l6)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l6)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L7(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l7)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l7)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L8(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l8)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l7)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)

    @Property(QColor, notify=modeChanged)
    def elevatedSurface_L9(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.surface_color_l9)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.surface_color_l7)
        if self._ui_mode.lower() == 'lite':
            return QColor(LiteMode.surface_color_all)


    @Property(QColor, notify=modeChanged)
    def primaryFontColor(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.primary_font_color)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.primary_font_color)
        if self._ui_mode == 'lite':
            return QColor(LiteMode.primary_font_color)
        return QColor("white")

    @Property(QColor, notify=modeChanged)
    def secondaryFontColor(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.secondary_font_color)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.secondary_font_color)
        if self._ui_mode == 'lite':
            return QColor(LiteMode.secondary_font_color)

        return QColor("white")

    @Property(QColor, notify=modeChanged)
    def disabledFontColor(self):
        return QColor('#7c7c7d')

    @Property(QColor, notify=modeChanged)
    def iconColor(self):
        if self._ui_mode.lower() == 'dark':
            return QColor(DarkMode.icon_color)
        if self._ui_mode.lower() == 'gray':
            return QColor(GrayMode.icon_color)
        if self._ui_mode == 'lite':
            return QColor(LiteMode.icon_color)
        return QColor("white")

    @Property(QColor, notify=modeChanged)
    def fontFamily(self):
        return 'roboto'

    @Property(QColor, notify=modeChanged)
    def errorColor(self):
        return QColor('#CF6679')


if __name__ == '__main__':
    print(Noaa.dark_blue)



