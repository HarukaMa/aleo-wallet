import qtinter
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget, QMessageBox, QApplication
# noinspection PyUnresolvedReferences
from __feature__ import snake_case, true_property

from ..designer.onboarding import Ui_onboarding
from ..events import EventType


class OnboardingWidget(QWidget, Ui_onboarding):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.on_next_clicked)
        self.main_window = main_window
        self.cancelled = False

    def on_next_clicked(self):
        self.close()

    # noinspection PyUnresolvedReferences
    def close_event(self, event: QCloseEvent) -> None:
        if self.cancelled:
            event.accept()
            return
        event.ignore()
        msgbox = QMessageBox(QMessageBox.Question, "Wallet not created",
                             "You have not created a wallet. Do you want to exit the program?",
                             QMessageBox.Yes | QMessageBox.No, self)
        msgbox.button(QMessageBox.Yes).clicked.connect(qtinter.asyncslot(self.cancel_onboarding))
        msgbox.button(QMessageBox.No).clicked.connect(msgbox.delete_later)
        QApplication.instance().aboutToQuit.connect(msgbox.delete_later)
        msgbox.show()

    async def cancel_onboarding(self):
        self.cancelled = True
        await self.main_window.wallet_core.event_dispatcher.post_event(EventType.OnboardingCancelled)
        QApplication.instance().quit()
        self.close()
