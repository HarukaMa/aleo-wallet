import asyncio

import qtinter
from PySide6.QtWidgets import QWidget, QMessageBox, QApplication
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from ..core import WalletCore
from ..designer.splash import Ui_splash_widget
from ..events import EventType
from ..utils.types import InitPhase


class SplashWidget(QWidget, Ui_splash_widget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.wallet_core = WalletCore()
        # noinspection PyUnresolvedReferences
        QApplication.instance().aboutToQuit.connect(qtinter.asyncslot(self.wallet_core.stop))
        asyncio.create_task(self.init())

    async def init(self):
        try:
            self.wallet_core.event_dispatcher.register_qt_event_receiver(self)
            self.progress_label.text = "Starting wallet core..."
            await self.wallet_core.start()
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", "Failed to start wallet core: \n\n" + traceback.format_exc())
            self.close()
            raise e

    def event(self, event):
        if event.type() == EventType.InitStep.value:
            phase = event.event.content
            self.progress_bar.value = phase.value
            match phase:
                case InitPhase.OpenChainDB:
                    self.progress_label.text = "Opening chain database..."
                case InitPhase.CreateChainDB:
                    self.progress_label.text = "Creating chain database..."
                case InitPhase.CheckChainDB:
                    self.progress_label.text = "Checking chain database integrity..."
                case InitPhase.Finish:
                    self.progress_label.text = "Done"

        return super().event(event)
