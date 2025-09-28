from typing import Annotated, Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status, Header, Request
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_jwt
from app.db.session import get_db
from app.db.models import User

# Existing strict auth
auth_scheme = HTTPBearer(auto_error=False)

async def get_bearer_token(authorization: Annotated[Optional[str], Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return authorization.split(" ", 1)[1].strip()

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(get_bearer_token),
) -> User:
    try:
        claims = await verify_jwt(token)
    except Exception as e:
        print("[auth] JWT error:", repr(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Clerk standard claims
    clerk_user_id = claims.get("sub")
    primary_email = claims.get("primary_email") or (claims.get("email_addresses") or [None])[0]
    first_name = claims.get("first_name")
    last_name = claims.get("last_name")

    if not clerk_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token (no sub)")

    # Upsert by clerk_user_id
    result = await db.execute(select(User).where(User.clerk_user_id == clerk_user_id))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            clerk_user_id=clerk_user_id,
            email=primary_email,
            first_name=first_name,
            last_name=last_name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"[users] created id={user.id} clerk_user_id={user.clerk_user_id}")
    else:
        # keep data fresh (no-op if unchanged)
        changed = False
        if primary_email and primary_email != user.email:
            user.email = primary_email; changed = True
        if first_name and first_name != user.first_name:
            user.first_name = first_name; changed = True
        if last_name and last_name != user.last_name:
            user.last_name = last_name; changed = True
        if changed:
            await db.commit()
            await db.refresh(user)
            print(f"[users] updated id={user.id}")

    return user

# ✅ New optional auth
async def get_current_user_optional(
        creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
        db: AsyncSession = Depends(get_db),
) -> User | None:
    """Return a User if valid auth provided, else None."""
    if not creds:
        return None

    try:
        payload = jwt.decode(
            creds.credentials,
            settings.clerk_jwks_public_key,
            algorithms=["RS256"],
            issuer=settings.JWT_ISSUER,
        )
        clerk_user_id = payload["sub"]
    except JWTError:
        return None

    user = await db.get(User, {"clerk_user_id": clerk_user_id})
    return user
