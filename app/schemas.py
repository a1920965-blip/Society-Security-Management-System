from pydantic import BaseModel,EmailStr
from fastapi import Form,File
from datetime import datetime
from typing import Optional,List


class Validate_login(BaseModel):
    user_id:str
    password:str
class Validate_user_registration(Validate_login):
    email:EmailStr
    name:str
    contact:Optional[str]="9876543210"

#------------------------------------------------ADMIN SCHEMAS-------------------------------------------------------#
class Validate_admin_registration(BaseModel):
    user_id:str
    password:str
    admin_key:str

#---------------------------------------Response Model--------------------------------------------#
class User_registration_response(BaseModel):
    success:bool
    message:str
#-------------------------------forget-password-----------------------------------------#
class Forget_Password(BaseModel):
    user_id:str
    email:EmailStr
class Otp_Verify(BaseModel):
    otp:str
    email:EmailStr
class Verify_Email(BaseModel):
    email:EmailStr
class Authenticate_Email(Verify_Email):
    pass

class Update_Password(BaseModel):
    user_id: str
    email: EmailStr
    password: str


class Personal(BaseModel):
    contact:Optional[int]=None
    email:Optional[EmailStr]=None
    department:Optional[str]=None
    designation:Optional[str]=None
class Resident(BaseModel):
    house_no:str=None
    block:str=None
    city:str=None
    pincode:str=None
    state:str=None 

class Add_vehicle(BaseModel):
    number:str

class Delete_vehicle(BaseModel):
    number:str

         #---------------------------USER SUPPORT SCHEMAS--------------------
class Complaint_post(BaseModel):
    category:str
    description:str
    subject:str
    has_attachment: Optional[bool] = False
    attachment: Optional[str] = None

class Epass_post(BaseModel):
    vehicle_no:Optional[str]
    contact:int
    guest_name:str
    purpose:Optional[str]
    arrival:Optional[str]="Not Specified"
    departure:Optional[str]="Not Specified"

class Complaint_update(BaseModel):
    status:str
    remark:Optional[str]=None
    
class Epass_update(BaseModel):
    status:str
    remark:Optional[str]=None


class Post_notice(BaseModel):
    Type:str
    body:str
    user:str

#---------------------------------------Response Model--------------------------------------------#
class User_registration_response(BaseModel):
    success:bool
    message:str

    
