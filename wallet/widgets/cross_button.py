import sys

from PySide6.QtWidgets import QPushButton
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property


class CrossPushButton(QPushButton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if sys.platform == "darwin":
            self.minimum_height = 32
        else:
            self.minimum_height = 23
