import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_REP_TELEGRAM", "")
DB = os.getenv("DB_REP_TELEGRAM", "")
CREATOR = os.getenv("CREATOR_ID_REP_TELEGRAM", "")
