from fastapi import FastAPI,Request
from app.exception.handle import user_exception_handler,jwt_exception_handler,postgres_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import auth
from app.routers.misls import qr_verify
from app.routers.admin import admin
from app.routers.user import user
import os
from starlette.middleware.sessions import SessionMiddleware

from .import utils
from .state import blocked
from datetime import datetime
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()

app=FastAPI()
app.add_middleware(SessionMiddleware,secret_key=os.getenv("SECRET_KEY"))
ALLOWED_ORIGINS =["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def block_middleware(request:Request,call_next):
    now=datetime.now()
    ip=request.client.host
    print(ip)
    if ip in blocked:
        if blocked[ip]>now:
            return JSONResponse(content="You are Temporary Blocked Try after some time",status_code=403)
        else:
            blocked.pop(ip)
    response=await call_next(request)
    return response


user_exception_handler(app)
jwt_exception_handler(app)
postgres_exception_handler(app)

@app.get('/')
def root(request:Request):
    return "root directory"
app.include_router(qr_verify.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(admin.router)
