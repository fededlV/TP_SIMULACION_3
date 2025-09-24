 # punto de entrada (inicia la GUI)
from __future__ import annotations
import sys
from PySide6 import QtWidgets
from src.ui.main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(1200, 700)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()