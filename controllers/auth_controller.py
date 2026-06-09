from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3

from database.connection import get_connection, row_to_dict


class AuthController:
    ITERATIONS = 180_000

    @staticmethod
    def hash_password(password: str, salt: bytes | None = None) -> str:
        if salt is None:
            salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            AuthController.ITERATIONS,
        )
        return f"pbkdf2_sha256${AuthController.ITERATIONS}${salt.hex()}${digest.hex()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        try:
            algorithm, iterations_text, salt_hex, digest_hex = stored_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            salt = bytes.fromhex(salt_hex)
            iterations = int(iterations_text)
            candidate = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations,
            ).hex()
            return hmac.compare_digest(candidate, digest_hex)
        except (ValueError, TypeError):
            return False

    def authenticate(self, usuario: str, senha: str) -> dict | None:
        usuario = usuario.strip()
        if not usuario or not senha:
            return None

        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM usuarios WHERE usuario = ?",
                (usuario,),
            ).fetchone()

        user = row_to_dict(row)
        if not user or not self.verify_password(senha, user["senha_hash"]):
            return None

        user.pop("senha_hash", None)
        return user

    def create_user(self, nome: str, usuario: str, senha: str, perfil: str = "Administrador") -> int:
        senha_hash = self.hash_password(senha)
        try:
            with get_connection() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO usuarios (nome, usuario, senha_hash, perfil)
                    VALUES (?, ?, ?, ?)
                    """,
                    (nome.strip(), usuario.strip(), senha_hash, perfil.strip()),
                )
                return int(cursor.lastrowid)
        except sqlite3.IntegrityError as exc:
            raise ValueError("Ja existe um usuario com esse login.") from exc
        except sqlite3.Error as exc:
            raise RuntimeError(f"Erro ao criar usuario: {exc}") from exc

    def ensure_default_admin(self) -> None:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM usuarios WHERE usuario = ?",
                ("admin",),
            ).fetchone()

        if row is None:
            self.create_user("Administrador", "admin", "admin123", "Administrador")

