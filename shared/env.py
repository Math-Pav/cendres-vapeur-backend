import os
from dotenv import load_dotenv

# Charge les variables du fichier .env situé à la racine du projet
load_dotenv()

class Env:
   
    # --- Configuration SMTP (Bureau de Poste) ---
    SMTP_SERVER = os.getenv("SMTP_SERVER", "sandbox.smtp.mailtrap.io")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 2525))
    SMTP_USER_ID = os.getenv("VOTRE_USER_ID")
    SMTP_PASSWORD = os.getenv("VOTRE_PASSWORD")