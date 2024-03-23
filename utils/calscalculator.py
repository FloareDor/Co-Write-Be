
from pydantic import BaseModel
from models.schemas import UserSchema


def calculate_bmr(sex, weight, height, age):
    if sex.lower() in ["female", "f"]:
        bmr = (weight * 10) + (height * 6.25) - (age * 5) - 161
    else:
        bmr = (weight * 10) + (height * 6.25) - (age * 5) + 5
    return int(bmr)

def calculate_total_calories(bmr, activity_level):
    activity_multipliers = {
        0: 1.25, # sedentary
        1: 1.375, # light
        2: 1.550, # moderate
        3: 1.725 # active
    }
    return bmr * activity_multipliers[activity_level]

def calculate_calories(user_input: UserSchema):
    bmr = calculate_bmr(str(user_input["gender"]), float(user_input["weight"]), float(user_input["height"]), int(user_input["age"]))
    dailycalgoal = calculate_total_calories(bmr, int(user_input["activeness"]))
    
    return dailycalgoal