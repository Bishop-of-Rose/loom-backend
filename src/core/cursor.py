import json
import base64
from uuid import UUID

def encode_cursor(unique_id: UUID) -> str:
    payload = {'id': str(unique_id)}
    encoded = json.dumps(payload).encode('utf-8')
    cursor = base64.b64encode(encoded).decode('utf-8')
    return cursor

def decode_cursor(cursor: str) -> UUID:
    try:
        decoded = base64.b64decode(cursor.encode('utf-8'))
        payload = json.loads(decoded.decode('utf-8'))
        unique_id = UUID(payload['id'])
        return unique_id

    except Exception:
        raise ValueError('Invalid cursor')


