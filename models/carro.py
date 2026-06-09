from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Carro:
    cliente_id: int
    placa: str
    marca: str = ""
    modelo: str = ""
    ano: int | None = None
    cor: str = ""
    tipo: str = ""
    observacoes: str = ""
    id: int | None = None

