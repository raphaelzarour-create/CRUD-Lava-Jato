from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controllers.auth_controller import AuthController
from database.connection import DB_PATH, initialize_database, get_connection


def reset_database() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    initialize_database()


def seed() -> None:
    reset_database()
    auth = AuthController()
    auth.ensure_default_admin()

    with get_connection() as conn:
        clientes = [
            ("Joao Pereira", "123.456.789-00", "(65) 99999-1001", "joao@email.com", "Rua das Flores, 120", "Cliente mensalista."),
            ("Maria Souza", "987.654.321-00", "(65) 99999-2002", "maria@email.com", "Av. Brasil, 450", "Prefere lavagem completa."),
            ("Auto Pecas Centro", "12.345.678/0001-99", "(65) 3322-7788", "contato@autopecas.com", "Centro Comercial, loja 8", "Cliente PJ."),
        ]
        conn.executemany(
            """
            INSERT INTO clientes (nome, cpf_cnpj, telefone, email, endereco, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            clientes,
        )

        carros = [
            (1, "Toyota", "Corolla", 2021, "ABC1D23", "Prata", "Sedan", "Interior claro."),
            (1, "Honda", "CG 160", 2022, "MOT2A22", "Vermelha", "Moto", ""),
            (2, "Jeep", "Renegade", 2020, "JKL4M56", "Branco", "SUV", ""),
            (3, "Fiat", "Strada", 2019, "PJL8T90", "Preto", "Pickup", "Uso comercial."),
        ]
        conn.executemany(
            """
            INSERT INTO carros
                (cliente_id, marca, modelo, ano, placa, cor, tipo, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            carros,
        )

        servicos = [
            ("Lavagem simples", "Lavagem externa com secagem manual.", 35.00, 35, 1),
            ("Lavagem completa", "Lavagem externa, aspiracao e painel.", 65.00, 70, 1),
            ("Higienizacao interna", "Limpeza detalhada de bancos, carpete e teto.", 180.00, 180, 1),
            ("Polimento", "Polimento tecnico de pintura.", 250.00, 240, 1),
            ("Cera cristalizadora", "Aplicacao de cera de protecao.", 90.00, 90, 1),
        ]
        conn.executemany(
            """
            INSERT INTO servicos
                (nome, descricao, preco, tempo_estimado_minutos, ativo)
            VALUES (?, ?, ?, ?, ?)
            """,
            servicos,
        )

        ordens = [
            (1, 1, "Aberta", 100.00, "Pix", "Retirar ate 17h", None),
            (2, 3, "Concluida", 245.00, "Cartao de credito", "Cliente aprovou adicional.", "2026-06-09 10:40:00"),
        ]
        conn.executemany(
            """
            INSERT INTO ordens_servico
                (cliente_id, carro_id, status, valor_total, forma_pagamento, observacoes, data_finalizacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ordens,
        )

        itens = [
            (1, 1, 1, 35.00, 35.00),
            (1, 2, 1, 65.00, 65.00),
            (2, 2, 1, 65.00, 65.00),
            (2, 3, 1, 180.00, 180.00),
        ]
        conn.executemany(
            """
            INSERT INTO ordem_servico_itens
                (ordem_id, servico_id, quantidade, valor_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
            """,
            itens,
        )

    print(f"Banco criado e populado em: {DB_PATH}")


if __name__ == "__main__":
    seed()
