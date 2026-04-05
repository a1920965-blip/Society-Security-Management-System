from passlib.context import CryptContext
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import os
import requests
import qrcode
import io
import base64
from datetime import datetime,timedelta
from uuid import uuid4
import secrets
from itsdangerous import URLSafeTimedSerializer,SignatureExpired,BadSignature
from .state import blocked
from .state import blocked
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
def hash(password:str):
    return pwd_context.hash(password)

def verify(plain_password,hashed):
    return pwd_context.verify(plain_password,hashed)


def generate_qr_code(user_id: str) -> str:
    token_id=f"{user_id}/{str(uuid4())}"
    token_url=f"{os.getenv('base_url')}/{token_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(token_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return {"data":qr_base64,"token_id":token_id}

ratings: dict[str, dict[str, int | datetime]] = {}

def rate_limit_login_attempts(request, critical_attempts=5,max_attempts=10, threshold_window_time=60):
    ip = request.client.host
    now = datetime.now()

    if ip not in ratings:
        ratings[ip] = {"time": now, "attempts": 1}
        return

    window_time = now - ratings[ip]["time"]

    if window_time <= timedelta(seconds=threshold_window_time):
        if ratings[ip]["attempts"] >= max_attempts:
            blocked[ip]=now+timedelta(minutes=2)
            raise HTTPException(status_code=429, content="Too many attempts ,You are Temporaily Blocked")
        elif ratings[ip]["attempts"] >= critical_attempts:
            ratings[ip]["attempts"] += 1
            raise HTTPException(status_code=429, detail="Too many attempts , Try After SomeTime")
        ratings[ip]["attempts"] += 1
    else:
        # reset window
        ratings[ip] = {"time": now, "attempts": 1}

def generate_otp():
    return int("".join(secrets.choice("0123456789") for _ in range(6)))

def generate_user_id():
    s="qwertyuioplkjhgfdsazxcvbnm1234567890"
    return "".join(secrets.choice(s) for _ in range(8))



def get_js_scripts(payload):
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Authenticating...</title></head>
    <body>
        <script>
            const data = {payload};
            
            // Send the data directly to the main window that opened this popup
            if (window.opener) {{
                window.opener.postMessage({{ type: 'google_oauth_result', payload: data }}, "*");
            }}
            
            // Automatically close this popup
            window.close();
        </script>
    </body>
    </html>
    """


SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeTimedSerializer(SECRET_KEY, salt="csrf")

def generate_csrf_token():
    return serializer.dumps("csrf-token")

def verify_csrf_token(token,max_age=3600):
    if not token:
        raise HTTPException(status_code=404,detail="CSRF Token Missing")
    try:
        serializer.loads(token,max_age=max_age)
        return True
    except SignatureExpired:
        raise HTTPException(status_code=403, detail="CSRF Token Expired")
    except BadSignature:
        raise HTTPException(status_code=403,detail="Invalid CSRF Token ")





