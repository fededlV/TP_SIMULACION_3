# KPIs/plots (costos, fill rate, etc.)
from __future__ import annotations
from PySide6 import QtWidgets


class ReportPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.text = QtWidgets.QTextEdit(readOnly=True)
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.text)

    def show_report(self, params: dict, last_row: dict):
        # formateo de parámetros clave
        dem = params.get('demanda', {})
        demora = params.get('demora', {})
        tramos = params.get('costos_tramos', [])
        polit = params.get('politica', '-')
        N = params.get('N_dias', '-')
        i = params.get('i_filas', '-')
        j = params.get('desde_j', '-')

        def fmt_pairs(vals, probs):
            return ", ".join(f"{v}:{p:.3f}" for v, p in zip(vals or [], probs or []))

        dem_s = fmt_pairs(dem.get('valores'), dem.get('probabilidades'))
        demora_s = fmt_pairs(demora.get('valores'), demora.get('probabilidades'))
        tr_s = ", ".join(
            f"[{t['min_decenas']}-{t['max_decenas'] if t['max_decenas'] is not None else '∞'} => ${t['costo']}]"
            for t in tramos
        )

        report = [
            "Parámetros usados:",
            f"  Política: {polit}",
            f"  Días simulados: {N}",
            f"  Ventana tabla: i={i}, desde j={j}",
            f"  Demanda(decenas): {dem_s}",
            f"  Demora(días): {demora_s}",
            f"  Costos por tramo: {tr_s}",
            "",
            "Resultados (último día):",
            f"  Día: {last_row['dia']}",
            f"  AC costo total: ${last_row['AC_cost_total']:.2f}",
            f"  AC costo almacén: ${last_row['AC_cost_almacen']:.2f}",
            f"  AC costo ruptura: ${last_row['AC_cost_ruptura']:.2f}",
            f"  AC costo pedido: ${last_row['AC_cost_pedido']:.2f}",
            f"  Fill rate: {last_row['fill_rate']*100:.2f}%",
            f"  Costo promedio día: ${last_row['costo_promedio_dia']:.2f}",
        ]
        self.text.setPlainText("\n".join(report))


""" class ReportPanel(QtWidgets.QWidget):
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
            #f"Fill rate: {last_row['fill_rate']:.4f}\n"
            f"Fill rate: {last_row['fill_rate']*100:.2f}%\n"
            f"Costo promedio día: ${last_row['costo_promedio_dia']:.2f}\n"
        )
        self.text.setPlainText(fmt)
 """