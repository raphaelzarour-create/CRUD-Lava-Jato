from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Cliente:
    nome: str
    cpf_cnpj: str = ""
    telefone: str = ""
    email: str = ""
    endereco: str = ""
    observacoes: str = ""
    id: int | None = None

