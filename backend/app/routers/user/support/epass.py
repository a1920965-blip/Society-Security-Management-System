from fastapi import APIRouter,status,HTTPException,Request,Depends
from app import schemas,utils,database,models
from app.exception.custom_exceptions import Content_Not_Found,Not_Authorized,Bad_Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.oauth2 import verify_user
from sqlalchemy import and_
from sqlalchemy import select
router=APIRouter(prefix="/epass")

@router.post('/')
async def Epass_post(user_data:schemas.Epass_post,user_id=Depends(verify_user),db:AsyncSession=Depends(database.get_db)):
    obj=models.Epass(user_id=user_id,vehicle_no=user_data.vehicle_no,
                    contact=user_data.contact,guest_name=user_data.guest_name,
                    purpose=user_data.purpose,arrival=user_data.arrival,
                    departure=user_data.departure)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return {"success":True,"message":"Request Submited","ticket_id":obj.ticket_id}
@router.get('/')
async def Epass_get(ticket_id:int,user_id=Depends(verify_user), db: AsyncSession = Depends(database.get_db)):
    result= await db.execute(select(models.Epass).where(and_(models.Epass.ticket_id == ticket_id,models.Epass.user_id==user_id)))
    e=result.scalars().first()
    print(user_id)
    if not e:
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