# ventana principal, menú, tabs
from __future__ import annotations
from PySide6 import QtCore, QtWidgets
from dataclasses import asdict
from src.config.loader import Config
from src.ui.params_panel import ParamsPanel
from src.ui.table_view import DictTableModel
from src.ui.report_panel import ReportPanel
from src.sim.engine import Engine
from src.domain.costs import CostosCfg, Tramo
from src.domain.policies import PolicyA, PolicyB
from src.sim.runner import SimWorker


HEADERS = [
'dia','rnd_demanda','demanda_dec','llegadas_dec','stock_ini_dec','ventas_dec','faltantes_dec','stock_fin_dec',
'pedido_hoy_dec','rnd_demora','demora_dias','orden_en_curso',
'costo_almacen','costo_ruptura','costo_pedido',
'AC_cost_almacen','AC_cost_ruptura','AC_cost_pedido','AC_cost_total',
'AC_demanda_uni','AC_ventas_uni','AC_faltantes_uni','AC_pedidos','fill_rate','costo_promedio_dia'
]

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StockSim – Monte Carlo")

        self.params = ParamsPanel()
        self.table = QtWidgets.QTableView(); self.model = DictTableModel(HEADERS); self.table.setModel(self.model)
        self.report = ReportPanel()

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.params, "Parámetros")
        tabs.addTab(self.table, "Vector de estado")
        tabs.addTab(self.report, "Informes")
        self.setCentralWidget(tabs)

        self.params.sim_btn.clicked.connect(self.simular)

        # barra de progreso + cancelar
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.cancel_btn = QtWidgets.QPushButton("Cancelar")
        self.cancel_btn.setEnabled(False)
        sb = QtWidgets.QToolBar()
        sb.addWidget(self.progress)
        sb.addWidget(self.cancel_btn)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, sb)

        self.params.sim_btn.clicked.connect(self.simular)
        self.cancel_btn.clicked.connect(self._cancelar)

        self._worker = None  # referencia al worker

    def _cancelar(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self.cancel_btn.setEnabled(False)

    def _build_engine(self, merged: dict, cfg: Config) -> Engine:
        costos = CostosCfg(
            c_almacen_uni_dia=cfg.costos.almacenamiento_por_unidad_por_dia,
            c_ruptura_uni_dia=cfg.costos.ruptura_por_unidad_por_dia,
            tramos=[Tramo(t['min_decenas'], t['max_decenas'], t['costo']) for t in merged['costos_tramos']]
        )
        if merged['politica'] == 'A':
            pol = PolicyA(cfg.politica_A.periodo_dias, cfg.politica_A.cantidad_decenas)
        else:
            pol = PolicyB(cfg.politica_B.periodo_dias, cfg.politica_B.ventana_historial_dias)

        eng = Engine(
            N_dias=merged['N_dias'],
            stock_inicial_dec=cfg.stock_inicial_decenas,
            pedido_primer_dia=merged['pedido_primer_dia'],
            demanda_values=merged['demanda']['valores'],
            demanda_probs=merged['demanda']['probabilidades'],
            demora_values=merged['demora']['valores'],
            demora_probs=merged['demora']['probabilidades'],
            costos_cfg=costos,
            policy=pol,
            semilla=merged.get('semilla') or cfg.semilla,
        )
        return eng

    def simular(self):
        try:
            overrides = self.params.get_overrides()
            path = overrides.get('path_cfg')
            cfg = Config.from_yaml(path)

            merged = {
                'N_dias': overrides['N_dias'] or cfg.N_dias,
                'i_filas': overrides['i_filas'] or cfg.mostrar.i_filas,
                'desde_j': overrides['desde_j'] or cfg.mostrar.desde_fila_j,
                'politica': overrides['politica'] or cfg.politica,
                'pedido_primer_dia': overrides['pedido_primer_dia'] if overrides['pedido_primer_dia'] is not None else cfg.pedido_primer_dia,
                'demanda': overrides['demanda'],
                'demora': overrides['demora'],
                'costos_tramos': overrides['costos_tramos'],
                'semilla': overrides.get('semilla') or cfg.semilla,
            }

            eng = self._build_engine(merged, cfg)

            self.model.clear()
            i = merged['i_filas']
            j = merged['desde_j']
            last_row = None

            for row in eng.run():
                last_row = asdict(row)
                if j <= row.dia < j + i:
                    self.model.append_row(asdict(row))

            if last_row:
                self.model.append_row(last_row)  # agregar última fila N
                # Mostrar informe con parámetros + KPIs
                self.report.show_report(
                    params={k: merged[k] for k in ('N_dias','i_filas','desde_j','politica','demanda','demora','costos_tramos')},
                    last_row=last_row,
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error de simulación", str(e))

