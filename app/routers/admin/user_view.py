from fastapi import APIRouter,Depends
from app.oauth2 import verify_admin
from app.exception.custom_exceptions import Content_Not_Found
from app import database,models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
router=APIRouter()

@router.get('/users')
async def list_users(admin=Depends(verify_admin),db:AsyncSession=Depends(database.get_db)):
    result=await db.execute(select(models.Personal.user_id,models.Personal.Name))
    users=result.all()
    return {"success":True,"data":[{"user_id":u.user_id,"Name":u.Name} for u in users]}
@router.get('/user/')
async def user_profile(
    user_id: str,
    db: AsyncSession = Depends(database.get_db),
    admin=Depends(verify_admin)
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

    user = result.scalars().first()

    if not user:
        raise Content_Not_Found("User Not Found")

    personal = user.personal[0] if user.personal else None
    resident = user.resident[0] if user.resident else None
    vehicle = user.vehicle

    return {
        "success": True,
        "data": {
            "user_id": user.user_id,
            "Name": user.name,
            "designation": personal.designation if personal else None,
            "department": personal.department if personal else None,
            "contact": personal.contact if personal else None,
            "email": user.email,
            "house_no": resident.house_no if resident else None,
            "block": resident.block if resident else None,
            "city": resident.city if resident else None,
            "state": resident.state if resident else None,
            "pincode": resident.pincode if resident else None,
            "vehicles": [{"Number": v.number} for v in vehicle] if vehicle else []
        }
    }