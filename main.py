import qtinter
from PySide6 import QtWidgets

if __name__ == '__main__':
    with qtinter.using_asyncio_from_qt():
        app = QtWidgets.QApplication()
        window = QtWidgets.QWidget()
        window.show()
        app.exec()
