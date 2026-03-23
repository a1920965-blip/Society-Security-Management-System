from fastapi import Request,status
from .custom_exceptions import Not_Authorized,Content_Not_Found
from fastapi.responses import JSONResponse
#So this decorator registers a handler like: If any endpoint raises VehicleNotFound, run this function automatically.
def user_exception_handler(app):

    @app.exception_handler(Not_Authorized)
    def credential_handler(request:Request,exec:Not_Authorized):
        return JSONResponse(status_code=401,content={"success": False,"message": exec.message })
    @app.exception_handler(Content_Not_Found)
    def Content_Not_Found_handler(request:Request,exec:Content_Not_Found):
        return JSONResponse(status_code=404,content={"success":False,"message":exec.message})
def jwt_exception_handler(app):
    pass



def postgres_exception_handler(app):
    pass 
