import logging
from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.oauth2 import verify_admin
from app.dependency import SessionDp
from app.exception.custom_exceptions import Content_Not_Found
from ...import database,models,schemas
from sqlalchemy import select

logger = logging.getLogger(__name__)

router=APIRouter()

@router.get('/complaints/')
async def get_complaints(db:SessionDp,admin=Depends(verify_admin),):
    try:
        result=await db.execute(select(models.Complaint))
        complaints=result.scalars().all()
        return {"success":True,"data":{"complaints":[{"ticket_id":c.ticket_id,
                                "user_id":c.user_id,
                                "category":c.category,
                                "description":c.description,
                                "attachment":c.attachment,
                                "subject":c.subject,
                                "status":c.status,
                                "remark":c.remark} for c in complaints] if complaints else None}}
    except Exception as error:
        logger.error(f"Database error during fetching complaints: {str(error)}")
        raise HTTPException(status_code=500,detail="database Error occur")

                            
@router.put('/complaint/action')
async def update_complaint(ticket_id:int,c_Data:schemas.Complaint_update,db:SessionDp,admin=Depends(verify_admin)):
    try:
        comp=await db.get(models.Complaint,ticket_id)
        if comp==None:
            raise Content_Not_Found("Invalid Request")
        elif comp.status.upper()=="APPROVED":
            raise Content_Not_Found("Already Aprroved")
        elif comp.status.upper()=="PENDING":
            comp.status=c_Data.status
            comp.remark=c_Data.remark
            await db.commit()
            return {"success":True,"message":"Complant updated Successfully"}
        else:
            raise Content_Not_Found("Invalid Request")
    except Content_Not_Found:
        raise
    except Exception as error:
        await db.rollback()
        logger.error(f"Database error during updating complaint {ticket_id}: {str(error)}")
        raise HTTPException(status_code=500,detail="database Error occur")

