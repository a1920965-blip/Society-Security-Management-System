from fastapi import APIRouter,Depends
from app import database,models
from app.exception.custom_exceptions import Not_Authorized
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router=APIRouter(tags=["QrCode/Token Valdation"])

@router.get('/verify/')
async def token_verify(token_id:str,db:AsyncSession=Depends(database.get_db)):
    result=await db.execute(select(models.Token).where(models.Token.token_id==token_id))
    user=result.scalars().first()
    if user==None:
        raise Not_Authorized("Invalid Token")
    return {"success":True,"message":"Verifyed user"}