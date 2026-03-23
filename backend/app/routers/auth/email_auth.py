
from datetime import datetime,timedelta
from fastapi import APIRouter,Depends,Request,HTTPException,BackgroundTasks
from app import schemas,database,models,tasks,utils
from  app.utils import rate_limit_login_attempts,verify_csrf_token
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse
from sqlalchemy import select


router=APIRouter()

@router.post('/verify-email/')
async def verify_email(request:Request,payload:schemas.Verify_Email,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    result=await db.execute(select(models.Auth).where(models.Auth.email==payload.email))
    registered=result.scalars().first()
    if registered:
        raise HTTPException(status_code=403,detail="Email Id Belongs To Other Account")
    return RedirectResponse(url="/auth/email/",status_code=307)
@router.post('/email/',status_code=200)
async def authenticate_email(request:Request,background_task:BackgroundTasks,payload:schemas.Authenticate_Email,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    rate_limit_login_attempts(request)
    Otp=utils.generate_otp()
    user=await db.get(models.Auth,payload.email)
    if not user:
        user=models.Email_Table(email=payload.email,expire_at=datetime.now()+timedelta(minutes=10),otp=Otp)
    else:
        user.otp=Otp
        user.expire_at=datetime.now()+timedelta(minutes=10)
    db.add(user)
    await db.commit()
    response=background_task.add_task(tasks.send_mail,payload.email,Otp)
    return {"status":True,"message":"OTP sent Successfully"}

@router.post('/verify-otp/',status_code=200)
async def verify_otp(request:Request,payload:schemas.Otp_Verify,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    rate_limit_login_attempts(request)
    user=await db.get(models.Email_Table,payload.email)
    if not user or not user.otp:
        raise HTTPException(status_code=403)
    elif user.expire_at<datetime.now():
        raise HTTPException(status_code=404,detail="OTP expired please Try Again")
    elif user.otp != int(payload.otp):
        raise HTTPException(status_code=401,detail=" Invalid OTP")
    else:
        user.otp=None
        user.expire_at=None
        user.status=True
        await db.commit()
    return {"status":True,"message":"Email Verified successfuly"}