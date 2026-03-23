from fastapi import APIRouter,Depends,status,Request,HTTPException,BackgroundTasks
from app import database,models,utils
from app.oauth2 import create_access_token
import os
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from datetime import datetime,timedelta
from app.utils import verify_csrf_token
from .api_config import oauth
import json
from sqlalchemy import select

router=APIRouter()
@router.get("/google/")
async def login_google(request:Request):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    redirect_uri="http://127.0.0.1:8000/auth/google/callback/"
    print(redirect_uri)
    return await oauth.google.authorize_redirect(request,redirect_uri)

@router.get("/google/callback/")
async def auth_google_callback(request:Request,db:AsyncSession=Depends(database.get_db)):
    token= await oauth.google.authorize_access_token(request)
    user_info=token.get("userinfo")
    if not user_info:
        return {"error":"User info not found"}
    email=user_info["email"]
    name=user_info.get("name")
    google_id=user_info["sub"]

    result=await db.execute(select(models.Provider).where(models.Provider.platform=="google",models.Provider.provider_id==google_id))
    user=result.scalars().first()
    if not user:
        user=models.Auth(user_id=user_id,password=utils.hash(""),role="USER",email=email)
        Qr=utils.generate_qr_code(user_id)
        token_obj=models.Token(user_id=user_id,token=Qr["data"],token_id=Qr["token_id"])
        log=models.User_logs(user_id=user_id,action="Register",name=name)
        personal=models.Personal(user_id=user_id,contact="987654321",email=email,Name=name)
        db.add(token_obj)
        db.add(log)
        db.add(personal)
        db.add(user)
        await db.commit()
    user_id=utils.generate_user_id()
    payload={"user_id":user_id,"name":name}
    token=create_access_token(payload)
    payload_json=json.dumps({"success":True,"role":"USER","user_id":user_id,"access_token": token,"token_type": "bearer",})
    return HTMLResponse(utils.get_js_scripts(payload_json))
@router.get('/github/')
async def login_github(request:Request,db:AsyncSession=Depends(database.get_db)):
    # verify_csrf_token(request.headers.get("X-CSRF-Token"))
    redirect_uri="http://127.0.0.1:8000/auth/github/callback/"
    return await oauth.github.authorize_redirect(request,redirect_uri)

@router.get("/github/callback/")
async def auth_github_callback(request: Request,code, db: AsyncSession = Depends(database.get_db)):
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get("https://api.github.com/user", token=token)
    user_info = resp.json()
    print(user_info)
    github_id = str(user_info["id"])
    name = user_info.get("name") or user_info.get("login")
    email = user_info.get("email")
    if not email:
        resp = await oauth.github.get("https://api.github.com/user/emails", token=token)
 
        emails = resp.json()
        email = emails[0]["email"]
    user_id = utils.generate_user_id()
    result= await db.execute(select(models.Provider).where(models.Provider.platform == "github",models.Provider.provider_id == github_id))
    user=result.scalars().first()
    if not user:
        user = models.Provider(name=name,email=email,provider_id=github_id,platform="github")
        auth=models.Auth(user_id=user_id,password=utils.hash(""),role="USER",email=email)
        Qr=utils.generate_qr_code(user_id)
        token_obj=models.Token(user_id=user_id,token=Qr["data"],token_id=Qr["token_id"])
        log=models.User_logs(user_id=user_id,action="Register",name=name)
        personal=models.Personal(user_id=user_id,contact="987654321",email=email,Name=name)
        db.add(token_obj)
        db.add(log)
        db.add(personal)
        db.add(user)
        await db.commit()
    jwt_token = create_access_token({"user_id": user_id,"name": name})
    payload_json = json.dumps({"success": True,"role": "USER","user_id": user_id,"access_token": jwt_token,"token_type": "bearer",})
    return HTMLResponse(utils.get_js_scripts(payload_json))