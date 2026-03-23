from sqlalchemy import Column,Integer,String,TIMESTAMP,text,ForeignKey,Identity,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base=declarative_base()

class Email_Table(Base):
    __tablename__="email"
    email=Column(String,nullable=False,primary_key=True)
    otp=Column(Integer,nullable=True)
    expire_at=Column(TIMESTAMP,nullable=True)
    status=Column(Boolean,server_default="false",nullable=False)

class Auth(Base):
    __tablename__="auth"
    user_id=Column(String,nullable=False,unique=True,primary_key=True)
    password=Column(String,nullable=False)
    email=Column(String,nullable=True,unique=True)
    role=Column(String,nullable=False,server_default="USER")
    name=Column(String,nullable=True)
    provider=Column(String,server_default="None")
    provider_id=Column(String,server_default="None")
    resident=relationship("Resident",cascade="all,delete")
    vehicle=relationship("Vehicle",cascade="all,delete")
    personal=relationship("Personal",cascade="all,delete")
    complaint=relationship("Complaint",cascade="all,delete")

class Resident(Base):
    __tablename__="resident"
    house_no=Column(String)
    block=Column(String)
    state=Column(String)
    city=Column(String)
    pincode=Column(String)
    owner=Column(String,ForeignKey("auth.user_id",ondelete="CASCADE"),nullable=False,primary_key=True)
class Personal(Base):
    __tablename__="personal"
    user_id=Column(String,ForeignKey("auth.user_id",ondelete="CASCADE"),nullable=False,primary_key=True)
    email=Column(String,nullable=False)
    Name=Column(String,nullable=False)
    department=Column(String)
    contact=Column(String,nullable=False)
    designation=Column(String)
    timestamp=Column(TIMESTAMP,server_default=text("now()"),nullable=False)
class Vehicle(Base):
    __tablename__="vehicle"
    owner=Column(String,ForeignKey("auth.user_id",ondelete="CASCADE"),nullable=False,primary_key=True)
    number=Column(String,nullable=False,primary_key=True)

class Complaint(Base):
    __tablename__="complaint"
    ticket_id=Column(Integer,Identity(start=201,increment=1),primary_key=True,index=True,nullable=False)
    user_id=Column(String,ForeignKey("auth.user_id",ondelete="CASCADE"),nullable=False)
    description=Column(String,nullable=False)
    category=Column(String,nullable=False)
    attachment=Column(String)
    subject=Column(String)
    status=Column(String,default="Pending")
    remark=Column(String,default="None")

class Epass(Base):
    __tablename__="epass"
    ticket_id=Column(Integer,Identity(start=101, increment=1),primary_key=True,index=True,nullable=False)
    user_id=Column(String,ForeignKey("auth.user_id",ondelete="CASCADE"),nullable=False)
    guest_name=Column(String,nullable=False)
    purpose=Column(String)
    arrival=Column(String)
    departure=Column(String)
    contact=Column(String)
    vehicle_no=Column(String)
    status=Column(String,default="Pending")
    remark=Column(String,default="None")

class Token(Base):
    __tablename__="token"
    token=Column(String,nullable=False)
    user_id=Column(String,nullable=False)
    token_id=Column(String,primary_key=True,nullable=False)

class User_logs(Base):
    __tablename__="user_logs"
    user_id=Column(String,nullable=False)
    name=Column(String,nullable=False)
    logs_id=Column(Integer,Identity(start=1021, increment=1),primary_key=True,nullable=False)
    action=Column(String,nullable=False)
    
class Notices(Base):
    __tablename__="notices"
    notice_id=Column(Integer,Identity(start=1001,increment=1),primary_key=True,nullable=False)
    Type=Column(String,nullable=False)
    body=Column(String,nullable=False)
    user=Column(String,nullable=False)