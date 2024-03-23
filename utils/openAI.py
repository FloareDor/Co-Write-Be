from openai import OpenAI
import os
from os import environ as env
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:	
	load_dotenv(ENV_FILE)

class GPT:
	def __init__(self):
		self.client = OpenAI(api_key=env.get('OPENAI_API_KEY'))

	def chat(self, prompt):
		print("chat init")
		final_string = ""
		stream = self.client.chat.completions.create(
			model="gpt-3.5-turbo",
			messages=[{"role": "user", "content": prompt}],
			stream=True,
		)
		print("chat init 2")
		for chunk in stream:
			final_string += chunk.choices[0].delta.content or ""

		return final_string
	
	def healthifyMenu(self, userPrompt, restaurant, items, location, dailycalgoal, dailycarbgoal, dailyfatgoal, dailyproteingoal):
		prompt = f'''
		Given a list of menu items from various restaurants, each with its calorie content and a brief description, identify the three best options that meet the following criteria:
		I'm feeling {userPrompt}
		The daily total calorie intake goal is "{dailycalgoal} calories"
		The daily total carbohydrate intake goal is {dailycarbgoal} grams.
		The daily total fat intake goal is {dailyfatgoal} grams.
		The daily total protein intake goal is {dailyproteingoal} grams. 
		The description of each recommended item should be concise, ideally less than 10 words.
		The selection should aim for a balance across different types of food while maximizing the variety and nutritional value., ideally less than 10 words

		Consider the following data for menu items from {restaurant} in {location}:

		{items}

		recommend me the three best menu options that fulfill the criteria mentioned above, ensuring the total does not exceed the daily calorie goal.
		Please Don't start with a basic sentence, keep the language slightly funny but safe. 
		Please Don't start with a basic sentence, keep the language slightly entertaining but safe. 
		Please Don't start with a basic sentence, keep the language slightly funny but safe.
		Don't mention that you're an AI, you're Gator My Menu
		Don't mention that you're an AI, you're Gator My Menu
		Don't mention that you're an AI, you're Gator My Menu
		'''
		print(prompt)
		return self.chat(prompt)



    
    
# print(generate_quote({"title": "play games", "description": "play more games"}))