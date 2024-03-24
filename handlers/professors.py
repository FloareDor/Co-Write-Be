from fastapi import HTTPException, Header, Request, File, UploadFile, Form
import shutil
from fastapi.responses import JSONResponse
from bson import ObjectId
from pydantic import ValidationError
from utils.authenticator import Authenticator
from schemas.assignment import assignmentSchema

class ProfessorHandler:
    def __init__(self, db):
        self.db = db
        self.userCollection = db["users"]
        self.professor_collection = db["professor"]
        self.assignments_collection = db["assignments"]
        self.authenticator = Authenticator(db)

    async def add_new_assignment(
        self,
        request: Request,
        authorization: str = Header(None),
    ):
        if authorization is None:
            raise HTTPException(status_code=500, detail="No Authorization Token Received")

        try:
            # Authorize the request
            encodedUserData = await self.authenticator.Authorize(authorization=authorization)
            print(encodedUserData)
        except HTTPException as http_exception:
            # Handle authorization errors
            return JSONResponse(
                {"detail": f"Authorization error: {http_exception.detail}"},
                status_code=http_exception.status_code,
            )

        try:
            existingUser = self.userCollection.find_one(
                {"sub": encodedUserData["sub"]}  # Query condition
            )
        except Exception as e:
            print(f"USER NOT FOUND: {e}")
            raise HTTPException(status_code=500, detail=f"USER NOT FOUND: {encodedUserData}")

        if existingUser is not None:
            userType = existingUser["type"]
            if userType != "professor":
                raise HTTPException(
                    status_code=400,
                    detail=f"You are not a professor. If you are one, please sign up as a professor.",
                )

        try:
            form_data = await request.form()
            title = form_data.get("title")
            description = form_data.get("description")
            ai_limitation = form_data.get("ai_limitation")
            resource_file = form_data.get("resource_file")

            if not all([title, description, ai_limitation]):
                raise HTTPException(
                    status_code=400,
                    detail="Title, description, and ai_limitation are required.",
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error: {e}",
            )

        try:
            assignment_id = str(ObjectId())
            assignment_data = {
                "_id": assignment_id,
                "professor_id": str(encodedUserData["_id"]),
                "title": title,
                "description": description,
                "ai_limitation": ai_limitation,
                "resource_file": None,
            }

            try:
                if resource_file:
                    file_path = f"rag_custom_data/docs/{resource_file.filename}"
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(resource_file.file, buffer)
                    assignment_data["resource_file"] = resource_file.filename
            except Exception as e:
                print(f"resource file error: {e}")

            # Validate the assignment data using the Pydantic schema
            assignment_schema = assignmentSchema(**assignment_data)
            # Insert the assignment into the database
            result = self.assignments_collection.insert_one(assignment_data)
            # Check if the insertion was successful
            if result.acknowledged:
                return JSONResponse(
                    {"message": "Assignment added successfully", "assignment_id": assignment_id},
                    status_code=200,
                )
            else:
                return {"message": "Failed to add assignment"}
        except ValidationError as e:
            # Handle validation errors
            raise HTTPException(status_code=400, detail=f"Invalid assignment data: {e.errors()}")

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")