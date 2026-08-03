import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")

ADMIN_IDS = [
    1555474257,
]

DEFAULT_TRIAL_DAYS = 10