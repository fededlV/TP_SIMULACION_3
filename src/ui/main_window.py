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
        self.table = QtWidgets.QTableView()
        self.model = DictTableModel(HEADERS)
        self.table.setModel(self.model)
        self.report = ReportPanel()

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.params, "Parámetros")
        tabs.addTab(self.table, "Vector de estado")
        tabs.addTab(self.report, "Informes")
        self.setCentralWidget(tabs)

        self.params.sim_btn.clicked.connect(self.simular)

    def _build_engine(self, cfg: Config) -> Engine:
        costos = CostosCfg(
            c_almacen_uni_dia=cfg.costos.almacenamiento_por_unidad_por_dia,
            c_ruptura_uni_dia=cfg.costos.ruptura_por_unidad_por_dia,
            tramos=[Tramo(t.min_decenas, t.max_decenas, t.costo) for t in cfg.costos.pedido_por_tramo]
        )
        if self.params.politica.currentText() == 'A' or cfg.politica.upper() == 'A':
            pol = PolicyA(cfg.politica_A.periodo_dias, cfg.politica_A.cantidad_decenas)
        else:
            pol = PolicyB(cfg.politica_B.periodo_dias, cfg.politica_B.ventana_historial_dias)

        eng = Engine(
            N_dias=self.params.dias.value() or cfg.N_dias,
            stock_inicial_dec=cfg.stock_inicial_decenas,
            pedido_primer_dia=cfg.pedido_primer_dia,
            demanda_values=cfg.demanda.valores,
            demanda_probs=cfg.demanda.probabilidades,
            demora_values=cfg.demora.valores,
            demora_probs=cfg.demora.probabilidades,
            costos_cfg=costos,
            policy=pol,
            semilla=self.params.semilla.value() if self.params.semilla.value() else cfg.semilla,
        )
        return eng

    def simular(self):
        # cargar config
        path = self.params.path_cfg.text().strip() or 'data/ejemplos/config_ejemplo.yaml'
        cfg = Config.from_yaml(path)
        eng = self._build_engine(cfg)

        self.model.clear()
        i = self.params.i_filas.value() or cfg.mostrar.i_filas
        j = self.params.desde_j.value() or cfg.mostrar.desde_fila_j
        last_row = None

        # stream: sólo filas j..j+i-1 y la última
        for row in eng.run():
            last_row = asdict(row)
            if j <= row.dia < j + i:
                self.model.append_row(asdict(row))
        if last_row:
            self.model.append_row(last_row)
            self.report.show_kpis(last_row)
