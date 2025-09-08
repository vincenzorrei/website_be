from fastapi import Depends, HTTPException, Header
from ..core.settings import settings

#def require_token(authorization: str | None = Header(default=None)):
#    if not settings.API_TOKEN:
#        return None
#    if authorization != f"Bearer {settings.API_TOKEN}":
#        raise HTTPException(status_code=401, detail="Unauthorized")
#    return True

def require_token(authorization: str | None = Header(default=None)):
    if not settings.API_TOKEN:
        return None  # Nessun token richiesto
    # resto del codice...