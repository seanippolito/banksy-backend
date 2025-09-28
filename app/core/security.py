import time
from typing import Any, Dict, Optional
import httpx
from jose import jwt
from jose.utils import base64url_decode
from app.core.config import settings

# Simple JWKS cache
_JWKS_CACHE: dict[str, Any] = {"exp": 0, "jwks": None}
_JWKS_TTL_SECONDS = 600

async def _fetch_jwks() -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(settings.CLERK_JWKS_URL)
        r.raise_for_status()
        return r.json()

async def get_jwks() -> Dict[str, Any]:
    now = time.time()
    if _JWKS_CACHE["jwks"] is None or now >= _JWKS_CACHE["exp"]:
        jwks = await _fetch_jwks()
        _JWKS_CACHE["jwks"] = jwks
        _JWKS_CACHE["exp"] = now + _JWKS_TTL_SECONDS
    return _JWKS_CACHE["jwks"]

def _find_key(jwks: Dict[str, Any], kid: str) -> Optional[Dict[str, Any]]:
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k
    return None

async def verify_jwt(token: str) -> Dict[str, Any]:
    # 1) read header to find kid
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("JWT header missing 'kid'")

    # 2) fetch jwks, find key
    jwks = await get_jwks()
    key = _find_key(jwks, kid)
    if not key:
        raise ValueError("Signing key not found for kid")

    # 3) verify
    options = {"verify_aud": bool(settings.JWT_AUDIENCE)}
    claims = jwt.decode(
        token,
        key,
        algorithms=[key.get("alg", "RS256")],
        audience=settings.JWT_AUDIENCE if settings.JWT_AUDIENCE else None,
        issuer=settings.JWT_ISSUER if settings.JWT_ISSUER else None,
        options=options,
    )
    return claims
