from __future__ import annotations

import hashlib
import hmac

from database.connection import get_connection, row_to_dict


class AuthController:
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
