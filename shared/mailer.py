import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from email.mime.text import MIMEText
from shared.env import Env

def send_2fa_code_email(email, code, username):
    """
    Envoie le code 2FA par email
    
    Pour développement: Affiche le code en console
    Pour production: Configurer EMAIL_HOST, EMAIL_PORT dans settings.py
    """
    
    sender_email = getattr(settings, 'EMAIL_HOST_USER', None)
    sender_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
    smtp_server = getattr(settings, 'EMAIL_HOST', None)
    smtp_port = getattr(settings, 'EMAIL_PORT', 587)
    
    if not sender_email or not smtp_server:
        print(f"\n{'='*60}")
        print(f"📧 CODE 2FA SIMULÉ (email non configuré)")
        print(f"{'='*60}")
        print(f"Pour: {username} ({email})")
        print(f"Code:  {code}")
        print(f"Valide pour: 10 minutes")
        print(f"{'='*60}\n")
        return True
    
    try:
        subject = "Votre code de vérification 2FA"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Authentification à deux facteurs</h2>
                <p>Bonjour {username},</p>
                <p>Voici votre code de vérification (valable 10 minutes):</p>
                <h1 style="color: #007bff; letter-spacing: 5px;">{code}</h1>
                <p>Ne partage pas ce code avec quiconque.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Si vous n'avez pas demandé cette vérification, ignorez ce message.
                </p>
            </body>
        </html>
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email
        
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        
        print(f"✅ Email 2FA envoyé à {email}")
        return True
    
    except Exception as e:
        print(f"⚠️ Impossible d'envoyer l'email: {str(e)}")
        print(f"Code de secours: {code}")
        return False

def send_welcome_email(email, username):
    """Envoie un email de bienvenue après inscription"""
    try:
        subject = "Bienvenue sur notre plateforme"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Bienvenue {username}!</h2>
                <p>Merci de vous être inscrit sur notre plateforme.</p>
                <p>Vous pouvez maintenant vous connecter avec votre email et votre mot de passe.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                    Questions? Contactez notre support.
                </p>
            </body>
        </html>
        """
        
        sender_email = settings.EMAIL_HOST_USER or "noreply@exemple.com"
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email
        
        part = MIMEText(html_content, "html")
        message.attach(part)
        
        print(f"📧 Email de bienvenue simulé pour {email}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du welcome email: {str(e)}")
        return False

def send_payment_confirmation_email(email, username, order_id, total_amount, transaction_id):
    """Envoie un simple email de confirmation de paiement"""
    sender_email = getattr(settings, 'EMAIL_HOST_USER', None)
    
    if not sender_email:
        print(f"\n{'='*50}")
        print(f"✅ CONFIRMATION DE PAIEMENT")
        print(f"{'='*50}")
        print(f"À: {username} ({email})")
        print(f"Commande: CMD-{order_id:05d}")
        print(f"Montant: {total_amount}€")
        print(f"Transaction: {transaction_id}")
        print(f"{'='*50}\n")
        return True
    
    try:
        subject = f"Commande confirmée - Numéro CMD-{order_id:05d}"
        html_content = f"""
        <html>
            <body style="font-family: Arial; color: #333;">
                <h2 style="color: #28a745;">✓ Paiement approuvé</h2>
                <p>Bonjour {username},</p>
                <p>Votre commande a été payée avec succès!</p>
                <br>
                <p><strong>Numéro de commande:</strong> CMD-{order_id:05d}</p>
                <p><strong>Montant:</strong> {total_amount}€</p>
                <p><strong>Transaction:</strong> {transaction_id}</p>
                <br>
                <p>Vous recevrez bientôt les détails de livraison.</p>
            </body>
        </html>
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = email
        message.attach(MIMEText(html_content, "html"))
        
        sender_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        smtp_server = getattr(settings, 'EMAIL_HOST', None)
        smtp_port = getattr(settings, 'EMAIL_PORT', 587)
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        
        print(f"✅ Email de paiement envoyé à {email}")
        return True
    except Exception as e:
        print(f"⚠️ Erreur email: {str(e)}")
        return False

class Missive(BaseModel):
    expediteur: EmailStr
    sujet: str
    message: str

SMTP_SERVER = Env.SMTP_SERVER
SMTP_PORT = Env.SMTP_PORT
SMTP_USER = Env.SMTP_USER_ID
SMTP_PASSWORD = Env.SMTP_PASSWORD

async def envoyer_missive(missive: Missive):
    try:
        corps_mail = f"""
        --- MESSAGE REÇU DU SECTEUR EXTERNE ---
        Expéditeur : {missive.expediteur}
        Sujet : {missive.sujet}
        
        Message :
        {missive.message}
        ---------------------------------------
        """
        
        msg = MIMEMultipart()
        msg['From'] = missive.expediteur
        msg['To'] = "administrateur@zonefranche.col"
        msg['Subject'] = f"[URGENT] {missive.sujet}"
        msg.attach(MIMEText(corps_mail, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {"status": "success", "message": "La missive a été transmise au Grand Conseil."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Échec de la transmission : {str(e)}")