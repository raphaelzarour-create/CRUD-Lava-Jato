from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class OrdemServicoItem:
    servico_id: int
    quantidade: int
    valor_unitario: float
    subtotal: float
    id: int | None = None


@dataclass(slots=True)
class OrdemServico:
    cliente_id: int
    carro_id: int
    status: str = "Aberta"
    forma_pagamento: str = ""
    observacoes: str = ""
    itens: list[OrdemServicoItem] = field(default_factory=list)
    id: int | None = None

