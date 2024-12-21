import logging
import requests
from twilio.rest import Client
import os

# Setup logging
logger = logging.getLogger(__name__)

# Laden van API-sleutels via Environment Variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialiseren van Twilio Client
twilio_client = None
if TWILIO_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    except Exception as e:
        logger.error(f"Fout bij initialiseren van Twilio Client: {e}")

# LinkedIn, Twitter en Telegram API Keys
LINKEDIN_API_KEY = os.getenv("LINKEDIN_API_KEY")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")

def initiate_contact(company: dict, method: str):
    method = method.lower()
    logger.info(f"Initiëren van contact via {method} voor bedrijf {company.get('name')}")
    
    if method == 'email':
        send_email(company.get('contact'))
    elif method == 'whatsapp':
        send_whatsapp(company.get('contact'))
    elif method == 'call':
        make_call(company.get('contact'))
    elif method == 'sms':
        send_sms(company.get('contact'))
    elif method == 'linkedin':
        send_linkedin_message(company.get('linkedin_profile'))
    elif method == 'twitter':
        send_twitter_dm(company.get('twitter_handle'))
    elif method == 'telegram':
        send_telegram_message(company.get('telegram_handle'))
    elif method in {'contact_form', 'live_chat'}:
        open_contact_form(company.get('live_chat_url') or company.get('contact_form_url'))
    else:
        raise ValueError(f"Onbekende contactmethode: {method}")

def send_email(email: str):
    if not email:
        raise ValueError("Geen e-mailadres beschikbaar.")
    logger.info(f"Verzenden van e-mail naar {email}")
    # Implementatie voor het verzenden van een e-mail

def send_whatsapp(number: str):
    if not number:
        raise ValueError("Geen WhatsApp-nummer beschikbaar.")
    if not twilio_client:
        raise ValueError("Twilio Client is niet geïnitialiseerd.")
    
    try:
        message = twilio_client.messages.create(
            body="Hallo, wij bieden IT-diensten aan die uw bedrijf kunnen helpen...",
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
            to=f'whatsapp:{number}'
        )
        logger.info(f"WhatsApp-bericht verzonden naar {number}: SID {message.sid}")
    except Exception as e:
        logger.error(f"Fout bij verzenden van WhatsApp-bericht naar {number}: {e}")
        raise

def make_call(number: str):
    if not number:
        raise ValueError("Geen telefoonnummer beschikbaar.")
    if not twilio_client:
        raise ValueError("Twilio Client is niet geïnitialiseerd.")
    
    try:
        call = twilio_client.calls.create(
            url='http://demo.twilio.com/docs/voice.xml',
            from_=TWILIO_PHONE_NUMBER,
            to=number
        )
        logger.info(f"Telefoongesprek gestart naar {number}: Call SID {call.sid}")
    except Exception as e:
        logger.error(f"Fout bij maken van telefoongesprek naar {number}: {e}")
        raise

def send_sms(number: str):
    if not number:
        raise ValueError("Geen SMS-nummer beschikbaar.")
    if not twilio_client:
        raise ValueError("Twilio Client is niet geïnitialiseerd.")
    
    try:
        message = twilio_client.messages.create(
            body="Hallo, wij bieden IT-diensten aan die uw bedrijf kunnen helpen...",
            from_=TWILIO_PHONE_NUMBER,
            to=number
        )
        logger.info(f"SMS verzonden naar {number}: SID {message.sid}")
    except Exception as e:
        logger.error(f"Fout bij verzenden van SMS naar {number}: {e}")
        raise

def send_linkedin_message(profile_url: str):
    if not profile_url:
        raise ValueError("Geen LinkedIn profiel URL beschikbaar.")
    logger.info(f"Sturen van LinkedIn-bericht naar {profile_url}")
    # Implementatie voor het sturen van een LinkedIn-bericht

def send_twitter_dm(twitter_handle: str):
    if not twitter_handle:
        raise ValueError("Geen Twitter handle beschikbaar.")
    logger.info(f"Sturen van Twitter DM naar @{twitter_handle}")
    # Implementatie voor het sturen van een Twitter DM

def send_telegram_message(telegram_handle: str):
    if not telegram_handle:
        raise ValueError("Geen Telegram handle beschikbaar.")
    logger.info(f"Sturen van Telegram-bericht naar {telegram_handle}")
    # Implementatie voor het sturen van een Telegram-bericht

def open_contact_form(url: str):
    if not url:
        raise ValueError("Geen contactformulier of live chat URL beschikbaar.")
    logger.info(f"Openen van contactformulier of live chat via {url}")
    # Logica om de URL terug te sturen naar de frontend
