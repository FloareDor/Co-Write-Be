from fastapi import HTTPException, Header, Request, File, UploadFile
import shutil
from fastapi.responses import JSONResponse
from bson import ObjectId
import re
import json
from schemas.assignment import assignmentSchema
from schemas.submission import submissionSchema
from schemas.user import userSchema

from pydantic import ValidationError

from utils.authenticator import Authenticator

class StudentHandler:
	def __init__(self, db):
		self.db = db
		self.userCollection = db["users"]
		self.assignments_collection = db["assignments"]
		self.submissions_collection = db["submissions"]  # New collection for submissions
		self.authenticator = Authenticator(db)

	async def submit_assignment(self, request: Request, authorization: str = Header(None)):
		if authorization is None:
			raise HTTPException(status_code=500, detail="No Authorization Token Received")
		try:
			# Authorize the request
			encodedUserData = await self.authenticator.Authorize(authorization=authorization)
			print(encodedUserData)
			
		except HTTPException as http_exception:
			# Handle authorization errors
			return JSONResponse({"detail": f"Authorization error: {http_exception.detail}"}, status_code=http_exception.status_code)
		try:
			existingUser = self.userCollection.find_one(
				{"sub": encodedUserData["sub"]},  # Query condition
			)
		except Exception as e:
			print(f"USER NOT FOUND: {e}")
			raise HTTPException(status_code=500, detail=f"USER NOT FOUND: {encodedUserData}")
		if existingUser is not None:
			userType = existingUser["type"]
			if userType != "professor":
				raise HTTPException(status_code=400, detail=f"You are not a student. Please sign up as a student.")

		try:
			data_bytes = await request.body()
			data_str = data_bytes.decode('utf-8')
			data = json.loads(data_str, strict=False)
			
			student_id = encodedUserData["_id"]
			submission_id = str(ObjectId())
			submission_data = {
					"_id": submission_id,
					"student_id": str(student_id),
					"assignment_id": data["assignment_id"],
					"submission_text": data["submission_text"],
					"submission_file": data["submission_file"]
			}

			# Validate the submission data using the Pydantic schema
			submission_schema = submissionSchema(**submission_data)

			# Insert the submission into the database
			result = self.submissions_collection.insert_one(submission_data)

			# Check if the insertion was successful
			if result.acknowledged:
				return JSONResponse({"message": "Submission added successfully", "submission_id": submission_id}, status_code=200)
			else:
				return {"message": "Failed to add submission"}

		except ValidationError as e:
			# Handle validation errors
			return {"message": "Invalid submission data", "errors": e.errors()}

		except Exception as e:
			return {"message": "An error occurred", "error": str(e)}
