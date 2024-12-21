import os
import json

# Pad naar secrets.json
SECRETS_FILE = os.path.join(os.path.dirname(__file__), 'secrets.json')

def load_secrets():
    try:
        with open(SECRETS_FILE, 'r') as f:
            secrets = json.load(f)
        return secrets
    except FileNotFoundError:
        raise Exception(f"Configuratiebestand niet gevonden: {SECRETS_FILE}")
    except json.JSONDecodeError as e:
        raise Exception(f"Fout bij het parsen van configuratiebestand: {e}")

# Laden van secrets
SECRETS = load_secrets()

# Toegang tot de API-sleutels en andere gevoelige gegevens
TWILIO_SID = SECRETS.get("TWILIO_SID")
TWILIO_AUTH_TOKEN = SECRETS.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = SECRETS.get("TWILIO_PHONE_NUMBER")
LINKEDIN_API_KEY = SECRETS.get("LINKEDIN_API_KEY")
TWITTER_API_KEY = SECRETS.get("TWITTER_API_KEY")
TELEGRAM_API_KEY = SECRETS.get("TELEGRAM_API_KEY")
