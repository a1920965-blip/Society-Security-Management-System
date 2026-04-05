from fastapi import BackgroundTasks,HTTPException
import smtplib 
from .utils import generate_otp
from app.dependency import SessionDp
import os
from . import models
from email.mime.text import MIMEText
import time

async def send_mail(email:str,db:SessionDp):
    try:
        otp=generate_otp()
        e= await db.get(models.Email_Table,email)
        if not e:
            e=models.Email_Table(email=email,otp=otp,expire_at=int(time.time()+600))
            db.add(e)
        else:
            e.otp=otp
            e.expire_at=int(time.time()+600)
        await db.commit()
    except Exception as error:
        await db.rollback()
        raise HTTPException(status_code=500,detail="Database error occur")
    
    sender=os.getenv("sender")
    password=os.getenv("password")
    html = f"""
    <h2>OTP Verification</h2>
    <p>Your OTP is:</p>
    <h1>{otp}</h1>
    <p>This OTP will expire in 10 minutes.</p>
    """
    msg = MIMEText(html, "html")
    msg["Subject"]="OTP Verification"
    msg["From"]=sender
    msg["To"]=email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(sender,password)
            server.send_message(msg)
    except Exception as error:
        raise HTTPException(status_code=503,detail="Error Occur from SMTP SERVERR")
    
    return {"status":True,"message":"Otp Sent Successfully"}
