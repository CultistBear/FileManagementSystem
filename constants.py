import pathlib
import os
#from cryptography.fernet import Fernet
#Fernet.generate_key()
FLASK_SECRET_KEY = os.environ['FLASK_SECRET']
DB_USERNAME = os.environ['MYSQL_USER']
DB_PASSWORD = os.environ['MYSQL_PASS']
DATABASE_NAME = os.environ['FMS_DB']
PASSWORD_SALT = os.environ['FMS_SALT']
FILE_NAME_KEY = str.encode(os.environ["FILE_NAME_KEY"])
FILE_SHARE_KEY = str.encode(os.environ["FILE_SHARE_KEY"])
CURRENT_WORKING_DIRECTORY = pathlib.Path(__file__).parent.resolve()
TIME_OF_DAY=['Night','Morning','Afternoon','Evening']