import logging
from fastapi import APIRouter,status,HTTPException,Request,Depends
from app import schemas,utils,database,models
from app.exception.custom_exceptions import Content_Not_Found,Not_Authorized,Bad_Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.oauth2 import verify_user
from sqlalchemy import and_
from sqlalchemy import select
from app.dependency import SessionDp

logger = logging.getLogger(__name__)

router=APIRouter(prefix="/epass")

@router.post('/')
async def Epass_post(user_data:schemas.Epass_post,db:SessionDp,user_id=Depends(verify_user),):
    try:
        obj=models.Epass(user_id=user_id,vehicle_no=user_data.vehicle_no,
                        contact=str(user_data.contact),guest_name=user_data.guest_name,
                        purpose=user_data.purpose,arrival=user_data.arrival,
                        departure=user_data.departure)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        logger.info(f"Epass request submitted successfully for user {user_id}: ticket_id {obj.ticket_id}")
        return {"success":True,"message":"Request Submited","ticket_id":obj.ticket_id}
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during epass submission for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.get('/')
async def Epass_get(ticket_id:int,db:SessionDp,user_id=Depends(verify_user)):
    try:
        result= await db.execute(select(models.Epass).where(and_(models.Epass.ticket_id == ticket_id,models.Epass.user_id==user_id)))
        e=result.scalars().first()
        if not e:
            logger.warning(f"Epass not found or access denied for user {user_id}: ticket_id {ticket_id}")
            raise Content_Not_Found("Invalid Ticket Id")
        data={
                "ticket_id": e.ticket_id,
                "guest_name": e.guest_name,
                "purpose": e.purpose,
                "arrival": e.arrival,
                "departure": e.departure,
                "contact": e.contact,
                "vehicle_no": e.vehicle_no,
                "status": e.status,
                "remark": e.remark
            }
        if e.status.upper()=="APPROVED":
            guest_id=e.guest_name.strip().lower()
            result=await db.execute(select(models.Token).where(models.Token.user_id==guest_id))
            t=result.scalars().first()
            data.update({"qr_data":t.token})
        return {"success": True,"data": data}
    except Content_Not_Found:
        raise
    except Exception as e:
        logger.error(f"Database error during fetching epass for user {user_id}: ticket_id {ticket_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")