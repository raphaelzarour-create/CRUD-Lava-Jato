from __future__ import annotations

from database.connection import DatabaseError, IntegrityError, get_connection, row_to_dict, rows_to_dicts


class ServicoController:
    def create(self, data: dict) -> int:
        nome = data.get("nome", "").strip()
        preco = float(data.get("preco") or 0)
        if not nome:
            raise ValueError("Informe o nome do servico.")
        if preco <= 0:
            raise ValueError("Informe um preco valido para o servico.")

        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO servicos
                        (nome, descricao, preco, tempo_estimado_minutos, ativo)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        nome,
                        data.get("descricao", "").strip(),
                        preco,
                        int(data.get("tempo_estimado_minutos") or 0),
                        1 if data.get("ativo", True) else 0,
                    ),
                )
                return int(cursor.lastrowid)
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao cadastrar servico: {exc}") from exc

    def update(self, servico_id: int, data: dict) -> None:
        nome = data.get("nome", "").strip()
        preco = float(data.get("preco") or 0)
        if not nome:
            raise ValueError("Informe o nome do servico.")
        if preco <= 0:
            raise ValueError("Informe um preco valido para o servico.")

        try:
            with get_connection() as conn:
                conn.execute(
                    """
                    UPDATE servicos
                    SET nome = ?, descricao = ?, preco = ?, tempo_estimado_minutos = ?,
                        ativo = ?, atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        nome,
                        data.get("descricao", "").strip(),
                        preco,
                        int(data.get("tempo_estimado_minutos") or 0),
                        1 if data.get("ativo", True) else 0,
                        servico_id,
                    ),
                )
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao atualizar servico: {exc}") from exc

    def delete(self, servico_id: int) -> None:
        try:
            with get_connection() as conn:
                conn.execute("DELETE FROM servicos WHERE id = ?", (servico_id,))
        except IntegrityError as exc:
            raise ValueError("Nao e possivel excluir servico vinculado a ordens.") from exc
        except DatabaseError as exc:
            raise RuntimeError(f"Erro ao excluir servico: {exc}") from exc

    def get(self, servico_id: int) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,)).fetchone()
        return row_to_dict(row)

    def list(self, search: str = "", only_active: bool = False) -> list[dict]:
        search = search.strip()
        query = "SELECT * FROM servicos"
        clauses = []
        params: list = []
        if only_active:
            clauses.append("ativo = 1")
        if search:
            like = f"%{search}%"
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            params.extend([like, like])
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY nome"
        with get_connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return rows_to_dicts(rows)
