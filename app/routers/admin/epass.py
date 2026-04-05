import logging
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.oauth2 import verify_admin
from app.dependency import SessionDp
from app import database,models,schemas,utils
from app.exception.custom_exceptions import Content_Not_Found

logger = logging.getLogger(__name__)

router=APIRouter()

@router.get('/epass')
async def get_epass(db:SessionDp,admin=Depends(verify_admin)):
    try:
        result=await db.execute(select(models.Epass))
        epasses=result.scalars().all()
        return {"success":True,"data":{"epasses":[{"ticket_id": e.ticket_id,
                                        "guest_name": e.guest_name,
                                        "purpose": e.purpose,
                                        "arrival": e.arrival,
                                        "departure": e.departure,
                                        "contact": e.contact,
                                        "vehicle_no": e.vehicle_no,
                                        "status": e.status,
                                        "remark": e.remark} for e in epasses] if epasses else None
                                        }}
    except Exception as error:
        logger.error(f"Database error during fetching epasses: {str(error)}")
        await db.rollback()
        raise HTTPException(status_code=500,detail="database Error occur")

@router.put('/epass/action')
async def update_epasses(ticket_id:int,e_data:schemas.Epass_update,db:SessionDp,admin=Depends(verify_admin)):
    try:
        epass=await db.get(models.Epass,ticket_id)
        if epass==None:
            raise Content_Not_Found("Invalid Request")
        epass.status=e_data.status
        epass.remark= e_data.remark
        token_obj=None
        if e_data.status.upper()=="APPROVED": 
            guest_id=epass.guest_name.strip().lower()
            Qr=utils.generate_qr_code(guest_id)
            token_obj=models.Token(user_id=guest_id,token=Qr["data"],token_id=Qr["token_id"])
            db.add(token_obj)
        await db.commit()
        return {"success":True,"message":"epass updated Successfully"}
    except Content_Not_Found:
        raise
    except Exception as error:
        await db.rollback()
        logger.error(f"Database error during updating epass {ticket_id}: {str(error)}")
        raise HTTPException(status_code=500,detail="database Error occur")


