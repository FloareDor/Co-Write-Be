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

	async def open_assignment(self, request: Request, authorization: str = Header(None)):

		print("000")
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
		try:
			print("111")
			form_data = await request.form()
			assignment_id = form_data.get("assignment_id")
			print("121")

			if not all([assignment_id]):
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
			print("131")
			form_data = await request.form()
			assignment_id = form_data.get("assignment_id")
			student_id = encodedUserData["_id"]
			print("141")
			existing_submission = self.submissions_collection.find_one({
						"assignment_id": assignment_id,
						"student_id": str(student_id)
					})
			print("151")
			if existing_submission:
				return JSONResponse(
					{"message": "Submission already exists for this assignment and student"},
					status_code=400
				)
			print("161")
			submission_id = str(ObjectId())
			submission_data = {
					"_id": submission_id,
					"student_id": str(student_id),
					"assignment_id": assignment_id,
					"submission_text": None,
					"submission_file": None,
					"active": True,	
			}
			print("22222222")
			# Validate the submission data using the Pydantic schema
			submission_schema = submissionSchema(**submission_data)
			print("3333")
			# Insert the submission into the database
			result = self.submissions_collection.insert_one(submission_data)
			
			# Check if the insertion was successful
			if not result.acknowledged:
			# 	return JSONResponse({"message": "Opened Assignment successfully", "submission_id": submission_id}, status_code=200)
			# else:
				return {"message": "Failed to add submission"}

		except ValidationError as e:
			# Handle validation errors
			return {"message": "Invalid submission data", "errors": e.errors()}

		try:
			existingAssignment = self.assignments_collection.find_one(
							{"_id": assignment_id},  # Query condition
						)
			print("4444")
			# Check if the insertion was successful
			if existingAssignment:
				existingAssignment.pop("ai_limitation")
				print("555")
				return JSONResponse(
					{"message": "Assignment Joined Successfully", "assignment_details": existingAssignment},
					status_code=200,
				)
				
			else:
				raise HTTPException(status_code=400, detail=f"Invalid assignment code: {e.errors()}")
		except ValidationError as e:
			# Handle validation errors
			raise HTTPException(status_code=400, detail=f"Invalid assignment code: {e.errors()}")

		except Exception as e:
			raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")


	async def submit_assignment(self, request: Request, authorization: str = Header(None)):
		if authorization is None:
			raise HTTPException(status_code=500, detail="No Authorization Token Received")

		try:
			# Authorize the request
			encodedUserData = await self.authenticator.Authorize(authorization=authorization)

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
			form_data = await request.form()
			assignment_id = form_data.get("assignment_id")
			submission_text = form_data.get("submission_text")
			submission_file = form_data.get("submission_file")
			student_id = encodedUserData["_id"]

			# Check if a submission with the given student_id and assignment_id already exists
			existing_submission = self.submissions_collection.find_one({
				"student_id": str(student_id),
				"assignment_id": assignment_id
			})

			if existing_submission:
				# Update the existing submission
				submission_id = existing_submission["_id"]
				update_result = self.submissions_collection.update_one(
					{"_id": submission_id},
					{"$set": {
						"submission_text": submission_text,
						"submission_file": submission_file,
						"active": False
					}}
				)
				if update_result.modified_count > 0:
					return JSONResponse({"message": "Submission updated successfully", "submission_id": str(submission_id)}, status_code=200)
				else:
					return {"message": "Failed to update submission"}
			else:
				# Create a new submission
				submission_id = str(ObjectId())
				submission_data = {
					"_id": submission_id,
					"student_id": str(student_id),
					"assignment_id": assignment_id,
					"submission_text": submission_text,
					"submission_file": submission_file,
					"active": False,
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
		
	async def get_submissions_by_student(
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
		
		submissions = []
		assignments = []

		student_id = encodedUserData["_id"]
		for submission in self.submissions_collection.find({"student_id": re.compile(student_id, re.IGNORECASE)}).sort("_id"):
			# Convert the ObjectId to string representation before returning
			submission["_id"] = str(submission["_id"])
			assignment = self.assignments_collection.find_one(
				{"_id": submission["assignment_id"]}  # Query condition
			)
			assignment["active"] = submission["active"]
			assignments.append(assignment)
			submissions.append(submission)
		
		if assignments:
			response = JSONResponse(assignments, status_code=200)
			return response
		else:
			raise HTTPException(status_code=404, detail=f"No assignments for you: {student_id}")
