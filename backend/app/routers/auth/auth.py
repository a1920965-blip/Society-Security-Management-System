from fastapi import APIRouter,Depends,status,Request,HTTPException,BackgroundTasks
from app import schemas,database,models,utils
from  app.utils import rate_limit_login_attempts,verify_csrf_token
from app.oauth2 import create_access_token
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse,JSONResponse
from . import email_auth,provider

router=APIRouter(prefix="/auth",tags=["Authentication"])

router.include_router(email_auth.router)
router.include_router(provider.router)
@router.get('/home/')
def root():
    return JSONResponse(content="Root Directory",status_code=200)


@router.post('/login/',status_code=200)
async def validate_login(request:Request,credential:schemas.Validate_login,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    rate_limit_login_attempts(request)
    user=await db.get(models.Auth,credential.user_id)
    print(user)
    if user==None or not utils.verify(credential.password,user.password):
        print("errror is here")
        raise HTTPException(status_code=401,detail="Invalid Credential user not found!")
    token=create_access_token({"user_id":credential.user_id,"role":user.role})
    return {"success":True,"role":user.role,"user_id":user.user_id,"access_token": token,"token_type": "bearer",}

@router.post('/register/user/',response_model=schemas.User_registration_response,status_code=status.HTTP_201_CREATED)
async def user_registration(request:Request,f_data:schemas.Validate_user_registration,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    rate_limit_login_attempts(request)
    existing=await db.get(models.Auth,f_data.user_id)
    if existing:
        raise HTTPException(status_code=409,detail="User Already Exit")
    check=await db.get(models.Email_Table,f_data.email)
    if not check or not check.status:
        raise HTTPException(status_code=403,detail="Email not Verified")
    check.status=False
    auth=models.Auth(user_id=f_data.user_id,password=utils.hash(f_data.password),role="USER",email=f_data.email)
    
    Qr=utils.generate_qr_code(f_data.user_id)
    token_obj=models.Token(user_id=f_data.user_id,token=Qr["data"],token_id=Qr["token_id"])
    log=models.User_logs(user_id=f_data.user_id,action="Register",name=f_data.name)
    personal=models.Personal(user_id=f_data.user_id,contact=f_data.contact,email=f_data.email,Name=f_data.name)
    db.add(token_obj)
    db.add(log)
    db.add(auth)
    db.add(personal)
    await db.commit()
    return {"success":True,"message":"Registeration Successfully!"}

@router.post('/register/admin/',status_code=201)
async def admin_registration(request:Request,f_data:schemas.Validate_admin_registration,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    rate_limit_login_attempts(request)
    existing=await db.get(models.Auth,f_data.user_id)
    if existing:
        raise HTTPException(status_code=409,detail="Admin Already Exit")
    if f_data.admin_key!=os.getenv("ADMIN_CODE"):
        raise HTTPException(status_code=401,detail="Wrong Security code!")
    else:
        auth=models.Auth(user_id=f_data.user_id,password=utils.hash(f_data.password),role="ADMIN")
        db.add(auth)
        await db.commit()
    return {"success":True,"message":"Admin Register Successfully!"}


@router.post('/forget-password/')
async def forget_password(request:Request,payload:schemas.Forget_Password,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    rate_limit_login_attempts(request)
    user=await db.get(models.Auth,payload.user_id)
    if not user or user.email != payload.email:
        raise HTTPException(status_code=404,detail="Invalid Email Address")
    return RedirectResponse(url="/auth/email/",status_code=307)

@router.put('/update-password/',status_code=200)
async def update_password(request:Request,payload:schemas.Update_Password,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    rate_limit_login_attempts(request)
    user=await db.get(models.Auth,payload.user_id)
    if not user:
        raise HTTPException(status_code=404)
    check_email=await db.get(models.Email_Table,payload.email)
    if not check_email or not check_email.status:
        raise HTTPException(status_code=403,detail="Email not Verified")
    user.password=utils.hash(payload.password)
    check_email.status=False
    await db.commit()
    return {"status":True,"message":"Password Updated Successfully !"}

