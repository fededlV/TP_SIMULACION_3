# Políticas A y B (estrategia de reposición)
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, List


class Policy(Protocol):
    def cantidad_a_pedir(self, dia: int, demandas_ultimos: List[int]) -> int:
        ...


@dataclass
class PolicyA:
    periodo: int
    cantidad_dec: int

    def cantidad_a_pedir(self, dia: int, demandas_ultimos: List[int]) -> int:
        return self.cantidad_dec if dia % self.periodo == 0 else 0


@dataclass
class PolicyB:
    periodo: int
    ventana: int

    def cantidad_a_pedir(self, dia: int, demandas_ultimos: List[int]) -> int:
        if dia % self.periodo != 0:
            return 0
        # suma de demandas de los últimos "ventana" días
        return max(0, sum(demandas_ultimos[-self.ventana:]))
