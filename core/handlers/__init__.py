from aiogram import Router

from .general import router as general_router


def setup() -> Router:
    router = Router()
    router.include_router(general_router)
    return router
