from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models import ApplicationLogger
from app.api.deps import get_current_user_optional  # a variant that returns None if no user
import traceback

async def error_logger_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        async with AsyncSessionLocal() as db:  # manual session since we're outside DI
            user = None
            try:
                user = await get_current_user_optional(request)
            except Exception:
                pass

            log = ApplicationLogger(
                user_id=user.id if user else None,
                error_code=getattr(e, "status_code", 500),
                message=tb,
                location=f"{request.method} {request.url.path}",
            )
            db.add(log)
            await db.commit()

        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred. It has been logged."},
        )
