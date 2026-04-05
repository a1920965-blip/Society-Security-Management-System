import logging
from fastapi import APIRouter,Depends,status,Request,HTTPException,BackgroundTasks
from app import database,models,utils
from app.oauth2 import create_access_token
import os
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from app.dependency import SessionDp
from app.utils import verify_csrf_token
from .api_config import oauth
import json
from sqlalchemy import select

logger = logging.getLogger(__name__)

router=APIRouter()

@router.get("/google/")
async def login_google(request:Request):
    redirect_uri="http://127.0.0.1:8000/auth/google/callback/"
    return await oauth.google.authorize_redirect(request,redirect_uri)

@router.get("/google/callback/")
async def auth_google_callback(request:Request,db:SessionDp):
    try:
        token= await oauth.google.authorize_access_token(request)
        user_info=token.get("userinfo")
        if not user_info:
            raise HTTPException(status_code=400, detail="User info not found")
        email=user_info["email"]
        name=user_info.get("name")
        google_id=user_info["sub"]
        
        result=await db.execute(select(models.Auth).where(models.Auth.provider=="google",models.Auth.provider_id==google_id))
        user=result.scalars().first()
        if not user:
            user_id=utils.generate_user_id()
            user=models.Auth(user_id=user_id,password=utils.hash(""),role="USER",email=email,name=name,provider_id=google_id,provider="google")  # Fixed provider to "google"
            Qr=utils.generate_qr_code(user_id)
            token_obj=models.Token(user_id=user_id,token=Qr["data"],token_id=Qr["token_id"])
            log=models.User_logs(user_id=user_id,action="Register",name=name)
            personal=models.Personal(user_id=user_id,contact="987654321",email=email,Name=name)
            db.add(token_obj)
            db.add(log)
            db.add(personal)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"New Google user registered: {user_id}")
        
        payload={"user_id":user.user_id,"name":name}
        token=create_access_token(payload)
        payload_json=json.dumps({"success":True,"role":"USER","user_id":user.user_id,"access_token": token,"token_type": "bearer",})
        return HTMLResponse(utils.get_js_scripts(payload_json))
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during Google auth callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")

@router.get('/github/')
async def login_github(request:Request,db:SessionDp):
    redirect_uri="http://127.0.0.1:8000/auth/github/callback/"
    return await oauth.github.authorize_redirect(request,redirect_uri)

@router.get("/github/callback/")
async def auth_github_callback(request: Request, db: SessionDp):
    try:
        token = await oauth.github.authorize_access_token(request)
        resp = await oauth.github.get("https://api.github.com/user", token=token)
        user_info = resp.json()
        github_id = str(user_info["id"])
        name = user_info.get("name") or user_info.get("login")
        email = user_info.get("email")
        if not email:
            resp = await oauth.github.get("https://api.github.com/user/emails", token=token)
            emails = resp.json()
            email = emails[0]["email"]
        result= await db.execute(select(models.Auth).where(models.Auth.provider == "github",models.Auth.provider_id == github_id))
        user=result.scalars().first()
        if not user:
            user_id = utils.generate_user_id()
            user=models.Auth(user_id=user_id,password=utils.hash(""),role="USER",email=email,provider_id=github_id,provider="github")
            Qr=utils.generate_qr_code(user_id)
            token_obj=models.Token(user_id=user_id,token=Qr["data"],token_id=Qr["token_id"])
            log=models.User_logs(user_id=user_id,action="Register",name=name)
            personal=models.Personal(user_id=user_id,contact="987654321",email=email,Name=name)
            db.add(token_obj)
            db.add(log)
            db.add(personal)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"New GitHub user registered: {user_id}")
        jwt_token = create_access_token({"user_id":user.user_id,"name": name})
        payload_json = json.dumps({"success": True,"role": "USER","user_id":user.user_id,"access_token": jwt_token,"token_type": "bearer",})
        return HTMLResponse(utils.get_js_scripts(payload_json))
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Database error during GitHub auth callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")