 # bucle de simulación (generator/iterador)
from __future__ import annotations
from typing import Dict, List
import numpy as np
from src.domain.state import Row, DECENA
from src.domain.distributions import DiscreteSampler
from src.domain.policies import PolicyA, PolicyB
from src.domain.costs import CostosCfg, Tramo
import sys 
print("ENGINE LOADED FROM:", __file__, file=sys.stderr)

class Engine:
    def __init__(
        self,
        N_dias: int,
        stock_inicial_dec: int,
        pedido_primer_dia: bool,
        demanda_values: list[int], demanda_probs: list[float],
        demora_values: list[int], demora_probs: list[float],
        costos_cfg: CostosCfg,
        policy: PolicyA | PolicyB,
        semilla: int | None = None
    ):
        self.N = N_dias
        self.stock = stock_inicial_dec
        self.pedido_primer_dia = pedido_primer_dia
        self.costos = costos_cfg
        self.policy = policy

        self.rng = np.random.default_rng(semilla)
        self.demanda = DiscreteSampler(demanda_values, demanda_probs, self.rng)
        self.demora = DiscreteSampler(demora_values, demora_probs, self.rng)

        # calendario de llegadas: dia -> cantidad_dec
        self.arrivals: Dict[int, int] = {}
        # historial de demanda diaria (en decenas)
        self.historial_demanda: List[int] = []

        # acumuladores
        self.AC_cost_almacen = 0.0
        self.AC_cost_ruptura = 0.0
        self.AC_cost_pedido = 0.0
        self.AC_cost_total = 0.0
        self.AC_demanda_uni = 0
        self.AC_ventas_uni = 0
        self.AC_faltantes_uni = 0
        self.AC_pedidos = 0

    def _aplicar_llegadas(self, dia: int) -> int:
        """ llegadas_dec = self.arrivals.pop(dia, 0)
        self.stock += llegadas_dec
        return llegadas_dec """
        return self.arrivals.pop(dia, 0)

    def run(self):
        for dia in range(1, self.N + 1):
            # 1) Llegadas al INICIO del día
            llegadas_dec = self._aplicar_llegadas(dia)
            self.stock += llegadas_dec

            # 2) Stock inicial (después de sumar llegadas)
            stock_ini = self.stock

            # 3) Demanda del día y ventas
            rnd_demanda, demanda_dec = self.demanda.sample()
            self.historial_demanda.append(demanda_dec)

            ventas_dec = min(stock_ini, demanda_dec)
            faltantes_dec = max(0, demanda_dec - stock_ini)

            # Actualizar stock
            self.stock = stock_ini - ventas_dec
            stock_fin = self.stock

            # 4) Costos del día (unidades)
            DECENA = 10
            stock_promedio_uni = ((stock_ini + stock_fin) / 2) * DECENA
            costo_almacen = stock_promedio_uni * self.costos.c_almacen_uni_dia
            costo_ruptura = (faltantes_dec * DECENA) * self.costos.c_ruptura_uni_dia

            # Variables de este día (pueden acumular múltiples pedidos)
            costo_pedido = 0.0
            pedido_hoy_dec = 0
            rnd_demora = None
            demora_dias = None

            # 5) Pedido inicial día 1 (independiente de la política)
            if self.pedido_primer_dia and dia == 1:
                if isinstance(self.policy, PolicyA):
                    cant_inicial = self.policy.cantidad_dec
                else:  # PolicyB
                    cant_inicial = max(0, sum(self.historial_demanda[-self.policy.ventana:]))
                if cant_inicial > 0:
                    u0, d0 = self.demora.sample()
                    self._agendar_llegada(dia, cant_inicial, d0)
                    c0 = self.costos.costo_pedido(cant_inicial)
                    self.AC_cost_pedido += c0
                    self.AC_pedidos += 1
                    pedido_hoy_dec += cant_inicial
                    rnd_demora = u0
                    demora_dias = d0

            # 6) Pedido al FINAL del día
            cant_pedir = self.policy.cantidad_a_pedir(dia, self.historial_demanda)
            if cant_pedir > 0:
                pedido_hoy_dec = cant_pedir
                rnd_demora, demora_dias = self.demora.sample()
                self._agendar_llegada(dia, cant_pedir, demora_dias)
                costo_pedido = self.costos.costo_pedido(cant_pedir)
                self.AC_cost_pedido += costo_pedido
                self.AC_pedidos += 1

            # 7) Acumuladores
            self.AC_cost_almacen += costo_almacen
            self.AC_cost_ruptura += costo_ruptura
            self.AC_cost_total += (costo_almacen + costo_ruptura + self.AC_cost_pedido - self.AC_cost_pedido + c0 if 'c0' in locals() else 0)
            # Nota: AC_cost_total ya suma costo_pedido más arriba al momento de emitirlo;
            # por claridad preferimos sumar el total del día explícitamente:
            self.AC_cost_total += costo_almacen + costo_ruptura  # costo_pedido ya fue acumulado cuando se emitió

            self.AC_demanda_uni += demanda_dec * DECENA
            self.AC_ventas_uni += ventas_dec * DECENA
            self.AC_faltantes_uni += faltantes_dec * DECENA

            fill_rate = (self.AC_ventas_uni / self.AC_demanda_uni) if self.AC_demanda_uni else 1.0
            costo_prom_dia = self.AC_cost_total / dia

            # Próxima llegada (solo display)
            proximas = [f"{cant} @ d{d}" for d, cant in sorted(self.arrivals.items()) if d >= dia+1]
            orden_en_curso = proximas[0] if proximas else "-"

            # 8) Emitir fila
            yield Row(
                dia=dia,
                rnd_demanda=rnd_demanda,
                demanda_dec=demanda_dec,
                llegadas_dec=llegadas_dec,
                stock_ini_dec=stock_ini,
                ventas_dec=ventas_dec,
                faltantes_dec=faltantes_dec,
                stock_fin_dec=stock_fin,
                pedido_hoy_dec=pedido_hoy_dec,
                rnd_demora=rnd_demora,
                demora_dias=demora_dias,
                orden_en_curso=orden_en_curso,
                costo_almacen=costo_almacen,
                costo_ruptura=costo_ruptura,
                costo_pedido=costo_pedido,
                AC_cost_almacen=self.AC_cost_almacen,
                AC_cost_ruptura=self.AC_cost_ruptura,
                AC_cost_pedido=self.AC_cost_pedido,
                AC_cost_total=self.AC_cost_total,
                AC_demanda_uni=self.AC_demanda_uni,
                AC_ventas_uni=self.AC_ventas_uni,
                AC_faltantes_uni=self.AC_faltantes_uni,
                AC_pedidos=self.AC_pedidos,
                fill_rate=fill_rate,
                costo_promedio_dia=costo_prom_dia,
            )


    def _agendar_llegada(self, dia: int, cantidad_dec: int, demora_dias: int):
        """ llegada_dia = dia + demora_dias
        self.arrivals[llegada_dia] = self.arrivals.get(llegada_dia, 0) + cantidad_dec """
        if cantidad_dec <= 0:
            return
        d = dia + demora_dias  # llega al INICIO del día d
        self.arrivals[d] = self.arrivals.get(d, 0) + cantidad_dec
