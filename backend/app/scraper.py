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

def call_gemini_api(prompt, retries=3, backoff=5):
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

def parse_user_input(user_input):
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
def geocode_city(city, api_key):
    gmaps_client = googlemaps.Client(key=api_key)
    try:
        geocode_result = gmaps_client.geocode(city)
        if not geocode_result:
            return None
        return geocode_result[0]["geometry"]["location"]
    except Exception as e:
        logger.error(f"Fout bij geocoding: {e}")
        return None

def scrape_google_places(city, industry, api_key, radius=5000):
    if not api_key:
        logger.warning("Geen Google Places API key.")
        return []
    location = geocode_city(city, api_key)
    if not location:
        logger.error(f"Geocoding mislukt voor stad: {city}")
        return []

    latlng = (location["lat"], location["lng"])

    results = []
    try:
        gmaps_client = googlemaps.Client(key=api_key)
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
            rating = place.get("rating") or float('nan')
            try:
                details = gmaps_client.place(place_id=place_id).get("result", {})
                phone = details.get("formatted_phone_number") or float('nan')
                website = details.get("website") or float('nan')
            except Exception as e:
                logger.error(f"Fout bij het ophalen van details voor '{name}': {e}")
                phone, website = float('nan'), float('nan')

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

def scrape_website(url):
    if not url:
        return {
            "contact_form_url": float('nan'),
            "linkedin_profile": float('nan'),
            "twitter_handle": float('nan'),
            "telegram_handle": float('nan'),
            "live_chat_url": float('nan')
        }
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        data = {
            "contact_form_url": float('nan'),
            "linkedin_profile": float('nan'),
            "twitter_handle": float('nan'),
            "telegram_handle": float('nan'),
            "live_chat_url": float('nan')
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
            "contact_form_url": float('nan'),
            "linkedin_profile": float('nan'),
            "twitter_handle": float('nan'),
            "telegram_handle": float('nan'),
            "live_chat_url": float('nan')
        }

def google_search(query, num_pages=1):
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

def find_extras_by_search(name, field):
    query = f"{name} {field}"
    links = google_search(query, num_pages=1)
    for link in links:
        if field in link.lower():
            return link
    return float('nan')

def hybrid_scraper(user_input, google_api_key, scrape_search=True):
    parsed = parse_user_input(user_input)
    city = parsed["city"]
    industry = parsed["industry"]
    places_data = scrape_google_places(city, industry, google_api_key)
    final_data = []
    for place in places_data:
        website_data = scrape_website(place.get("website"))
        missing = {}
        for key, val in website_data.items():
            if not val:
                if key == "linkedin_profile":
                    found = find_extras_by_search(place["name"], "linkedin")
                    missing[key] = found if found else float('nan')
                if key == "twitter_handle":
                    found = find_extras_by_search(place["name"], "twitter")
                    missing[key] = found if found else float('nan')
                if key == "telegram_handle":
                    found = find_extras_by_search(place["name"], "telegram")
                    missing[key] = found if found else float('nan')
        combined = {**place, **website_data, **missing}
        final_data.append(combined)
    return {
        "parsed_input": parsed,
        "results": final_data
    }

def scrape_companies(city, industry, company_types, areas, google_api_key):
    """
    Scrapes company information based on the provided search criteria.

    Args:
        city (str): De stad waarin gezocht wordt.
        industry (str): De branche waarin gezocht wordt.
        company_types (list): Lijst van bedrijfstypes (bijv. ['kledingwinkel', 'timmermannen']).
        areas (list): Lijst van gebieden binnen de stad (bijv. ['centrum', 'bedrijfsterrein']).
        google_api_key (str): API-sleutel voor Google Maps/Places.

    Returns:
        list: Een lijst van dictionaries met bedrijfsinformatie.
    """
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

def scrape_companies_wrapper(city, industry, company_types, areas):
    """
    Wrapper functie die de `scrape_companies` aanroept met de Google API key vanuit environment variables.

    Args:
        city (str): De stad waarin gezocht wordt.
        industry (str): De branche waarin gezocht wordt.
        company_types (list): Lijst van bedrijfstypes.
        areas (list): Lijst van gebieden binnen de stad.

    Returns:
        list: Een lijst van dictionaries met bedrijfsinformatie.
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    return scrape_companies(city, industry, company_types, areas, google_api_key)
