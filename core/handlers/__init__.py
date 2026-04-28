from aiogram import Router

from .general_handler import router as general_router
from .marry_handler import router as marry_router
from .voices_handler import router as voices_router
from .reactions_handler import router as reactions_router
from .games_handler import router as games_router


def setup() -> Router:
    router = Router()
    router.include_router(general_router)
    router.include_router(marry_router)
    router.include_router(games_router)
    router.include_router(reactions_router)
    router.include_router(voices_router)
    return router
