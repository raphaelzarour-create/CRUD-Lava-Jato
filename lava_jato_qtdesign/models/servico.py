from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Servico:
    nome: str
    preco: float
    descricao: str = ""
    tempo_estimado_minutos: int = 0
    ativo: bool = True
    id: int | None = None

