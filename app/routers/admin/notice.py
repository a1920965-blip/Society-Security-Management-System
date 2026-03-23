from fastapi import APIRouter,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.oauth2 import verify_admin
from app import database,models,schemas
router=APIRouter()
# will be available soon
@router.post('/notice')
async def post_notice(n_data:schemas.Post_notice,admin=Depends(verify_admin),db:AsyncSession=Depends(database.get_db)):
    n=models.Notices(**n_data.dict())
    db.add(n) 
    await db.commit()
    return {"success":True,"message":"Notice posted Successfully"}
@router.get('/notice')
async def get_notice(db:AsyncSession=Depends(database.get_db),admin=Depends(verify_admin)):
    result =await db.execute(select(models.Notices))
    notices=result.scalars().all()
    return{"status":True,"data":notices}