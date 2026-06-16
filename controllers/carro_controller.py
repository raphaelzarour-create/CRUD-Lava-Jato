from __future__ import annotations

from database.connection import DatabaseError, IntegrityError, get_connection, row_to_dict, rows_to_dicts


class CarroController:
    def create(self, data: dict) -> int:
        cliente_id = int(data.get("cliente_id") or 0)
        placa = data.get("placa", "").strip().upper()
        if cliente_id <= 0:
            raise ValueError("Selecione o cliente dono do veiculo.")
        if not placa:
            raise ValueError("Informe a placa do veiculo.")

        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO carros
                        (cliente_id, marca, modelo, ano, placa, cor, tipo, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cliente_id,
                        data.get("marca", "").strip(),
                        data.get("modelo", "").strip(),
                        data.get("ano"),
                        placa,
                        data.get("cor", "").strip(),
                        data.get("tipo", "").strip(),
                        data.get("observacoes", "").strip(),
                    ),
                )
                return int(cursor.lastrowid)
        except IntegrityError as exc:
            raise ValueError("Ja existe um veiculo cadastrado com essa placa.") from exc
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao cadastrar veiculo: {exc}") from exc

    def update(self, carro_id: int, data: dict) -> None:
        cliente_id = int(data.get("cliente_id") or 0)
        placa = data.get("placa", "").strip().upper()
        if cliente_id <= 0:
            raise ValueError("Selecione o cliente dono do veiculo.")
        if not placa:
            raise ValueError("Informe a placa do veiculo.")

        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    UPDATE carros
                    SET cliente_id = ?, marca = ?, modelo = ?, ano = ?, placa = ?,
                        cor = ?, tipo = ?, observacoes = ?, atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        cliente_id,
                        data.get("marca", "").strip(),
                        data.get("modelo", "").strip(),
                        data.get("ano"),
                        placa,
                        data.get("cor", "").strip(),
                        data.get("tipo", "").strip(),
                        data.get("observacoes", "").strip(),
                        carro_id,
                    ),
                )
        except IntegrityError as exc:
            raise ValueError("Ja existe um veiculo cadastrado com essa placa.") from exc
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao atualizar veiculo: {exc}") from exc

    def delete(self, carro_id: int) -> None:
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM carros WHERE id = ?", (carro_id,))
        except IntegrityError as exc:
            raise ValueError("Nao e possivel excluir veiculo vinculado a ordens.") from exc
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao excluir veiculo: {exc}") from exc

    def get(self, carro_id: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute(
                """
                SELECT carros.*, clientes.nome AS cliente_nome
                FROM carros
                JOIN clientes ON clientes.id = carros.cliente_id
                WHERE carros.id = ?
                """,
                (carro_id,),
            ).fetchone()
        return row_to_dict(row)

    def list(self, search: str = "") -> list[dict]:
        search = search.strip()
        query = """
            SELECT carros.*, clientes.nome AS cliente_nome
            FROM carros
            JOIN clientes ON clientes.id = carros.cliente_id
        """
        params: tuple = ()
        if search:
            like = f"%{search}%"
            query += """
                WHERE clientes.nome LIKE ? OR carros.placa LIKE ? OR carros.marca LIKE ?
                   OR carros.modelo LIKE ? OR carros.tipo LIKE ?
            """
            params = (like, like, like, like, like)
        query += " ORDER BY clientes.nome, carros.placa"
        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return rows_to_dicts(rows)

    def list_by_cliente(self, cliente_id: int) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM carros
                WHERE cliente_id = ?
                ORDER BY placa
                """,
                (cliente_id,),
            ).fetchall()
        return rows_to_dicts(rows)
