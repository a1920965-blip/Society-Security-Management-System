from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.oauth2 import verify_admin

from app import database,models,schemas,utils
from app.exception.custom_exceptions import Content_Not_Found
router=APIRouter()

@router.get('/epass')
async def get_epass(admin=Depends(verify_admin),db:AsyncSession=Depends(database.get_db)):
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
@router.put('/epass/action')
async def update_epasses(ticket_id:int,e_data:schemas.Epass_update,admin=Depends(verify_admin),db:AsyncSession=Depends(database.get_db)):
    epass=await db.get(models.Epass,ticket_id)
    if epass==None:
        raise Content_Not_Found("Invalid Request")
    epass.status=e_data.status
    epass.remark= e_data.remark
    token_obj=None
    if e_data.status.upper()=="APPROVED":  #  guestid function is remaning we can also import it into utils 
        guest_id=epass.guest_name.strip().lower()
        Qr=utils.generate_qr_code(guest_id)
        token_obj=models.Token(user_id=guest_id,token=Qr["data"],token_id=Qr["token_id"])
        db.add(token_obj)
    await db.commit()
    return {"success":True,"message":"epass updated Successfully"}

