from fastapi import APIRouter
from .import epass,complaint,notice,user_view,logs

router=APIRouter(prefix="/admin",tags=["Admin"])

router.include_router(epass.router)
router.include_router(complaint.router)
router.include_router(notice.router)
router.include_router(user_view.router)
router.include_router(logs.router)