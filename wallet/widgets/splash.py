import asyncio

from PySide6.QtWidgets import QWidget
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from ..designer.splash import Ui_splash_widget


class SplashWidget(QWidget, Ui_splash_widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        asyncio.create_task(self.init())

    async def init(self):
        while True:
            self.progress_bar.value += 5
            await asyncio.sleep(0.1)
            if self.progress_bar.value == 100:
                self.close()
