import os
from dotenv import load_dotenv

load_dotenv()


TOKEN=os.getenv("TOKEN_REP_TELEGRAM", "")
DB=os.getenv("DB_REP_TELEGRAM", "")
ENGINE=os.getenv("ENGINE_REP_TELEGRAM","")
