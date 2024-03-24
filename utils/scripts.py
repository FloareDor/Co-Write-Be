
from pymongo import MongoClient
import json
from bson import ObjectId
import pandas as pd

from os import environ as env

# def insertSampleData(filename, db):
# 	professor_collection = db["professors"]
# 	with open(filename, "r") as json_file:
# 		data = json.load(json_file)
# 	for prof in data:
# 		# Insert the document into the professor_collection
# 		prof["_id"] = ObjectId(prof["_id"])
# 		prof["rating"] = 5
# 		prof["teachingQuality"] = 5
# 		prof["userRatings"] = []
# 		prof["totRatings"] = 0
# 		prof["helpfulness"] = 5
# 		prof["courseQuality"] = 5
# 		prof["responsiveness"] = 5
# 		insert_result = professor_collection.insert_one(prof)
# 		# Check if the insertion was successful
# 		if insert_result.acknowledged:
# 			# print("Document inserted successfully!")
# 			for doc in professor_collection.find():
# 				# Convert the ObjectId to string representation before printing
# 				doc["_id"] = str(doc["_id"])
# 				# print(doc)
# 		else:
# 			print("Failed to insert the document.")

# 	print("Document inserted successfully!")

# def insertSampleData(file_path, db):
# 	df = pd.read_csv(file_path)
# 	df = df.fillna('')

# 	def convert_to_schema(df):
# 		restaurants = {}
# 		for index, row in df.iterrows():
# 			print(index,row)
# 			item = {
				
# 				"name": str(row['item_name']).lower(),
# 				"description": str(row['item_description']).lower(),
# 				"cals": row['calories'],
# 				"carbs": row['carbs'],
# 				"fat": row['fat'],
# 				"protein": row['protein']
# 			}
# 			if row['restaurant'] in restaurants:
# 				restaurants[row['restaurant']]['items'].append(item)
# 			else:
# 				restaurants[row['restaurant']] = {
# 					"_id": str(row['_id']),
# 					"name": str(row['restaurant']).lower(),
# 					"location": row['location'],
# 					"logo": row['logo'],
# 					"items": [item]
# 				}
# 				print(str(row['_id']))
		
# 		return list(restaurants.values())

# 	converted_data = convert_to_schema(df)
# 	collection = db["restaurants"]
# 	collection.insert_many(converted_data)

def initDB():
	ATLAS_URL = env.get("ATLAS_URL")
	# LOCAL_DB = env.get("LOCAL_DB")
	client = MongoClient(ATLAS_URL)
	db = client["healthmymenu"]

	# restaurant collection
	professor_collection = db["professors"]
	# professor_collection.delete_many({})

	assgn_collection = db["assignments"]
	# assgn_collection.delete_many({})

	# User collection
	user_collection = db["users"]
	# user_collection.delete_many({})

	# items collection
	students_collection = db["students"]
	# students_collection.delete_many({})

	return db

