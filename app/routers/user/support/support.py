import logging
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import database,models
from .import epass,complaint
from sqlalchemy import select
from app.oauth2 import verify_user
from app.dependency import SessionDp

logger = logging.getLogger(__name__)

router=APIRouter(prefix="/support")

@router.get('/status/')
async def tickets_status(db:SessionDp,user_id=Depends(verify_user)):
    try:
        result_c=await db.execute(select(models.Complaint).where(models.Complaint.user_id==user_id))
        complaint=result_c.scalars().all()
        result_e=await db.execute(select(models.Epass).where(models.Epass.user_id==user_id))
        epasses=result_e.scalars().all()
        logger.info(f"Tickets status fetched successfully for user {user_id}")
        return {"success":True,
                        "data":{
                            "complaints":[{"ticket_id":c.ticket_id,
                                            "subject":c.subject,
                                            "status":c.status,
                                            "remark":c.remark,
                                            "type":"Complaint"} for c in complaint] if complaint else None,
                            "epasses":[{"ticket_id":e.ticket_id,
                                        "status":e.status,
                                        "remark":e.remark,
                                        "type":"E-pass"} for e in epasses] if epasses else None 
        }}
    except Exception as e:
        logger.error(f"Database error during fetching tickets status for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

router.include_router(epass.router)
router.include_router(complaint.router)
