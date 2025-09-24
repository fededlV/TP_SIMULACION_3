# KPIs/plots (costos, fill rate, etc.)
from __future__ import annotations
from PySide6 import QtWidgets


class ReportPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text = QtWidgets.QTextEdit(readOnly=True)
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.text)

    def show_kpis(self, last_row: dict):
        fmt = (
            f"\nDía: {last_row['dia']}\n"
            f"AC costo total: ${last_row['AC_cost_total']:.2f}\n"
            f"AC costo almacen: ${last_row['AC_cost_almacen']:.2f}\n"
            f"AC costo ruptura: ${last_row['AC_cost_ruptura']:.2f}\n"
            f"AC costo pedido: ${last_row['AC_cost_pedido']:.2f}\n"
            f"Fill rate: {last_row['fill_rate']:.4f}\n"
            f"Costo promedio día: ${last_row['costo_promedio_dia']:.2f}\n"
        )
        self.text.setPlainText(fmt)
