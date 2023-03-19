import asyncio

import qtinter
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QApplication, QInputDialog, QLineEdit
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

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
        self.closing = False

        self.action_settings.triggered.connect(self.open_settings)
        self.action_exit.triggered.connect(self.close)
        self.action_unlock.triggered.connect(qtinter.asyncslot(self.unlock_wallet))
        self.action_lock.triggered.connect(qtinter.asyncslot(self.lock_wallet))
        self.action_list_addresses.triggered.connect(self.list_addresses)
        self.action_import_private_key.triggered.connect(qtinter.asyncslot(self.import_private_key))
        self.action_about.triggered.connect(self.about)

        # noinspection PyUnresolvedReferences
        self.status_bar.add_widget(self.status_bar_label)
        self.status_bar_label.text = "Wallet is locked"

        asyncio.create_task(self.init())

    async def init(self):
        if self.onboarding:
            self.onboarding_widget = OnboardingWidget(self)
            self.onboarding_widget.show()
            self.hide()
            self.wallet_core.event_dispatcher.register_event_handler(EventType.OnboardingComplete, self.continue_init)
            self.wallet_core.event_dispatcher.register_event_handler(EventType.OnboardingCancelled,
                                                                     self.cancel_onboarding)

    def open_settings(self):
        pass

    async def unlock_wallet(self):
        password = QInputDialog.get_text(self, "Unlock wallet", "Enter password:", QLineEdit.EchoMode.Password)
        if not password[1]:
            return
        password = password[0]
        unlocked = await self.wallet_core.wallet.unlock(password)
        if not unlocked:
            QMessageBox.critical(self, "Error", "Failed to unlock wallet")
            return
        self.status_bar_label.text = "Wallet is unlocked"
        self.action_lock.visible = True
        self.action_unlock.visible = False
        self.action_list_addresses.enabled = True
        self.action_import_private_key.enabled = True

    async def lock_wallet(self):
        await self.wallet_core.wallet.lock()
        self.status_bar_label.text = "Wallet is locked"
        self.action_lock.visible = False
        self.action_unlock.visible = True
        self.action_list_addresses.enabled = False
        self.action_import_private_key.enabled = False

    def list_addresses(self):
        pass

    async def import_private_key(self):
        pass

    def about(self):
        pass

    async def continue_init(self, _: EventType):
        await self.wallet_core.reload_wallet()

    async def cancel_onboarding(self, _: EventType):
        self.close()

    def close_event(self, event: QCloseEvent) -> None:
        if self.closing:
            event.accept()
            return
        event.ignore()
        msgbox = QMessageBox(QMessageBox.Icon.Question, "Exit",
                             "Are you sure you want to exit?",
                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, self)
        msgbox.button(QMessageBox.StandardButton.Yes).clicked.connect(self.confirm_close)
        msgbox.button(QMessageBox.StandardButton.No).clicked.connect(msgbox.delete_later)
        QApplication.instance().aboutToQuit.connect(msgbox.delete_later)
        msgbox.show()

    def confirm_close(self) -> None:
        self.closing = True
        self.close()
