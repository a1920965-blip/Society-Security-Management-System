import logging
from fastapi import APIRouter,status,HTTPException,Request,Depends,UploadFile,File,Form
from app import schemas,utils,database,models
from sqlalchemy.ext.asyncio import AsyncSession
from app.oauth2 import verify_user
from app.exception.custom_exceptions import Content_Not_Found,Bad_Request,Not_Authorized
from sqlalchemy import and_
from app.dependency import SessionDp
from sqlalchemy import select
import aiofiles

logger = logging.getLogger(__name__)

router=APIRouter(prefix='/complaint')

@router.post('/')
async def complaint_post(user_data:schemas.Complaint_post,db:SessionDp,user = Depends(verify_user)):
    try:
        obj = models.Complaint(user_id=user,category=user_data.category,description=user_data.description,subject=user_data.subject)
        if user_data.has_attachment and user_data.attachment:
            obj.attachment=user_data.attachment
        db.add(obj)
        await db.commit()
        db.refresh(obj)
        logger.info(f"Complaint submitted successfully for user {user}: ticket_id {obj.ticket_id}")
        return {"success": True, "message": "Complaint submitted successfully!","ticket_id": obj.ticket_id}
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during complaint submission for user {user}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.get('/')
async def complaint_status(ticket_id:int,db:SessionDp,user_id=Depends(verify_user)):
    try:
        result= await db.execute(select(models.Complaint).where(and_(models.Complaint.ticket_id == ticket_id,models.Complaint.user_id==user_id)))
        c=result.scalars().first()
        if c is None:
            logger.warning(f"Complaint not found or access denied for user {user_id}: ticket_id {ticket_id}")
            raise Content_Not_Found("Complaint not found or you don't have access to it")
        return {
            "success": True, 
            "data": {
                "ticket_id": c.ticket_id,
                "category": c.category,
                "subject": c.subject,
                "description": c.description,
                "status": c.status or "Pending",
                "attachment": c.attachment
            }
        }
    except Content_Not_Found:
        raise
    except Exception as e:
        logger.error(f"Database error during fetching complaint status for user {user_id}: ticket_id {ticket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")