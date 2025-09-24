# definición del "vector de estado" (dataclass)
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


DECENA = 10


@dataclass
class Row:
    dia: int
    rnd_demanda: float
    demanda_dec: int
    llegadas_dec: int
    stock_ini_dec: int
    ventas_dec: int
    faltantes_dec: int
    stock_fin_dec: int
    
    
    pedido_hoy_dec: int
    rnd_demora: Optional[float]
    demora_dias: Optional[int]
    orden_en_curso: str
    
    
    costo_almacen: float
    costo_ruptura: float
    costo_pedido: float
    
    
    AC_cost_almacen: float
    AC_cost_ruptura: float
    AC_cost_pedido: float
    AC_cost_total: float
    AC_demanda_uni: int
    AC_ventas_uni: int
    AC_faltantes_uni: int
    AC_pedidos: int
    fill_rate: float
    costo_promedio_dia: float
    
    
def as_dict(self) -> Dict[str, Any]:
    return asdict(self)