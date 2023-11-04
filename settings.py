import os
from os.path import join, dirname
from dotenv import load_dotenv

# Load .env file
dotenv_path = join(dirname(__file__), 'vars.env')
load_dotenv(dotenv_path)

# ENVEIRONMENT VARIABLES
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
SECRET_KEY=os.environ.get('SECRET_KEY')