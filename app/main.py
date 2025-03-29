from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.api.main import api_router
from app.core.config import settings
from app.core.logging_config import logger
from app.models.generic import DetailItem

app = FastAPI(debug=True)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(
        f"HTTP {exc.status_code} - {exc.detail} - Path: {request.url.path}",
        # exc_info=True,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": DetailItem(
                type="unexpected_error",
                loc=[],
                msg="An unexpected error occurred. Please try again later.",
            ).model_dump(),
        },
    )
