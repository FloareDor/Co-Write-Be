from fastapi import APIRouter, Request, Header
from typing import Dict, Any, List
from starlette.requests import Request
from fastapi.responses import JSONResponse
from utils.authenticator import Authenticator

from handlers.professors import ProfessorHandler
from handlers.students import StudentHandler

from utils.scripts import initDB, insertSampleData

from fastapi import Query

db = initDB()
# insertSampleData("data/Final_data.csv", db)
professorHandler = ProfessorHandler(db)
studentHandler = StudentHandler(db)
authenticator = Authenticator(db)

# rate limit imports
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()

# Health check
@router.get("/", response_model=List[Dict[str, Any]])
@limiter.limit("30/minute")
async def health(request: Request):
    return JSONResponse({"status": "ok"}, status_code=200)

# Auth
@router.post("/verify_user")
@limiter.limit("12/minute")
async def verifyUser(request: Request):
    return await authenticator.Verify_user(request)

@router.post("/add-assignment")
@limiter.limit("30/minute")
async def onboard(request: Request, authorization: str = Header(None)):
    return await professorHandler.add_new_assignment(request, authorization=authorization)

@router.post("/submit-assignment")
@limiter.limit("30/minute")
async def onboard(request: Request, authorization: str = Header(None)):
    return await studentHandler.submit_assignment(request, authorization=authorization)



# @router.get("/professors", response_model=List[Dict[str, Any]])
# @limiter.limit("30/minute")
# async def getprofessors(request: Request, query: str = Query(None)):
#     if query:
#         return await professorHandler.search_professors(request, query)
#     else:
#         return await professorHandler.get_all_professors(request)

# @router.get("/{professor}/items", response_model=List[Dict[str, Any]])
# @limiter.limit("30/minute")
# async def health(request: Request):
#     return JSONResponse({"status": "ok"}, status_code=200)

# @router.post("/healthify-menu")
# @limiter.limit("30/minute")
# async def onboard(request: Request, authorization: str = Header(None)):
#     return await studentHandler.healthifyMenu(request, authorization=authorization)

# @router.get("/add-to-favourites", response_model=List[Dict[str, Any]])
# @limiter.limit("30/minute")
# async def health(request: Request):
#     return JSONResponse({"status": "ok"}, status_code=200)

# # Auth
# @router.post("/verify_user")
# @limiter.limit("12/minute")
# async def verifyUser(request: Request):
#     return await authenticator.Verify_user(request)




