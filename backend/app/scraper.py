# ai-contact-finder/backend/app/scraper.py

import os
import time
import json
import logging
import requests
import googlemaps
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as config_file:
            config = json.load(config_file)
        logger.info("Configuratie succesvol geladen.")
        return config
    except FileNotFoundError:
        logger.error(f"Configuratiebestand niet gevonden: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Fout bij het parsen van configuratiebestand: {e}")
        return {}

# Laden van configuratie bij module import
CONFIG = load_config()

def call_gemini_api(prompt: str, retries: int = 3, backoff: int = 5) -> str:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    gemini_endpoint = os.getenv("GEMINI_ENDPOINT", "https://api.gemini.example.com/v1/generate")

    if not gemini_api_key:
        logger.error("Geen Gemini API-sleutel gevonden. Stel de 'GEMINI_API_KEY' omgevingsvariabele in.")
        return "{}"

    headers = {
        "Authorization": f"Bearer {gemini_api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "model": "gemini-1.5-pro",
        "max_tokens": 150
    }

    for attempt in range(retries):
        try:
            response = requests.post(gemini_endpoint, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout bij poging {attempt + 1} van {retries}. Opnieuw proberen in {backoff} seconden...")
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response and e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", backoff))
                logger.warning(f"Rate limit bereikt. Wachten {retry_after} seconden...")
                time.sleep(retry_after)
            else:
                logger.error(f"RequestException: {e}. Poging {attempt + 1} van {retries}.")
        time.sleep(backoff)

    logger.error("Alle pogingen om de Gemini API te bereiken zijn mislukt.")
    return "{}"

def parse_user_input(user_input: str) -> dict:
    try:
        full_prompt = (
            f"Ontleed de volgende tekst:\n"
            f"\"{user_input}\"\n"
            "Formatteer als JSON:\n"
            "{\n"
            "  \"city\": \"...\",\n"
            "  \"industry\": \"...\",\n"
            "  \"area\": \"...\"\n"
            "}"
        )
        response = call_gemini_api(full_prompt)
        data = json.loads(response)
        return {
            "city": data.get("city", "onbekend"),
            "industry": data.get("industry", "onbekend"),
            "area": data.get("area", "onbekend")
        }
    except Exception as e:
        logger.error(f"Fout bij parse_user_input: {e}")
        return {"city": "onbekend", "industry": "onbekend", "area": "onbekend"}

@lru_cache(maxsize=100)
def geocode_city(city: str, api_key: str) -> dict:
    gmaps_client = googlemaps.Client(key=api_key)
    try:
        geocode_result = gmaps_client.geocode(city)
        if not geocode_result:
            return None
        return geocode_result[0]["geometry"]["location"]
    except Exception as e:
        logger.error(f"Fout bij geocoding: {e}")
        return None

def scrape_google_places(city: str, industry: str, api_key: str, radius: int = 5000) -> list:
    if not api_key:
        logger.warning("Geen Google Places API key.")
        return []
    location = geocode_city(city, api_key)
    if not location:
        logger.error(f"Geocoding mislukt voor stad: {city}")
        return []

    latlng = (location["lat"], location["lng"])

    results = []
    gmaps_client = googlemaps.Client(key=api_key)

    try:
        logger.info(f"Zoeken naar plaatsen: {industry} in {city}")
        places_response = gmaps_client.places_nearby(
            location=latlng, radius=radius, keyword=industry
        )
    except Exception as e:
        logger.error(f"Fout bij places_nearby: {e}")
        return []

    while True:
        for place in places_response.get("results", []):
            place_id = place.get("place_id")
            name = place.get("name")
            address = place.get("vicinity")
            rating = place.get("rating", None)
            try:
                details = gmaps_client.place(place_id=place_id).get("result", {})
                phone = details.get("formatted_phone_number")
                website = details.get("website")
            except Exception as e:
                logger.error(f"Fout bij het ophalen van details voor '{name}': {e}")
                phone, website = None, None

            results.append({
                "name": name,
                "address": address,
                "rating": rating,
                "phone": phone,
                "website": website,
                "place_id": place_id
            })

        next_token = places_response.get("next_page_token")
        if not next_token:
            break
        logger.info("Ophalen van volgende pagina resultaten...")
        time.sleep(2)  # Wachten op de volgende pagina token

        try:
            places_response = gmaps_client.places_nearby(
                location=latlng,
                radius=radius,
                keyword=industry,
                page_token=next_token
            )
        except Exception as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", 60))
                logger.warning(f"Rate limit bereikt. Wachten {retry_after} seconden...")
                time.sleep(retry_after)
            else:
                logger.error(f"Fout bij volgende pagina: {e}")
            break
    return results

def scrape_website(url: str) -> dict:
    if not url:
        return {
            "contact_form_url": None,
            "linkedin_profile": None,
            "twitter_handle": None,
            "telegram_handle": None,
            "live_chat_url": None
        }
    try:
        logger.info(f"Scrapen van website: {url}")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        data = {
            "contact_form_url": None,
            "linkedin_profile": None,
            "twitter_handle": None,
            "telegram_handle": None,
            "live_chat_url": None
        }
        for link in soup.find_all("a", href=True):
            href = link["href"]
            lower_href = href.lower()
            text_lower = (link.text or "").lower()

            if "contact" in lower_href and ("form" in lower_href or "contact" in text_lower):
                data["contact_form_url"] = urljoin(url, href)
            if "linkedin.com" in lower_href:
                data["linkedin_profile"] = urljoin(url, href)
            if "twitter.com" in lower_href:
                data["twitter_handle"] = urljoin(url, href)
            if "t.me" in lower_href or "telegram.me" in lower_href:
                data["telegram_handle"] = urljoin(url, href)
            if "livechat" in lower_href or "live-chat" in lower_href:
                data["live_chat_url"] = urljoin(url, href)

        return data
    except Exception as e:
        logger.error(f"Fout bij het scrapen van {url}: {e}")
        return {
            "contact_form_url": None,
            "linkedin_profile": None,
            "twitter_handle": None,
            "telegram_handle": None,
            "live_chat_url": None
        }

def google_search(query: str, num_pages: int = 1) -> list:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7"
    })
    results = []
    for page in range(num_pages):
        params = {"q": query, "start": page * 10}
        try:
            logger.info(f"Google zoeken: {query}, pagina {page + 1}")
            r = session.get("https://www.google.com/search", params=params, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for g in soup.select("div.g"):
                link = g.select_one("a")
                if link:
                    url = link.get("href")
                    if url and url.startswith("http"):
                        results.append(url)
        except Exception as e:
            logger.error(f"Fout bij Google Search (pagina {page+1}): {e}")
            break
    return results

def find_extras_by_search(name: str, field: str) -> str:
    query = f"{name} {field}"
    links = google_search(query, num_pages=1)
    for link in links:
        if field in link.lower():
            return link
    return None

def scrape_companies(city: str, industry: str, company_types: list, areas: list, google_api_key: str) -> list:
    # Scrape bedrijven via Google Places API
    places_data = scrape_google_places(city, industry, google_api_key)
    final_data = []
    for place in places_data:
        website_data = scrape_website(place.get("website"))
        # Zoek naar ontbrekende gegevens via Google Search
        missing = {}
        if not website_data.get("linkedin_profile"):
            found = find_extras_by_search(place.get("name"), "linkedin")
            missing["linkedin_profile"] = found
        if not website_data.get("twitter_handle"):
            found = find_extras_by_search(place.get("name"), "twitter")
            missing["twitter_handle"] = found
        if not website_data.get("telegram_handle"):
            found = find_extras_by_search(place.get("name"), "telegram")
            missing["telegram_handle"] = found
        if not website_data.get("live_chat_url"):
            found = find_extras_by_search(place.get("name"), "live chat")
            missing["live_chat_url"] = found

        # Combineer de gegevens
        combined = {**place, **website_data, **missing}
        final_data.append(combined)
    return final_data

def scrape_companies_wrapper(city: str, industry: str, company_types: list, areas: list) -> list:
    google_api_key = os.getenv("GOOGLE_API_KEY")
    return scrape_companies(city, industry, company_types, areas, google_api_key)
