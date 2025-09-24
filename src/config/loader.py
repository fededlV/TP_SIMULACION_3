# carga/merge: defaults + archivo + UI
from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from pathlib import Path
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
    def from_yaml(path: str | None) -> "Config":
        # Path por defecto: <root>/data/ejemplos/config_ejemplo.yaml
        if not path:
            root = Path(__file__).resolve().parents[2]  # .../src/config/ -> subir 2 = root del repo
            path = str(root / "data" / "ejemplos" / "config_ejemplo.yaml")

        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"No existe el archivo de configuración: {p}")

        with p.open('r', encoding='utf-8') as f:
            raw = yaml.safe_load(f)  # requiere PyYAML

        if not isinstance(raw, dict):
            raise ValueError(f"El YAML está vacío o mal formado: {p}")

        # Validaciones explícitas para dar errores claros
        for clave in ("demanda", "demora", "costos"):
            if clave not in raw or raw[clave] is None:
                raise KeyError(f"Falta la sección obligatoria '{clave}' en {p}")

        # Remap claves demanda/demora → Distribucion
        dem = raw["demanda"]
        if "valores_decenas" not in dem or "probabilidades" not in dem:
            raise KeyError("En 'demanda' faltan 'valores_decenas' o 'probabilidades'")

        raw['demanda'] = {
            'valores': dem['valores_decenas'],
            'probabilidades': dem['probabilidades'],
        }

        dm = raw["demora"]
        if "valores_dias" not in dm or "probabilidades" not in dm:
            raise KeyError("En 'demora' faltan 'valores_dias' o 'probabilidades'")

        raw['demora'] = {
            'valores': dm['valores_dias'],
            'probabilidades': dm['probabilidades'],
        }

        return Config(**raw)

