from cryptography.fernet import Fernet
import os


KEY_FILE = "secret.key"


def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        k = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(k)
        # Permisos (sólo lectura/escritura para el propietario)
            try:
                os.chmod(KEY_FILE, 0o600)
            except Exception:
                pass
            return k


KEY = load_or_create_key()
fernet = Fernet(KEY)


def encrypt_text(plain: str) -> bytes:
    return fernet.encrypt(plain.encode("utf-8"))


def decrypt_text(token: bytes) -> str:
    return fernet.decrypt(token).decode("utf-8")
