import sys

import qtinter
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from .widgets.splash import SplashWidget


def main():
    with qtinter.using_asyncio_from_qt():
        app = QtWidgets.QApplication()
        window = SplashWidget()
        window.set_window_flags(Qt.FramelessWindowHint)
        window.show()
        sys.exit(app.exec())


if __name__ == '__main__':
    main()
