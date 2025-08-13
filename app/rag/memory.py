from collections import deque
from typing import Deque, Dict, List, Tuple

# In dev, semplice dict in-memory. In prod, sostituisci con Redis.
_STORE: Dict[str, Deque[Tuple[str,str]]] = {}
WINDOW = 6  # ultime 6 turnazioni (user/assistant)

def _key(tenant_id: str, session_id: str) -> str:
    return f"{tenant_id}:{session_id}"

def append_turn(tenant_id: str, session_id: str, role: str, content: str):
    k = _key(tenant_id, session_id)
    if k not in _STORE:
        _STORE[k] = deque(maxlen=WINDOW*2)  # user+assistant
    _STORE[k].append((role, content))

def get_history(tenant_id: str, session_id: str) -> List[Tuple[str,str]]:
    return list(_STORE.get(_key(tenant_id, session_id), []))

def clear_history(tenant_id: str, session_id: str):
    _STORE.pop(_key(tenant_id, session_id), None)
