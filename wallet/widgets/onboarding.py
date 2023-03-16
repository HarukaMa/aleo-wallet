from PySide6.QtWidgets import QWidget

from ..designer.onboarding import Ui_onboarding


class OnboardingWidget(QWidget, Ui_onboarding):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.on_next_clicked)
        self.main_window = main_window

    def on_next_clicked(self):
        self.main_window.show()
        self.close()
