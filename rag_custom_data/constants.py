from os import environ as env
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:	
	load_dotenv(ENV_FILE)


OPENAI_API_KEY = env.get('OPENAI_API_KEY')