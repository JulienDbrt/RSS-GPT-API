from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from config import settings # IMPORTE LES SETTINGS !

API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False) # Auto_error à False pour un message plus clair

async def get_api_key(api_key_header_value: str = Security(api_key_header)):
    if not api_key_header_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key in header 'X-API-Key'",
        )
    if not settings.API_KEY or api_key_header_value != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API Key",
        )
    return api_key_header_value
