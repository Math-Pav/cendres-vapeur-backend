import os
from dotenv import load_dotenv

load_dotenv()

class Env:
   
    SMTP_SERVER = os.getenv("SMTP_SERVER", "sandbox.smtp.mailtrap.io")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 2525))
    SMTP_USER_ID = os.getenv("VOTRE_USER_ID")
    SMTP_PASSWORD = os.getenv("VOTRE_PASSWORD")