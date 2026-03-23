from fastapi import APIRouter,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.oauth2 import verify_admin
from app.exception.custom_exceptions import Content_Not_Found
from ...import database,models,schemas
from sqlalchemy import select
router=APIRouter()

@router.get('/complaints/')
async def get_complaints(admin=Depends(verify_admin),db:AsyncSession=Depends(database.get_db)):
    result=await db.execute(select(models.Complaint))
    complaints=result.scalars().all()
    return {"success":True,"data":{"complaints":[{"ticket_id":c.ticket_id,
                            "user_id":c.user_id,
                            "category":c.category,
                            "description":c.description,
                            "attachment":c.attachment,
                            "subject":c.subject,
                            "status":c.status,
                            "remark":c.remark} for c in complaints] if complaints else None,}
                            }
@router.put('/complaint/action')
async def update_complaint(ticket_id:int,c_Data:schemas.Complaint_update,admin=Depends(verify_admin),db:AsyncSession=Depends(database.get_db)):
    comp=await db.get(models.Complaint,ticket_id)
    if comp==None:
        raise Content_Not_Found("Invalid Request")
    elif comp.status.upper()=="APPROVED":
        raise Content_Not_Found("Already Aprroved")
    elif comp.status.upper()=="PENDING":
        comp.status=c_Data.status
        comp.remark=c_Data.remark
        await db.commit()
        return {"success":True,"message":"Complant updated Successfully"}
    else:
        raise Content_Not_Found("Invalid Request")
  