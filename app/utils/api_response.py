from functools import wraps

from fastapi import HTTPException

from core.logs import logger


def api_response(
    success_message: str = "Success",
    error_message: str = "An unexpected error occurred",
):
    """Standardize API responses and handle unexpected exceptions."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info("%s started", func.__name__)

            try:
                result = await func(*args, **kwargs)

                return {
                    "status": "success",
                    "message": success_message,
                    "data": result,
                }

            except HTTPException:
                logger.warning("%s raised an HTTPException", func.__name__)
                raise

            except Exception as e:
                logger.exception("%s failed unexpectedly", func.__name__ , e)

                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": e,
                        "message": error_message,
                    },
                )

        return wrapper

    return decorator