from __future__ import annotations

from database.connection import DatabaseError, IntegrityError, get_connection, row_to_dict, rows_to_dicts


class ClienteController:
    def create(self, data: dict) -> int:
        nome = data.get("nome", "").strip()
        if not nome:
            raise ValueError("Informe o nome do cliente.")

        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO clientes
                        (nome, cpf_cnpj, telefone, email, endereco, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nome,
                        data.get("cpf_cnpj", "").strip(),
                        data.get("telefone", "").strip(),
                        data.get("email", "").strip(),
                        data.get("endereco", "").strip(),
                        data.get("observacoes", "").strip(),
                    ),
                )
                return int(cursor.lastrowid)
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao cadastrar cliente: {exc}") from exc

    def update(self, cliente_id: int, data: dict) -> None:
        nome = data.get("nome", "").strip()
        if not nome:
            raise ValueError("Informe o nome do cliente.")

        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    UPDATE clientes
                    SET nome = ?, cpf_cnpj = ?, telefone = ?, email = ?,
                        endereco = ?, observacoes = ?, atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        nome,
                        data.get("cpf_cnpj", "").strip(),
                        data.get("telefone", "").strip(),
                        data.get("email", "").strip(),
                        data.get("endereco", "").strip(),
                        data.get("observacoes", "").strip(),
                        cliente_id,
                    ),
                )
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao atualizar cliente: {exc}") from exc

    def delete(self, cliente_id: int) -> None:
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        except IntegrityError as exc:
            raise ValueError("Nao e possivel excluir cliente vinculado a carros ou ordens.") from exc
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao excluir cliente: {exc}") from exc

    def get(self, cliente_id: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
        return row_to_dict(row)

    def list(self, search: str = "") -> list[dict]:
        search = search.strip()
        query = "SELECT * FROM clientes"
        params: tuple = ()
        if search:
            like = f"%{search}%"
            query += " WHERE nome LIKE ? OR cpf_cnpj LIKE ? OR telefone LIKE ? OR email LIKE ?"
            params = (like, like, like, like)
        query += " ORDER BY nome"
        with get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return rows_to_dicts(rows)
