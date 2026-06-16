from __future__ import annotations

from datetime import datetime
from typing import Any

from database.connection import DatabaseError, get_connection, row_to_dict, rows_to_dicts


class OrdemController:
    STATUS = ("Aberta", "Em andamento", "Concluida", "Cancelada")

    def _normalize_items(self, conn: Any, itens: list[dict]) -> list[dict]:
        normalized: list[dict] = []
        for item in itens:
            servico_id = int(item.get("servico_id") or 0)
            quantidade = int(item.get("quantidade") or 0)
            if servico_id <= 0 or quantidade <= 0:
                raise ValueError("Informe servico e quantidade validos.")

            servico = conn.execute(
                "SELECT id, nome, preco FROM servicos WHERE id = ?",
                (servico_id,),
            ).fetchone()
            if servico is None:
                raise ValueError("Servico informado nao foi encontrado.")

            valor_unitario = float(item.get("valor_unitario") or servico["preco"])
            subtotal = round(valor_unitario * quantidade, 2)
            normalized.append(
                {
                    "servico_id": servico_id,
                    "servico_nome": servico["nome"],
                    "quantidade": quantidade,
                    "valor_unitario": valor_unitario,
                    "subtotal": subtotal,
                }
            )
        return normalized

    def _validate_header(self, data: dict) -> tuple[int, int, str, str, str]:
        cliente_id = int(data.get("cliente_id") or 0)
        carro_id = int(data.get("carro_id") or 0)
        status = data.get("status", "Aberta").strip() or "Aberta"
        forma_pagamento = data.get("forma_pagamento", "").strip()
        observacoes = data.get("observacoes", "").strip()

        if cliente_id <= 0:
            raise ValueError("Selecione o cliente da ordem.")
        if carro_id <= 0:
            raise ValueError("Selecione o veiculo da ordem.")
        if status not in self.STATUS:
            raise ValueError("Status da ordem invalido.")
        return cliente_id, carro_id, status, forma_pagamento, observacoes

    def create(self, data: dict, itens: list[dict]) -> int:
        cliente_id, carro_id, status, forma_pagamento, observacoes = self._validate_header(data)
        if not itens:
            raise ValueError("Adicione pelo menos um servico na ordem.")

        try:
            with get_connection() as conn:
                normalized_items = self._normalize_items(conn, itens)
                total = round(sum(item["subtotal"] for item in normalized_items), 2)
                data_finalizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Concluida" else None

                cursor = conn.execute(
                    """
                    INSERT INTO ordens_servico
                        (cliente_id, carro_id, status, valor_total, forma_pagamento,
                         observacoes, data_finalizacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cliente_id,
                        carro_id,
                        status,
                        total,
                        forma_pagamento,
                        observacoes,
                        data_finalizacao,
                    ),
                )
                ordem_id = int(cursor.lastrowid)
                self._insert_items(conn, ordem_id, normalized_items)
                return ordem_id
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao cadastrar ordem de servico: {exc}") from exc

    def update(self, ordem_id: int, data: dict, itens: list[dict]) -> None:
        cliente_id, carro_id, status, forma_pagamento, observacoes = self._validate_header(data)
        if not itens:
            raise ValueError("Adicione pelo menos um servico na ordem.")

        try:
            with get_connection() as conn:
                normalized_items = self._normalize_items(conn, itens)
                total = round(sum(item["subtotal"] for item in normalized_items), 2)
                data_finalizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Concluida" else None

                conn.execute(
                    """
                    UPDATE ordens_servico
                    SET cliente_id = ?, carro_id = ?, status = ?, valor_total = ?,
                        forma_pagamento = ?, observacoes = ?, data_finalizacao = ?
                    WHERE id = ?
                    """,
                    (
                        cliente_id,
                        carro_id,
                        status,
                        total,
                        forma_pagamento,
                        observacoes,
                        data_finalizacao,
                        ordem_id,
                    ),
                )
                conn.execute("DELETE FROM ordem_servico_itens WHERE ordem_id = ?", (ordem_id,))
                self._insert_items(conn, ordem_id, normalized_items)
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao atualizar ordem de servico: {exc}") from exc

    def _insert_items(self, conn: Any, ordem_id: int, itens: list[dict]) -> None:
        conn.executemany(
            """
            INSERT INTO ordem_servico_itens
                (ordem_id, servico_id, quantidade, valor_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    ordem_id,
                    item["servico_id"],
                    item["quantidade"],
                    item["valor_unitario"],
                    item["subtotal"],
                )
                for item in itens
            ],
        )

    def delete(self, ordem_id: int) -> None:
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM ordens_servico WHERE id = ?", (ordem_id,))
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao excluir ordem de servico: {exc}") from exc

    def list(self, search: str = "") -> list[dict]:
        search = search.strip()
        filters: dict = {"cliente": search, "placa": search} if search else {}
        return self.search(filters)

    def search(self, filters: dict | None = None) -> list[dict]:
        filters = filters or {}
        query = """
            SELECT
                ordens_servico.id,
                ordens_servico.data_abertura,
                ordens_servico.data_finalizacao,
                ordens_servico.status,
                ordens_servico.valor_total,
                ordens_servico.forma_pagamento,
                clientes.nome AS cliente_nome,
                carros.marca,
                carros.modelo,
                carros.placa,
                CONCAT(carros.marca, ' ', carros.modelo) AS carro_nome
            FROM ordens_servico
            JOIN clientes ON clientes.id = ordens_servico.cliente_id
            JOIN carros ON carros.id = ordens_servico.carro_id
        """
        clauses: list[str] = []
        params: list = []

        cliente = filters.get("cliente", "").strip()
        placa = filters.get("placa", "").strip()
        status = filters.get("status", "").strip()
        data_inicio = filters.get("data_inicio", "").strip()
        data_fim = filters.get("data_fim", "").strip()

        if cliente:
            clauses.append("clientes.nome LIKE ?")
            params.append(f"%{cliente}%")
        if placa:
            clauses.append("carros.placa LIKE ?")
            params.append(f"%{placa.upper()}%")
        if status:
            clauses.append("ordens_servico.status = ?")
            params.append(status)
        if data_inicio:
            clauses.append("date(ordens_servico.data_abertura) >= date(?)")
            params.append(data_inicio)
        if data_fim:
            clauses.append("date(ordens_servico.data_abertura) <= date(?)")
            params.append(data_fim)

        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY ordens_servico.id DESC"

        with get_connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return rows_to_dicts(rows)

    def get(self, ordem_id: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    ordens_servico.*,
                    clientes.nome AS cliente_nome,
                    carros.placa,
                    carros.marca,
                    carros.modelo,
                    CONCAT(carros.marca, ' ', carros.modelo) AS carro_nome
                FROM ordens_servico
                JOIN clientes ON clientes.id = ordens_servico.cliente_id
                JOIN carros ON carros.id = ordens_servico.carro_id
                WHERE ordens_servico.id = ?
                """,
                (ordem_id,),
            ).fetchone()
        return row_to_dict(row)

    def get_with_items(self, ordem_id: int) -> dict | None:
        with get_connection() as conn:
            ordem_row = conn.execute(
                """
                SELECT
                    ordens_servico.*,
                    clientes.nome AS cliente_nome,
                    carros.placa,
                    carros.marca,
                    carros.modelo,
                    CONCAT(carros.marca, ' ', carros.modelo) AS carro_nome
                FROM ordens_servico
                JOIN clientes ON clientes.id = ordens_servico.cliente_id
                JOIN carros ON carros.id = ordens_servico.carro_id
                WHERE ordens_servico.id = ?
                """,
                (ordem_id,),
            ).fetchone()
            if ordem_row is None:
                return None
            item_rows = conn.execute(
                """
                SELECT
                    ordem_servico_itens.*,
                    servicos.nome AS servico_nome
                FROM ordem_servico_itens
                JOIN servicos ON servicos.id = ordem_servico_itens.servico_id
                WHERE ordem_servico_itens.ordem_id = ?
                ORDER BY ordem_servico_itens.id
                """,
                (ordem_id,),
            ).fetchall()

        ordem = dict(ordem_row)
        ordem["itens"] = rows_to_dicts(item_rows)
        return ordem

    def dashboard_metrics(self) -> dict:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM clientes) AS total_clientes,
                    (SELECT COUNT(*) FROM carros) AS total_carros,
                    (SELECT COUNT(*) FROM ordens_servico WHERE status IN ('Aberta', 'Em andamento')) AS ordens_abertas,
                    (SELECT COUNT(*) FROM ordens_servico WHERE status = 'Concluida') AS ordens_concluidas,
                    (SELECT COALESCE(SUM(valor_total), 0) FROM ordens_servico WHERE status = 'Concluida') AS faturamento_total
                """
            ).fetchone()
        return row_to_dict(row) or {
            "total_clientes": 0,
            "total_carros": 0,
            "ordens_abertas": 0,
            "ordens_concluidas": 0,
            "faturamento_total": 0,
        }
