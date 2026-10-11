import base64
from uuid import UUID

def encode_cursor(unique_id: UUID) -> str:
    cursor = base64.urlsafe_b64encode(unique_id.bytes).decode('utf-8')
    return cursor

def decode_cursor(cursor: str) -> UUID:
    try:
        unique_id = UUID(bytes=base64.urlsafe_b64decode(cursor.encode('utf-8')))
        return unique_id

    except Exception:
        raise ValueError