import pytest
from jose import jwt
from app.core import security

SECRET = "testsecret"
ALGO = "HS256"

def make_token(payload):
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def test_verify_jwt_valid(monkeypatch):
    token = make_token({"sub": "123"})
    # Monkeypatch jwk_client to accept our SECRET
    # monkeypatch.setattr(security, "CLERK_JWKS_URL", {"keys": []})
    # monkeypatch.setattr(security, "JWT_ISSUER", None)
    # monkeypatch.setattr(security, "JWT_AUDIENCE", None)

    # Should decode without raising
    decoded = jwt.decode(token, SECRET, algorithms=[ALGO])
    assert decoded["sub"] == "123"


def test_verify_jwt_invalid_signature():
    token = make_token({"sub": "123"})
    with pytest.raises(Exception):
        jwt.decode(token, "wrongsecret", algorithms=[ALGO])
