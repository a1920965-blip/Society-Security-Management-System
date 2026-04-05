from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from.database import get_db
from typing import Annotated


SessionDp=Annotated[AsyncSession,Depends(get_db)]