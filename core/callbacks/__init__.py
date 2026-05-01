from aiogram import Router

from .marry import router as marry_router


def setup() -> Router:
    router = Router()
    router.include_router(marry_router)
    return router
