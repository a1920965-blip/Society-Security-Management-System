from fastapi import APIRouter,status,HTTPException,Request,Depends
from app import schemas,utils,database,models
from app.exception.custom_exceptions import Content_Not_Found,Bad_Request,Not_Authorized
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from app.oauth2 import verify_user
from sqlalchemy import select
from app import api_services 
from sqlalchemy.orm import selectinload

router=APIRouter()
@router.get('/weather')
async def get_weather(user_id=Depends(verify_user),db:AsyncSession=Depends(database.get_db)):
    result=await db.execute(select(models.Resident).where(models.Resident.owner==user_id))
    user=result.scalars().first()
    city=None
    if user==None or user.city==None:
        city="Delhi"
    else:
        city=user.city
    data=api_services.weather_api(city)
    return {"success":True,"data":data}
#home page of user 

@router.get('/notice')
async def user_notice(user_id=Depends(verify_user),db:AsyncSession=Depends(database.get_db)):
    result = await db.execute(select(models.Notices).where(or_(models.Notices.user == user_id, models.Notices.user == "*")))
    notices=result.scalars().all() 
    data=[{"Type":n.Type,"Body":n.body} for n in notices] if notices else None
    return {"success":True,"data":data}

@router.get('/profile/')
async def user_profile(
    db: AsyncSession = Depends(database.get_db),
    user_id=Depends(verify_user)
):
    result = await db.execute(
        select(models.Auth)
        .options(
            selectinload(models.Auth.personal),
            selectinload(models.Auth.resident),
            selectinload(models.Auth.vehicle)
        )
        .where(models.Auth.user_id == user_id)
    )

    auth_user = result.scalars().first()

    if not auth_user:
        raise Content_Not_Found("User not found")

    personal = auth_user.personal[0] if auth_user.personal else None
    resident = auth_user.resident[0] if auth_user.resident else None
    vehicles = auth_user.vehicle

    token_result = await db.execute(
        select(models.Token).where(models.Token.user_id == auth_user.user_id)
    )
    user_qrcode = token_result.scalars().first()

    return {
        "success": True,
        "data": {
            "qr_data": user_qrcode.token if user_qrcode else None,
            "user_id": auth_user.user_id,
            "name": auth_user.name,
            "email": auth_user.email,
            "contact": personal.contact if personal else None,
            "department": personal.department if personal else None,
            "designation": personal.designation if personal else None,
            "timestamp": personal.timestamp.isoformat() if personal else None,
            "house_no": resident.house_no if resident else None,
            "block": resident.block if resident else None,
            "city": resident.city if resident else None,
            "state": resident.state if resident else None,
            "pincode": resident.pincode if resident else None,
            "vehicles": [{"number": v.number} for v in vehicles]
        }
    }
@router.put('/personal/')
async def update_personal(user_data:schemas.Personal,user_id=Depends(verify_user),db:AsyncSession=Depends(database.get_db)):
    user=await db.get(models.Personal,user_id)
    user.contact=str(user_data.contact)
    user.designation=user_data.designation
    user.department=user_data.department
    await db.commit()
    return {"success":True,"message":"Details Updates succesfully"}

@router.put('/resident/')
async def update_resident(user_data:schemas.Resident,user_id=Depends(verify_user),db:AsyncSession=Depends(database.get_db)):
    
    user=await db.get(models.Resident,user_id)
    if user is None:
        obj=models.Resident(owner=user_id,house_no=user_data.house_no,block=user_data.block,city=user_data.city,state=user_data.state,pincode=user_data.pincode)
        db.add(obj)
    else:
        user.house_no=user_data.house_no
        user.block=user_data.block
        user.city=user_data.city
        user.state=user_data.state
        user.pincode=user_data.pincode
    await db.commit()
    return {"success":True,"message":"Details Updates succesfully"}

@router.post('/vehicle/add/')
async def add_vehicle(user_data:schemas.Add_vehicle,user_id=Depends(verify_user),db:AsyncSession=Depends(database.get_db)):
    obj=models.Vehicle(owner=user_id,number=user_data.number)
    db.add(obj)
    await db.commit()
    return {"success":True,"message":"vehicle added succesfully"}
@router.delete('/vehicle/remove/')
async def delete_vehicle(user_data:schemas.Delete_vehicle,user_id=Depends(verify_user),db:AsyncSession=Depends(database.get_db)):
    obj=await db.get(models.Vehicle,(user_id,user_data.number))
    if obj==None:
        raise Content_Not_Found(f"Vehicle does not exit of number: {user_data.number}")
    db.delete(obj)
    await db.commit()
    return {"success":True,"message":"vehicle delete  succesfully"}


