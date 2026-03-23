from fastapi import BackgroundTasks
import smtplib 
import os
from email.mime.text import MIMEText


def send_mail(email:str,otp:int):
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
    with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
        server.login(sender,password)
        server.send_message(msg)
    return {"status":True,"message":"Otp Sent Successfully"}
