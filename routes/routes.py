from fastapi import APIRouter, Request, Header
from typing import Dict, Any, List
from starlette.requests import Request
from fastapi.responses import JSONResponse
from utils.authenticator import Authenticator

from handlers.professors import ProfessorHandler
from handlers.students import StudentHandler

from utils.scripts import initDB

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
@router.post("/verify-user")
@limiter.limit("12/minute")
async def verifyUser(request: Request):
    return await authenticator.Verify_user(request)

@router.post("/add-assignment")
@limiter.limit("30/minute")
async def add_assignment(request: Request, authorization: str = Header(None)):
    return await professorHandler.add_new_assignment(request, authorization=authorization)

@router.post("/open-assignment")
@limiter.limit("30/minute")
async def open_assignment(request: Request, authorization: str = Header(None)):
    return await studentHandler.open_assignment(request, authorization=authorization)

@router.post("/submit-assignment")
@limiter.limit("30/minute")
async def submit_assignment(request: Request, authorization: str = Header(None)):
    return await studentHandler.submit_assignment(request, authorization=authorization)

@router.post("/assignments-by-prof")
@limiter.limit("30/minute")
async def get_assignments_by_prof(request: Request, authorization: str = Header(None)):
    return await professorHandler.get_assignments_by_prof(request, authorization=authorization)

@router.post("/assignments-by-student")
@limiter.limit("30/minute")
async def get_submissions_by_student(request: Request, authorization: str = Header(None)):
    return await studentHandler.get_submissions_by_student(request, authorization=authorization)

@router.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, authorization: str = Header(None)):
    return await studentHandler.chat(request, authorization=authorization)

@router.post("/assignment-by-id")
@limiter.limit("30/minute")
async def get_assignment_by_id(request: Request, authorization: str = Header(None)):
    return await professorHandler.get_assignment_by_id(request, authorization=authorization)

@router.post("/joined-students")
@limiter.limit("30/minute")
async def get_joined_students(request: Request, authorization: str = Header(None)):
    return await professorHandler.get_joined_students(request, authorization=authorization)

@router.post("/update-assignment")
@limiter.limit("30/minute")
async def update_assignment(request: Request, authorization: str = Header(None)):
    return await professorHandler.update_assignment(request, authorization=authorization)



