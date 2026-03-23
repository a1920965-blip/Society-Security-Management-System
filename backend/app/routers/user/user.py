from fastapi import APIRouter
from . import profile
from .support import support
router=APIRouter(prefix="/user",tags=["User"])

router.include_router(profile.router)
router.include_router(support.router,tags=["User Support"])



