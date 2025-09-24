# cálculo de costos (almac., ruptura, pedido)
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

DECENA = 10

@dataclass
class Tramo:
    min_dec: int
    max_dec: Optional[int]
    costo: float

@dataclass
class CostosCfg:
    c_almacen_uni_dia: float
    c_ruptura_uni_dia: float
    tramos: List[Tramo]

    def costo_pedido(self, cant_dec: int) -> float:
        if cant_dec <= 0:
            return 0.0
        for t in self.tramos:
            if t.max_dec is None:
                if cant_dec >= t.min_dec:
                    return t.costo
            else:
                if t.min_dec <= cant_dec <= t.max_dec:
                    return t.costo
        # fallback
        return 0.0
