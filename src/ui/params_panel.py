# formulario de parámetros + validaciones
from __future__ import annotations
from PySide6 import QtWidgets


class ParamsPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        lay = QtWidgets.QFormLayout(self)
        self.path_cfg = QtWidgets.QLineEdit()
        self.path_btn = QtWidgets.QPushButton("...")
        hb = QtWidgets.QHBoxLayout()
        hb.addWidget(self.path_cfg)
        hb.addWidget(self.path_btn)
        self.semilla = QtWidgets.QSpinBox()
        self.semilla.setMaximum(10**9)
        self.semilla.setValue(2025)
        self.dias = QtWidgets.QSpinBox()
        self.dias.setMaximum(10**9)
        self.dias.setValue(365)
        self.i_filas = QtWidgets.QSpinBox()
        self.i_filas.setRange(1, 1000)
        self.i_filas.setValue(30)
        self.desde_j = QtWidgets.QSpinBox()
        self.desde_j.setRange(1, 10**9)
        self.desde_j.setValue(1)
        self.politica = QtWidgets.QComboBox()
        self.politica.addItems(["A", "B"])
        self.sim_btn = QtWidgets.QPushButton("Simular")

        lay.addRow("Config YAML:", hb)
        lay.addRow("Semilla:", self.semilla)
        lay.addRow("Días a simular:", self.dias)
        lay.addRow("Mostrar i filas:", self.i_filas)
        lay.addRow("Desde fila j:", self.desde_j)
        lay.addRow("Política:", self.politica)
        lay.addRow(self.sim_btn)

        self.path_btn.clicked.connect(self._pick)

    def _pick(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Elegir config", filter="YAML (*.yaml *.yml)")
        if p:
            self.path_cfg.setText(p)