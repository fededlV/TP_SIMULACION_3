# carga/merge: defaults + archivo + UI
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Tuple
import yaml


class TramoPedido(BaseModel):
    min_decenas: int
    max_decenas: Optional[int] = None
    costo: float


class Costos(BaseModel):
    almacenamiento_por_unidad_por_dia: float = 30.0
    ruptura_por_unidad_por_dia: float = 40.0
    pedido_por_tramo: List[TramoPedido]


class Distribucion(BaseModel):
    valores: List[int]
    probabilidades: List[float]

    @field_validator('probabilidades')
    @classmethod
    def probs_sum_to_one(cls, v):
        s = round(sum(v), 6)
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"Las probabilidades deben sumar 1 (suman {s})")
        return v


class Mostrar(BaseModel):
    i_filas: int = 30
    desde_fila_j: int = 1


class PoliticaA(BaseModel):
    periodo_dias: int = 7
    cantidad_decenas: int = 180


class PoliticaB(BaseModel):
    periodo_dias: int = 10
    ventana_historial_dias: int = 10


class Config(BaseModel):
    semilla: Optional[int] = None
    N_dias: int = 100000
    mostrar: Mostrar = Mostrar()

    stock_inicial_decenas: int = 20
    pedido_primer_dia: bool = True
    politica: str = "A"

    demanda: Distribucion
    demora: Distribucion
    costos: Costos

    politica_A: PoliticaA = PoliticaA()
    politica_B: PoliticaB = PoliticaB()

    @staticmethod
    def from_yaml(path: str) -> "Config":
        with open(path, 'r', encoding='utf-8') as f:
            raw = yaml.safe_load(f)
        # Remap claves demanda/demora → Distribucion
        raw['demanda'] = {
            'valores': raw['demanda']['valores_decenas'],
            'probabilidades': raw['demanda']['probabilidades'],
        }
        raw['demora'] = {
            'valores': raw['demora']['valores_dias'],
            'probabilidades': raw['demora']['probabilidades'],
        }
        return Config(**raw)
