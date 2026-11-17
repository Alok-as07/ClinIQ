import uuid
from pathlib import Path
from cryptography.fernet import Fernet
from api.app.core.config import settings

def get_fernet() -> Fernet:
    
    encryption_key = settings.FILE_ENCRYPTION_KEY
    if not encryption_key:
        raise RuntimeError(
            "FILE_ENCRYPTION_KEY is not configured"
        )

    return Fernet(
        encryption_key.encode("utf-8")
    )
    
def get_storage_directory() -> Path:
    directory = Path(
        settings.UPLOAD_DIR
    ).resolve()
    directory.mkdir(
        parents=True,
        exist_ok=True
    )
    return directory

def save_encrypted_file(
    content: bytes,
    filename: str
) -> str:
    """
    Encrypt and save the original uploaded file.
    The original filename is intentionally not used
    as the physical storage filename.
    """

    if not content:
        raise ValueError("Cannot store an empty file")
    encrypted_content = get_fernet().encrypt(content)
    storage_directory = get_storage_directory()
    file_id = str(uuid.uuid4())
    file_path = storage_directory / f"{file_id}.enc"
    file_path.write_bytes(encrypted_content)
    return str(file_path)

def read_decrypted_file(file_path: str) -> bytes:
    """
    Decrypt a previously stored file.
    The resolved path must remain inside UPLOAD_DIR.
    """
    storage_directory = get_storage_directory()
    requested_path = Path(file_path).resolve()
    try:
        requested_path.relative_to(storage_directory)
    except ValueError:
        raise ValueError("Invalid storage path")
    if not requested_path.is_file():
        raise FileNotFoundError("Stored document not found")
    encrypted_content = requested_path.read_bytes()
    return get_fernet().decrypt(encrypted_content)

def delete_encrypted_file(file_path: str) -> None:
    storage_directory = get_storage_directory()
    requested_path = Path(file_path).resolve()
    try:
        requested_path.relative_to(storage_directory)
    except ValueError:
        raise ValueError("Invalid storage path")
    if requested_path.exists() and requested_path.is_file():
        requested_path.unlink()