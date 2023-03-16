import asyncio

from PySide6.QtWidgets import QMainWindow

from .onboarding import OnboardingWidget
from ..core import WalletCore
from ..designer.main_window import Ui_main_window
from ..events import EventType


class MainWindow(QMainWindow, Ui_main_window):
    def __init__(self, wallet_core: WalletCore, onboarding, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.wallet_core = wallet_core
        self.onboarding = onboarding
        asyncio.create_task(self.init())

    async def init(self):
        if self.onboarding:
            self.onboarding_widget = OnboardingWidget(self)
            self.onboarding_widget.show()
            self.hide()
            self.wallet_core.event_dispatcher.register_event_handler(EventType.OnboardingComplete, self.continue_init)

    async def continue_init(self, _: EventType):
        await self.wallet_core.reload_wallet()
