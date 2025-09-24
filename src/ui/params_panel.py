# formulario de parámetros + validaciones
from __future__ import annotations
from PySide6 import QtWidgets
from typing import List, Tuple

class DistributionTable(QtWidgets.QTableWidget):
    def __init__(self, rows: int, parent=None):
        super().__init__(rows, 2, parent)
        self.setHorizontalHeaderLabels(["Valor", "Probabilidad"])
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

    def set_defaults(self, valores: List[int], probs: List[float]):
        self.setRowCount(max(len(valores), len(probs)))
        for r, v in enumerate(valores):
            self.setItem(r, 0, QtWidgets.QTableWidgetItem(str(v)))
        for r, p in enumerate(probs):
            self.setItem(r, 1, QtWidgets.QTableWidgetItem(str(p)))

    def get_values_probs(self) -> Tuple[List[int], List[float]]:
        valores, probs = [], []
        for r in range(self.rowCount()):
            v_item = self.item(r, 0)
            p_item = self.item(r, 1)
            if not v_item and not p_item:
                continue
            v = int((v_item.text() if v_item else "0").strip())
            p = float((p_item.text() if p_item else "0").strip())
            valores.append(v)
            probs.append(p)
        # Normalización opcional si no suma 1 (aviso suave)
        s = sum(probs)
        if s <= 0:
            raise ValueError("Las probabilidades deben ser > 0 y sumar 1.")
        if abs(s - 1.0) > 1e-6:
            probs = [p / s for p in probs]
        return valores, probs

class TramosTable(QtWidgets.QTableWidget):
    def __init__(self, rows: int = 3, parent=None):
        super().__init__(rows, 3, parent)
        self.setHorizontalHeaderLabels(["Min decenas", "Max decenas (vacío=∞)", "Costo"])
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

    def set_defaults(self, tramos: List[tuple[int, int | None, float]]):
        self.setRowCount(len(tramos))
        for r, (mn, mx, c) in enumerate(tramos):
            self.setItem(r, 0, QtWidgets.QTableWidgetItem(str(mn)))
            self.setItem(r, 1, QtWidgets.QTableWidgetItem("" if mx is None else str(mx)))
            self.setItem(r, 2, QtWidgets.QTableWidgetItem(str(c)))

    def get_tramos(self) -> List[dict]:
        out = []
        for r in range(self.rowCount()):
            mn_item = self.item(r, 0)
            mx_item = self.item(r, 1)
            c_item  = self.item(r, 2)
            if not mn_item and not mx_item and not c_item:
                continue
            mn = int((mn_item.text() if mn_item else "0").strip())
            mx_txt = (mx_item.text() if mx_item else "").strip()
            mx = int(mx_txt) if mx_txt else None
            c = float((c_item.text() if c_item else "0").strip())
            out.append({"min_decenas": mn, "max_decenas": mx, "costo": c})
        if not out:
            raise ValueError("Debe definir al menos un tramo de costos de pedido.")
        return out

class ParamsPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        lay = QtWidgets.QVBoxLayout(self)

        # Ruta YAML
        hl = QtWidgets.QHBoxLayout()
        self.path_cfg = QtWidgets.QLineEdit()
        self.path_btn = QtWidgets.QPushButton("...")
        self.path_btn.clicked.connect(self._pick)
        hl.addWidget(self.path_cfg); hl.addWidget(self.path_btn)

        # Controles básicos
        form = QtWidgets.QFormLayout()
        self.semilla = QtWidgets.QSpinBox(); self.semilla.setMaximum(10**9); self.semilla.setValue(2025)
        self.dias = QtWidgets.QSpinBox(); self.dias.setMaximum(10**9); self.dias.setValue(365)
        self.i_filas = QtWidgets.QSpinBox(); self.i_filas.setRange(1, 1000000); self.i_filas.setValue(30)
        self.desde_j = QtWidgets.QSpinBox(); self.desde_j.setRange(1, 10**9); self.desde_j.setValue(1)
        self.politica = QtWidgets.QComboBox(); self.politica.addItems(["A","B"])
        form.addRow("Semilla:", self.semilla)
        form.addRow("Tiempo a simular (días):", self.dias)
        form.addRow("Vector de estado – i filas:", self.i_filas)
        form.addRow("Desde fila j:", self.desde_j)
        form.addRow("Política:", self.politica)

        # Tablas de parámetros editables
        gb_dem = QtWidgets.QGroupBox("Demanda por día (decenas)")
        vb_dem = QtWidgets.QVBoxLayout(gb_dem)
        self.tbl_demanda = DistributionTable(6)
        self.tbl_demanda.set_defaults([0,10,20,30,40,50], [0.05,0.12,0.18,0.25,0.22,0.18])
        vb_dem.addWidget(self.tbl_demanda)

        gb_del = QtWidgets.QGroupBox("Demora de entrega (días)")
        vb_del = QtWidgets.QVBoxLayout(gb_del)
        self.tbl_demora = DistributionTable(4)
        self.tbl_demora.set_defaults([1,2,3,4], [0.15,0.20,0.40,0.25])
        vb_del.addWidget(self.tbl_demora)

        gb_tr = QtWidgets.QGroupBox("Costo de pedido por tramo (decenas)")
        vb_tr = QtWidgets.QVBoxLayout(gb_tr)
        self.tbl_tramos = TramosTable(3)
        self.tbl_tramos.set_defaults([
            (0,   100, 2000.0),
            (101, 200, 2800.0),
            (201, None, 3000.0),
        ])
        vb_tr.addWidget(self.tbl_tramos)

        # Botón simular
        self.sim_btn = QtWidgets.QPushButton("Simular")

        # Layout final
        lay.addLayout(hl)
        lay.addLayout(form)
        lay.addWidget(gb_dem)
        lay.addWidget(gb_del)
        lay.addWidget(gb_tr)
        lay.addWidget(self.sim_btn)

    def _pick(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Elegir config", filter="YAML (*.yaml *.yml)")
        if p:
            self.path_cfg.setText(p)

    # --- Overrides a partir de la UI ---
    def get_overrides(self) -> dict:
        valores_dem, probs_dem = self.tbl_demanda.get_values_probs()
        valores_del, probs_del = self.tbl_demora.get_values_probs()
        tramos = self.tbl_tramos.get_tramos()
        return {
            "N_dias": int(self.dias.value()),
            "i_filas": int(self.i_filas.value()),
            "desde_j": int(self.desde_j.value()),
            "politica": self.politica.currentText(),
            "demanda": {"valores": valores_dem, "probabilidades": probs_dem},
            "demora":  {"valores": valores_del, "probabilidades": probs_del},
            "costos_tramos": tramos,
            "semilla": int(self.semilla.value()),
            "path_cfg": self.path_cfg.text().strip() or None,
        }

""" class ParamsPanel(QtWidgets.QWidget):
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
            self.path_cfg.setText(p) """