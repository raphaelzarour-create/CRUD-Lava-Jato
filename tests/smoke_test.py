from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controllers.auth_controller import AuthController
from controllers.carro_controller import CarroController
from controllers.cliente_controller import ClienteController
from controllers.ordem_controller import OrdemController
from controllers.servico_controller import ServicoController
from database.connection import DB_PATH, initialize_database


def main() -> int:
    if not DB_PATH.exists():
        initialize_database()
    AuthController().ensure_default_admin()

    auth = AuthController()
    cliente_controller = ClienteController()
    carro_controller = CarroController()
    servico_controller = ServicoController()
    ordem_controller = OrdemController()

    assert auth.authenticate("admin", "admin123"), "login padrao falhou"
    metrics = ordem_controller.dashboard_metrics()
    assert "total_clientes" in metrics, "dashboard invalido"

    cliente_id = carro_id = servico_id = ordem_id = None
    try:
        cliente_id = cliente_controller.create(
            {
                "nome": "Smoke Test Cliente",
                "cpf_cnpj": "000.000.000-00",
                "telefone": "(65) 99999-0000",
                "email": "smoke@test.local",
                "endereco": "Rua Teste, 1",
                "observacoes": "Registro temporario.",
            }
        )
        cliente_controller.update(cliente_id, {"nome": "Smoke Test Cliente Editado"})
        assert cliente_controller.get(cliente_id)["nome"] == "Smoke Test Cliente Editado"

        carro_id = carro_controller.create(
            {
                "cliente_id": cliente_id,
                "marca": "Teste",
                "modelo": "Modelo",
                "ano": 2026,
                "placa": "TST0A00",
                "cor": "Azul",
                "tipo": "Carro",
                "observacoes": "",
            }
        )
        assert carro_controller.get(carro_id)["placa"] == "TST0A00"

        servico_id = servico_controller.create(
            {
                "nome": "Smoke Test Lavagem",
                "descricao": "Servico temporario.",
                "preco": 50.0,
                "tempo_estimado_minutos": 30,
                "ativo": True,
            }
        )
        assert servico_controller.get(servico_id)["preco"] == 50.0

        ordem_id = ordem_controller.create(
            {
                "cliente_id": cliente_id,
                "carro_id": carro_id,
                "status": "Aberta",
                "forma_pagamento": "Pix",
                "observacoes": "Smoke test",
            },
            [{"servico_id": servico_id, "quantidade": 2}],
        )
        ordem = ordem_controller.get_with_items(ordem_id)
        assert ordem and ordem["valor_total"] == 100.0
        assert len(ordem["itens"]) == 1
    finally:
        if ordem_id:
            ordem_controller.delete(ordem_id)
        if carro_id:
            carro_controller.delete(carro_id)
        if servico_id:
            servico_controller.delete(servico_id)
        if cliente_id:
            cliente_controller.delete(cliente_id)

    print("Smoke test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

