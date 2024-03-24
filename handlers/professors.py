from fastapi import HTTPException, Header, Request, File, UploadFile, Form
import shutil
from fastapi.responses import JSONResponse
from bson import ObjectId
from pydantic import ValidationError
from utils.authenticator import Authenticator
from schemas.assignment import assignmentSchema
import re
import requests

class ProfessorHandler:
    def __init__(self, db):
        self.db = db
        self.userCollection = db["users"]
        self.professor_collection = db["professor"]
        self.assignments_collection = db["assignments"]
        self.authenticator = Authenticator(db)

    async def call_index_function(assignment_id):
        try:
            url = f"http://localhost:8001/index?assignment_id={assignment_id}"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            # Error occurred during the request
            print(f"Error: {e}")
            return False

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
                "active": True,
            }

            try:
                if resource_file:
                    file_path = f"rag_custom_data/docs/{assignment_id}/{resource_file.filename}"
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
                call_result = await self.call_index_function(assignment_id)
                if call_result:
                    print("Index function call was successful")
                else:
                    print("Index function call failed")
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
        
    async def update_assignment(
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
            assignment_id = form_data.get("assignment_id")
            title = form_data.get("title")
            description = form_data.get("description")
            ai_limitation = form_data.get("ai_limitation")
            active = form_data.get("active")
            resource_file = form_data.get("resource_file")
            

            if not all([assignment_id]):
                raise HTTPException(
                    status_code=400,
                    detail="assignment_id is required.",
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error: {e}",
            )
        try:
            existingAssignment = self.assignments_collection.find_one(
                {"assignment_id": assignment_id}  # Query condition
            )
        except Exception as e:
            print(f"assignment NOT FOUND: {e}")
            raise HTTPException(status_code=500, detail=f"assignment NOT FOUND: {assignment_id}")

        if existingAssignment is not None:
            if existingAssignment["professor_id"] != encodedUserData["_id"]:
                raise HTTPException(status_code=403 , detail=f"You did not create this assignment. Therefore you do not have permission to edit.")

        try:
            assignment_data = {}
            if title:
                assignment_data["title"] = title
            if description:
                assignment_data["description"] = description
            if ai_limitation:
                assignment_data["ai_limitation"] = ai_limitation
            if active is not None:
                assignment_data["active"] = active

            if resource_file:
                try:
                    file_path = f"rag_custom_data/docs/{assignment_id}/{resource_file.filename}"
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(resource_file.file, buffer)
                    assignment_data["resource_file"] = resource_file.filename
                except Exception as e:
                    print(f"resource file error: {e}")
                    raise HTTPException(status_code=400, detail=f"resource file error: {e}")

            existing_assignment = self.assignments_collection.find_one({"_id": assignment_id})
            if existing_assignment:
                # Update existing assignment
                result = self.assignments_collection.update_one(
                    {"_id": assignment_id},
                    {"$set": assignment_data}
                )
            else:
                raise HTTPException(status_code=400, detail=f"No existing assignment found: {assignment_data}")

            # Validate the assignment data using the Pydantic schema
            assignment_schema = assignmentSchema(**assignment_data)
            # Insert the assignment into the database
            result = self.assignments_collection.insert_one(assignment_data)
            # Check if the insertion was successful
            if result.acknowledged:
                call_result = await self.call_index_function(assignment_id)
                if call_result:
                    print("Index function call was successful")
                else:
                    print("Index function call failed")
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
        
    async def get_assignments_by_prof(
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
        
        professor_id = encodedUserData["_id"]
        assignments = []
        for assignment in self.assignments_collection.find({"professor_id": re.compile(professor_id, re.IGNORECASE)}).sort("title"):
            # Convert the ObjectId to string representation before returning
            assignment["_id"] = str(assignment["_id"])
            assignments.append(assignment)
        if assignments:
            response = JSONResponse(assignments, status_code=200)
            return response
        else:
            raise HTTPException(status_code=404, detail=f"No assignments posted by professor: {professor_id}")
         
    async def get_assignment_by_id(
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
        
        try:
            form_data = await request.form()
            assignment_id = form_data.get("assignment_id")

            if not all([assignment_id]):
                raise HTTPException(
                    status_code=400,
                    detail="assignment_id is required.",
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error: {e}",
            )
        
        professor_id = encodedUserData["_id"]
        try:
            assignment = self.assignments_collection.find_one(
                {"_id": assignment_id}  # Query condition
            )
        except Exception as e:
            print(f"USER NOT FOUND: {e}")
            raise HTTPException(status_code=500, detail=f"ASSIGNMENT NOT FOUND: {e}")
        if assignment:
            if existingUser is not None:
                userType = existingUser["type"]
                if userType != "professor":
                    assignment.pop("ai_limitation")
                return JSONResponse(assignment, status_code=200)
            else:
                raise HTTPException(status_code=404, detail=f"User not found: {encodedUserData}")
        else:
            raise HTTPException(status_code=404, detail=f"No assignments posted by professor: {professor_id}")
        
    async def get_joined_students(
        self,
        request: Request,
        authorization: str = Header(None),
    ):
        if authorization is None:
            raise HTTPException(status_code=401, detail="No Authorization Token Received")

        try:
            # Authorize the request
            encodedUserData = await self.authenticator.Authorize(authorization=authorization)
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
            if not existingUser or existingUser["type"] != "professor":
                raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
        
        if existingUser is not None:
            userType = existingUser["type"]
            if userType != "professor":
                raise HTTPException(
                    status_code=400,
                    detail=f"You are not a professor. If you are one, please sign up as a professor.",
                )
        try:
            form_data = await request.form()
            assignment_id = form_data.get("assignment_id")

            if not assignment_id:
                raise HTTPException(status_code=400, detail="assignment_id is required")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error: {e}")

        student_ids = [submission["student_id"] for submission in self.submissions_collection.find({"assignment_id": assignment_id}, {"student_id": 1})]
        students = [self.userCollection.find_one({"_id": str(student_id)}, {"_id": 0, "name": 1, "email": 1}) for student_id in student_ids]

        if not students:
            raise HTTPException(status_code=404, detail="No students have joined this assignment")

        return JSONResponse(students, status_code=200)