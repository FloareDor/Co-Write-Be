from fastapi import HTTPException, Header, Request
from fastapi.responses import JSONResponse
from bson import ObjectId
import re
import json
from schemas.assignment import assignmentSchema
from schemas.submission import submissionSchema
from schemas.user import userSchema

from pydantic import ValidationError

from utils.authenticator import Authenticator

class ProfessorHandler:
	def __init__(self, db):
		self.db = db
		self.userCollection = db["users"]
		self.professor_collection = db["professor"]
		self.assignments_collection = db["assignments"]
		self.authenticator = Authenticator(db)

	async def add_new_assignment(self, request: Request, authorization: str = Header(None)):
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
				raise HTTPException(status_code=400, detail=f"You are not a professor. If you are one, please sign up as a professor.")

			

		try:
			data_bytes = await request.body()
			data_str = data_bytes.decode('utf-8')
			data = json.loads(data_str, strict=False)
			assignment_id = str(ObjectId())
			assignment_data = {
					"_id": assignment_id,
					"professor_id": str(encodedUserData["_id"]),
					"title": data["title"],
					"description": data["description"],
					"ai_limitation": data["ai_limitation"],
					"resource": data["resource"]
			}
			# Validate the assignment data using the Pydantic schema
			assignment_schema = assignmentSchema(**assignment_data)

			# Insert the assignment into the database
			result = self.assignments_collection.insert_one(assignment_data)

			# Check if the insertion was successful
			if result.acknowledged:
				return JSONResponse({"message": "Assignment added successfully", "assignment_id": assignment_id},status_code=200)
			else:
				return {"message": "Failed to add assignment"}

		except ValidationError as e:
			# Handle validation errors
			return {"message": "Invalid assignment data", "errors": e.errors()}

		except Exception as e:
			return {"message": "An error occurred", "error": str(e)}

	# async def get_all_professors(self, request: Request):
	# 	professors = []
	# 	projection = {"items": 0}
	# 	for professor in self.professor_collection.find(projection=projection).sort("name"):
	# 		professor["_id"] = str(professor["_id"])
	# 		professors.append(professor)
	# 	if professor:
	# 		return JSONResponse(professors, status_code=200)
	# 	else:
	# 		raise HTTPException(status_code=404, detail="No professors found")
		
	# async def search_professors(self, request: Request, query: str):
	# 	try:
	# 		search_query = str(query).lower()
	# 	except KeyError:
	# 		raise HTTPException(status_code=400, detail="Missing or invalid 'query' parameter")

	# 	filtered_professors = []
	# 	projection = {"items": 0}
	# 	# a regex pattern to match occurrences of the query anywhere within the name field
	# 	regex_pattern = {"$regex": search_query, "$options": "i"}  # Case insensitive match
	# 	query_filter = {"name": regex_pattern}
		
	# 	for professor in self.professor_collection.find(query_filter, projection=projection).sort("name"):
	# 		professor["_id"] = str(professor["_id"])
	# 		filtered_professors.append(professor)

	# 	if filtered_professors:
	# 		return JSONResponse(filtered_professors, status_code=200)
	# 	else:
	# 		raise HTTPException(status_code=404, detail="No professors found")

		
	

