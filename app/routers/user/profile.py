import logging
from fastapi import APIRouter,Depends,HTTPException
from app import schemas,database,models
from app.exception.custom_exceptions import Content_Not_Found
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from app.oauth2 import verify_user
from sqlalchemy import select
from app.dependency import SessionDp
from app import api_services 
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

router=APIRouter()

@router.get('/weather')
async def get_weather(db:SessionDp,user_id=Depends(verify_user)):
    try:
        result=await db.execute(select(models.Resident).where(models.Resident.owner==user_id))
        user=result.scalars().first()
        city=None
        if user==None or user.city==None:
            city="Delhi"
        else:
            city=user.city
        data=api_services.weather_api(city)
        return {"success":True,"data":data}
    except Exception as e:
        logger.error(f"Database error during fetching weather for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.get('/notice')
async def user_notice(db:SessionDp,user_id=Depends(verify_user)):
    try:
        result = await db.execute(select(models.Notices).where(or_(models.Notices.user == user_id, models.Notices.user == "*")))
        notices=result.scalars().all() 
        data=[{"Type":n.Type,"Body":n.body} for n in notices] if notices else None
        return {"success":True,"data":data}
    except Exception as e:
        logger.error(f"Database error during fetching notices for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.get('/profile/')
async def user_profile(
    db: AsyncSession = Depends(database.get_db),
    user_id=Depends(verify_user)
):
    try:
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
    except Content_Not_Found:
        raise
    except Exception as e:
        logger.error(f"Database error during fetching user profile for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.put('/personal/')
async def update_personal(user_data:schemas.Personal,db:SessionDp,user_id=Depends(verify_user)):
    try:
        user=await db.get(models.Personal,user_id)
        if not user:
            raise Content_Not_Found("Personal details not found")
        user.contact=str(user_data.contact)
        user.designation=user_data.designation
        user.department=user_data.department
        await db.commit()
        logger.info(f"Personal details updated for user {user_id}")
        return {"success":True,"message":"Details Updates succesfully"}
    except Content_Not_Found:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during updating personal details for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.put('/resident/')
async def update_resident(user_data:schemas.Resident,db:SessionDp,user_id=Depends(verify_user)):
    try:
        user=await db.get(models.Resident,user_id)
        if user is None:
            obj=models.Resident(owner=user_id,house_no=user_data.house_no,block=user_data.block,city=user_data.city,state=user_data.state,pincode=user_data.pincode)
            db.add(obj)
        else:
            user.house_no=user_data.house_no
            user.block=user_data.block
            user.city=user.data.city
            user.state=user.data.state
            user.pincode=user.data.pincode
        await db.commit()
        logger.info(f"Resident details updated for user {user_id}")
        return {"success":True,"message":"Details Updates succesfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during updating resident details for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.post('/vehicle/add/')
async def add_vehicle(user_data:schemas.Add_vehicle,db:SessionDp,user_id=Depends(verify_user)):
    try:
        obj=models.Vehicle(owner=user_id,number=user_data.number)
        db.add(obj)
        await db.commit()
        logger.info(f"Vehicle added for user {user_id}: {user_data.number}")
        return {"success":True,"message":"vehicle added succesfully"}
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during adding vehicle for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.delete('/vehicle/remove/')
async def delete_vehicle(user_data:schemas.Delete_vehicle,db:SessionDp,user_id=Depends(verify_user)):
    try:
        obj=await db.get(models.Vehicle,(user_id,user_data.number))
        if obj==None:
            raise Content_Not_Found(f"Vehicle does not exit of number: {user_data.number}")
        db.delete(obj)
        await db.commit()
        logger.info(f"Vehicle removed for user {user_id}: {user_data.number}")
        return {"success":True,"message":"vehicle delete  succesfully"}
    except Content_Not_Found:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during removing vehicle for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")


