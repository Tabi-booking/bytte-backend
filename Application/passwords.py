from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt solo acepta como máximo 72 bytes en la contraseña en claro
_BCRYPT_MAX_BYTES = 72


def _plain_for_bcrypt(plain: str) -> str:
    """Normaliza la entrada para bcrypt (límite 72 bytes UTF-8)."""
    b = (plain or "").encode("utf-8")
    if len(b) <= _BCRYPT_MAX_BYTES:
        return plain or ""
    return b[:_BCRYPT_MAX_BYTES].decode("utf-8", errors="ignore")


def hash_password(plain: str) -> str:
    return _pwd.hash(_plain_for_bcrypt(plain))


def verify_password(plain: str, stored: str) -> bool:
    if not stored:
        return False
    s = stored.strip()
    if s.startswith("$2"):
        return _pwd.verify(_plain_for_bcrypt(plain), s)
    return plain == s


def prepare_password_for_store(plain: str) -> str:
    s = (plain or "").strip()
    if not s:
        return s
    if s.startswith("$2"):
        return s
    return hash_password(s)
