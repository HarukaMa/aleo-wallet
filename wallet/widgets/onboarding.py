import asyncio
from enum import IntEnum

import qtinter
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget, QMessageBox, QApplication
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from ..core import HDWallet
from ..designer.onboarding import Ui_onboarding
from ..events import EventType, Event


class OnboardingWidget(QWidget, Ui_onboarding):
    class Page(IntEnum):
        Start = 0
        Password = 1
        Mnemonic = 2
        MnemonicVerify = 3
        Finish = 4

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.next_button.clicked.connect(qtinter.asyncslot(self.next_clicked))
        self.new_wallet_radio.toggled.connect(self.new_wallet_radio_toggled)
        self.wizard_stack.currentChanged.connect(self.wizard_page_changed)
        self.main_window = main_window
        self.cancelled = False
        self.completed = False
        self.mode = 0
        self.new_wallet: HDWallet | None = None

    async def next_clicked(self):
        # before page change; previous page
        match self.wizard_stack.current_index:
            case self.Page.Start.value:
                if self.new_wallet_radio.checked:
                    self.mode = 1
                else:
                    self.mode = 2
            case self.Page.Password.value:
                self.next_button.enabled = False
                self.new_wallet = await HDWallet.create_wallet(self.password_input.text)
                await self.new_wallet.unlock(self.password_input.text)
        self.wizard_stack.current_index += 1

    def new_wallet_radio_toggled(self, checked):
        self.next_button.enabled = checked

    def wizard_page_changed(self, index):
        # after page change; current page
        match index:
            case self.Page.Password.value:
                self.next_button.enabled = False
                self.password_input.textChanged.connect(self.password_check)
                self.password_confirm_input.textChanged.connect(self.password_check)
            case self.Page.Mnemonic.value:
                asyncio.create_task(self.delayed_next())
                self.populate_mnemonic()
            case self.Page.Finish.value:
                self.next_button.text = "Finish"
                self.next_button.clicked.disconnect()
                self.next_button.clicked.connect(qtinter.asyncslot(self.finish_clicked))
                self.completed = True

    async def finish_clicked(self):
        await self.main_window.wallet_core.event_dispatcher.post_event(Event(EventType.OnboardingComplete, None))
        await self.new_wallet.close()
        self.main_window.show()
        self.close()

    async def delayed_next(self):
        await asyncio.sleep(5)
        self.next_button.enabled = True

    def populate_mnemonic(self):
        mnemonic = self.new_wallet.to_mnemonic().split(" ")
        self.word_1_label.text = mnemonic[0]
        self.word_2_label.text = mnemonic[1]
        self.word_3_label.text = mnemonic[2]
        self.word_4_label.text = mnemonic[3]
        self.word_5_label.text = mnemonic[4]
        self.word_6_label.text = mnemonic[5]
        self.word_7_label.text = mnemonic[6]
        self.word_8_label.text = mnemonic[7]
        self.word_9_label.text = mnemonic[8]
        self.word_10_label.text = mnemonic[9]
        self.word_11_label.text = mnemonic[10]
        self.word_12_label.text = mnemonic[11]

    def password_check(self):
        if self.password_input.text != "" and self.password_input.text == self.password_confirm_input.text:
            self.next_button.enabled = True
        else:
            self.next_button.enabled = False

    def close_event(self, event: QCloseEvent) -> None:
        if self.cancelled or self.completed:
            event.accept()
            return
        event.ignore()
        msgbox = QMessageBox(QMessageBox.Icon.Question, "Wallet not created",
                             "You have not created a wallet. Do you want to exit the program?",
                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, self)
        msgbox.button(QMessageBox.StandardButton.Yes).clicked.connect(qtinter.asyncslot(self.cancel_onboarding))
        msgbox.button(QMessageBox.StandardButton.No).clicked.connect(msgbox.delete_later)
        QApplication.instance().aboutToQuit.connect(msgbox.delete_later)
        msgbox.show()

    async def cancel_onboarding(self):
        self.cancelled = True
        if self.new_wallet is not None:
            await self.new_wallet.destroy()
        await self.main_window.wallet_core.event_dispatcher.post_event(EventType.OnboardingCancelled)
        QApplication.instance().quit()
        self.close()
