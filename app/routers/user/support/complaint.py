from fastapi import APIRouter,status,HTTPException,Request,Depends,UploadFile,File,Form
from app import schemas,utils,database,models
from sqlalchemy.ext.asyncio import AsyncSession
from app.oauth2 import verify_user
from app.exception.custom_exceptions import Content_Not_Found,Bad_Request,Not_Authorized
from sqlalchemy import and_
from sqlalchemy import select
import aiofiles
router=APIRouter(prefix='/complaint')

@router.post('/')
async def complaint_post(user_data:schemas.Complaint_post,db: AsyncSession = Depends(database.get_db),user = Depends(verify_user)):
    # if has_attachment and attachment:
    #     file_path = f"uploads/{attachment.filename}"
    #     async with aiofiles.open(file_path, "wb") as f:
    #         while chunk := await attachment.read(1024):
    #             await f.write(chunk)
    obj = models.Complaint(user_id=user,category=user_data.category,description=user_data.description,subject=user_data.subject)
    if user_data.has_attachment and user_data.attachment:
        obj.attachment=user_data.attachment
    db.add(obj)
    await db.commit()
    db.refresh(obj) 
    return {"success": True, "message": "Complaint submitted successfully!","ticket_id": obj.ticket_id} 

@router.get('/')
async def complaint_status(ticket_id:int,user_id=Depends(verify_user), db: AsyncSession = Depends(database.get_db)):
    result= await db.execute(select(models.Complaint).where(and_(models.Complaint.ticket_id == ticket_id,models.Complaint.user_id==user_id)))
    c=result.scalars().first()
    if c is None:
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