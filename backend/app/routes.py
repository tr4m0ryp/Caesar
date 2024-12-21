
import requests
from twilio.rest import Client
from config.settings import (
    TWILIO_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    LINKEDIN_API_KEY,
    TWITTER_API_KEY,
    TELEGRAM_API_KEY
)

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def initiate_contact(company: dict, method: str):
    method = method.lower()
    if method == 'email':
        send_email(company.get('contact'))
    elif method == 'whatsapp':
        send_whatsapp(company.get('contact'))
    elif method == 'call':
        make_call(company.get('contact'))
    elif method in {'contact_form', 'live_chat'}:
        open_contact_form(company.get('live_chat_url') or company.get('contact_form_url'))
    elif method == 'linkedin':
        send_linkedin_message(company.get('linkedin_profile'))
    elif method == 'twitter':
        send_twitter_dm(company.get('twitter_handle'))
    elif method == 'sms':
        send_sms(company.get('phone'))  # Zorg ervoor dat 'phone' beschikbaar is
    elif method == 'telegram':
        send_telegram_message(company.get('telegram_handle'))
    else:
        raise ValueError(f"Onbekende contactmethode: {method}")

def send_email(email: str):
    if not email:
        raise ValueError("Geen e-mailadres beschikbaar.")
    # Implementatie voor het verzenden van een e-mail
    pass

def send_whatsapp(number: str):
    if not number:
        raise ValueError("Geen WhatsApp-nummer beschikbaar.")
    client.messages.create(
        body="Hallo, wij bieden IT-diensten aan die uw bedrijf kunnen helpen...",
        from_='whatsapp:' + TWILIO_PHONE_NUMBER,
        to='whatsapp:' + number
    )

def make_call(number: str):
    if not number:
        raise ValueError("Geen telefoonnummer beschikbaar.")
    client.calls.create(
        url='http://demo.twilio.com/docs/voice.xml',
        from_=TWILIO_PHONE_NUMBER,
        to=number
    )

def open_contact_form(url: str):
    if not url:
        raise ValueError("Geen contactformulier of live chat URL beschikbaar.")
    # Logica om het contactformulier te openen, kan door de frontend worden afgehandeld
    pass

def send_linkedin_message(profile_url: str):
    if not profile_url:
        raise ValueError("Geen LinkedIn profiel URL beschikbaar.")
    # Implementatie voor het sturen van een LinkedIn bericht via de API
    pass

def send_twitter_dm(twitter_handle: str):
    if not twitter_handle:
        raise ValueError("Geen Twitter handle beschikbaar.")
    # Implementatie voor het sturen van een Twitter DM via de API
    pass

def send_sms(number: str):
    if not number:
        raise ValueError("Geen SMS-nummer beschikbaar.")
    client.messages.create(
        body="Hallo, wij bieden IT-diensten aan die uw bedrijf kunnen helpen...",
        from_=TWILIO_PHONE_NUMBER,
        to=number
    )

def send_telegram_message(telegram_handle: str):
    if not telegram_handle:
        raise ValueError("Geen Telegram handle beschikbaar.")
    # Implementatie voor het sturen van een Telegram bericht via de API
    pass
