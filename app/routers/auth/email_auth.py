import logging
from datetime import datetime,timedelta
from fastapi import APIRouter,Request,HTTPException,BackgroundTasks
from app import schemas,models,tasks,utils
from  app.utils import rate_limit_login_attempts
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from app.tasks import send_mail
from app.dependency import SessionDp
import time

logger = logging.getLogger(__name__)

router=APIRouter()

@router.post('/verify-email/')
async def verify_email(request:Request,payload:schemas.Verify_Email,db:SessionDp,background_task:BackgroundTasks):
    try:
        result=await db.execute(select(models.Auth).where(models.Auth.email==payload.email))
        registered=result.scalars().first()
        if registered:
            logger.warning(f"Email verification attempt for already registered email: {payload.email}")
            raise HTTPException(status_code=403,detail="Email Id Belongs To Other Person")
        background_task.add_task(send_mail,payload.email)
        logger.info(f"OTP sent for email verification: {payload.email}")
        return {"success":True,"message":"Otp sended Successfully"}
    except HTTPException:
        raise 
    except Exception as error:
        await db.rollback()
        logger.error(f"Database error during email verification for {payload.email}: {str(error)}")
        raise HTTPException(status_code=500,detail="database error occured")
       

@router.post('/verify-otp/',status_code=200)
async def verify_otp(request:Request,payload:schemas.Otp_Verify,db:SessionDp):
    try:
        rate_limit_login_attempts(request)
        user=await db.get(models.Email_Table,payload.email)
        if not user or not user.otp:
            logger.warning(f"OTP verification attempt for invalid or missing OTP: {payload.email}")
            raise HTTPException(status_code=403)
        elif user.expire_at<int(time.time()):
            logger.warning(f"Expired OTP verification attempt: {payload.email}")
            raise HTTPException(status_code=404,detail="OTP expired please Try Again")
        elif user.otp != int(payload.otp):
            logger.warning(f"Invalid OTP provided: {payload.email}")
            raise HTTPException(status_code=401,detail=" Invalid OTP")
        else:
            user.otp=None
            user.expire_at=None
            user.status=True
            await db.commit()
            logger.info(f"Email verified successfully: {payload.email}")
        return {"status":True,"message":"Email Verified successfuly"}
    except HTTPException:
        raise 
    except Exception as error:
        await db.rollback()
        logger.error(f"Database error during OTP verification for {payload.email}: {str(error)}")
        raise HTTPException(status_code=500,detail="Database error occur")
