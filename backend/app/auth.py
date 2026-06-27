"""Keycloak-tokenvalidatie (OIDC). Valideert handtekening + issuer + rol.

- JWKS wordt intern bij Keycloak opgehaald (KEYCLOAK_INTERNAL_ISSUER) zodat de
  backend niet via het publieke TLS-endpoint hoeft.
- De `iss`-claim wordt gecheckt tegen de PUBLIEKE issuer (KEYCLOAK_ISSUER).
- AUTH_DISABLED=1 zet auth uit (enkel voor lokale dev).
"""
import os
import time

import httpx
from fastapi import HTTPException, Request
from jose import jwt

ISSUER = os.environ.get("KEYCLOAK_ISSUER", "").rstrip("/")
INTERNAL_ISSUER = os.environ.get("KEYCLOAK_INTERNAL_ISSUER", ISSUER).rstrip("/")
ADMIN_ROLE = os.environ.get("KEYCLOAK_ADMIN_ROLE", "beheerder")
AUTH_DISABLED = os.environ.get("AUTH_DISABLED", "0") == "1"

_jwks = {"keys": [], "ts": 0.0}


def _get_jwks(force=False):
    now = time.time()
    if force or not _jwks["keys"] or now - _jwks["ts"] > 3600:
        url = f"{INTERNAL_ISSUER}/protocol/openid-connect/certs"
        resp = httpx.get(url, timeout=5)
        resp.raise_for_status()
        _jwks["keys"] = resp.json()["keys"]
        _jwks["ts"] = now
    return _jwks["keys"]


def _find_key(kid):
    key = next((k for k in _get_jwks() if k["kid"] == kid), None)
    if key is None:  # sleutel kan geroteerd zijn -> ververs één keer
        key = next((k for k in _get_jwks(force=True) if k["kid"] == kid), None)
    return key


def require_admin(request: Request):
    if AUTH_DISABLED:
        return {"sub": "dev", "preferred_username": "dev"}

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="geen token")
    token = auth[7:]

    try:
        header = jwt.get_unverified_header(token)
        key = _find_key(header.get("kid"))
        if key is None:
            raise HTTPException(status_code=401, detail="onbekende sleutel")
        claims = jwt.decode(
            token,
            key,
            algorithms=[header.get("alg", "RS256")],
            issuer=ISSUER,
            options={"verify_aud": False},
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=401, detail=f"ongeldig token: {exc}")

    roles = (claims.get("realm_access") or {}).get("roles", [])
    if ADMIN_ROLE not in roles:
        raise HTTPException(status_code=403, detail="geen beheerdersrol")
    return claims
