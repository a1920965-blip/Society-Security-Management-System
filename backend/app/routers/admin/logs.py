from fastapi import APIRouter,status,HTTPException,Request,Depends,status
from app import schemas,database,models
from app import utils
from app.exception.custom_exceptions import Content_Not_Found
from app.oauth2 import verify_admin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

router=APIRouter()

@router.get('/users/logs')
async def user_logs(db:AsyncSession=Depends(database.get_db),admin=Depends(verify_admin)):
    result =await db.execute(select(models.User_logs))
    logs=result.scalars().all()
    data = [{ 
        "user_id": l.user_id,
        "log_id": l.logs_id,
        "Name": l.name,
        "action": l.action
    } for l in logs] if logs else None
    return {"success":True,"data":data} 