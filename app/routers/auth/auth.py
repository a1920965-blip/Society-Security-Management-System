import logging
from fastapi import APIRouter,Depends,status,Request,HTTPException,BackgroundTasks
from app import schemas,database,models,utils
from  app.utils import rate_limit_login_attempts
from app.oauth2 import create_access_token
import os
from app.tasks import send_mail
from app.dependency import SessionDp
from fastapi.responses import RedirectResponse,JSONResponse
from . import email_auth,provider

logger = logging.getLogger(__name__)

router=APIRouter(prefix="/auth",tags=["Authentication"])

router.include_router(email_auth.router)
router.include_router(provider.router)

@router.get('/home/')
def root():
    return JSONResponse(content="Root Directory",status_code=200)


@router.post('/login/',status_code=200)
async def validate_login(request:Request,user_data:schemas.Validate_login,db:SessionDp):
    try:
        rate_limit_login_attempts(request)
        user=await db.get(models.Auth,user_data.user_id)
        if not user or not utils.verify(user_data.password,user.password):
            logger.warning(f"Failed login attempt for user: {user_data.user_id}")
            raise HTTPException(status_code=401,detail="Invalid Credential user not found!")
        logger.info(f"Successful login for user: {user_data.user_id}")
        token=create_access_token({"user_id":user_data.user_id,"role":user.role})
        return {"success":True,"role":user.role,"user_id":user.user_id,"access_token": token,"token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(status_code=500,detail="Database error occurred")

@router.post('/register/user/',response_model=schemas.User_registration_response,status_code=status.HTTP_201_CREATED)
async def user_registration(request:Request,user_data:schemas.Validate_user_registration,db:SessionDp):
    try:
        rate_limit_login_attempts(request)
        existing=await db.get(models.Auth,user_data.user_id)
        if existing:
            logger.warning(f"Duplicate registration attempt for user: {user_data.user_id}")
            raise HTTPException(status_code=409,detail="User Already Exit")
        check=await db.get(models.Email_Table,user_data.email)
        if not check or not check.status:
            logger.warning(f"Email not verified for user: {user_data.user_id}")
            raise HTTPException(status_code=403,detail="Email not Verified")
        check.status=False
        auth=models.Auth(user_id=user_data.user_id,password=utils.hash(user_data.password),role="USER",email=user_data.email,provider="app",provider_id=utils.generate_user_id())
        
        Qr=utils.generate_qr_code(user_data.user_id)
        token_obj=models.Token(user_id=user_data.user_id,token=Qr["data"],token_id=Qr["token_id"])
        log=models.User_logs(user_id=user_data.user_id,action="Register",name=user_data.name)
        personal=models.Personal(user_id=user_data.user_id,contact=user_data.contact,email=user_data.email,Name=user_data.name)
        db.add(token_obj)
        db.add(log)
        db.add(auth)
        db.add(personal)
        await db.commit()
        logger.info(f"User registered successfully: {user_data.user_id}")
        return {"success":True,"message":"Registeration Successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during user registration for {user_data.user_id}: {str(e)}")
        raise HTTPException(status_code=500,detail="Database error occurred during registration")

@router.post('/register/admin/',status_code=201)
async def admin_registration(request:Request,user_data:schemas.Validate_admin_registration,db:SessionDp):
    try:
        rate_limit_login_attempts(request)
        existing=await db.get(models.Auth,user_data.user_id)
        if existing:
            logger.warning(f"Duplicate admin registration attempt for user: {user_data.user_id}")
            raise HTTPException(status_code=409,detail="Admin Already Exit")
        if user_data.admin_key!=os.getenv("ADMIN_CODE"):
            logger.warning(f"Invalid admin code provided for user: {user_data.user_id}")
            raise HTTPException(status_code=401,detail="Wrong Security code!")
        else:
            auth=models.Auth(user_id=user_data.user_id,password=utils.hash(user_data.password),role="ADMIN",email=user_data.email,provider="app",provider_id=utils.generate_user_id())
            db.add(auth)
            await db.commit()
            logger.info(f"Admin registered successfully: {user_data.user_id}")
        return {"success":True,"message":"Admin Register Successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during admin registration for {user_data.user_id}: {str(e)}")
        raise HTTPException(status_code=500,detail="Database error occurred during admin registration")

@router.post('/forget-password/')
async def forget_password(request:Request,payload:schemas.Forget_Password,db:SessionDp,background_task:BackgroundTasks):
    try:
        rate_limit_login_attempts(request)
        user=await db.get(models.Auth,payload.user_id)
        if not user or user.email != payload.email:
            logger.warning(f"Failed password reset attempt for user: {payload.user_id}")
            raise HTTPException(status_code=404,detail="Invalid Email Address")
        logger.info(f"Password reset initiated for user: {payload.user_id}")
        background_task.add_task(send_mail,user.email)
        return {"status":True,"message":"Otp Send Successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error during forget password for {payload.user_id}: {str(e)}")
        raise HTTPException(status_code=500,detail="Database error occurred")

@router.put('/update-password/',status_code=200)
async def update_password(request:Request,payload:schemas.Update_Password,db:SessionDp):
    try:
        rate_limit_login_attempts(request)
        user=await db.get(models.Auth,payload.user_id)
        if not user:
            logger.warning(f"Password update attempt for non-existent user: {payload.user_id}")
            raise HTTPException(status_code=404)
        check_email=await db.get(models.Email_Table,payload.email)
        if not check_email or not check_email.status:
            logger.warning(f"Email not verified for password update: {payload.user_id}")
            raise HTTPException(status_code=403,detail="Email not Verified")
        user.password=utils.hash(payload.password)
        check_email.status=False
        await db.commit()
        logger.info(f"Password updated successfully for user: {payload.user_id}")
        return {"status":True,"message":"Password Updated Successfully !"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during password update for {payload.user_id}: {str(e)}")
        raise HTTPException(status_code=500,detail="Database error occurred")