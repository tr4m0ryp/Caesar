# ai-contact-finder/backend/app/routes.py

from flask import request, jsonify
from . import db
from .models import Company, Contact
from .scraper import hybrid_scraper
from .contact_tools import initiate_contact
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    city = data.get('city')
    industry = data.get('industry')
    company_types = data.get('company_types', [])
    areas = data.get('areas', [])

    # Validatie van verplichte velden
    if not city or not industry:
        logger.warning("Stad en branche zijn vereist.")
        return jsonify({'error': 'Stad en branche zijn vereist.'}), 400

    # Validatie van company_types en areas als lijsten
    if not isinstance(company_types, list):
        logger.warning("company_types moet een lijst zijn.")
        return jsonify({'error': 'company_types moet een lijst zijn.'}), 400
    if not isinstance(areas, list):
        logger.warning("areas moet een lijst zijn.")
        return jsonify({'error': 'areas moet een lijst zijn.'}), 400

    # Validatie van de inhoud van company_types en areas
    if not all(isinstance(ct, str) and ct.strip() for ct in company_types):
        logger.warning("Alle company_types moeten niet-lege strings zijn.")
        return jsonify({'error': 'Alle company_types moeten niet-lege strings zijn.'}), 400
    if not all(isinstance(ar, str) and ar.strip() for ar in areas):
        logger.warning("Alle areas moeten niet-lege strings zijn.")
        return jsonify({'error': 'Alle areas moeten niet-lege strings zijn.'}), 400

    # Scrape bedrijven op basis van stad, branche, bedrijfstypes en gebieden
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logger.error("Geen Google API-sleutel gevonden.")
        return jsonify({'error': 'Interne serverfout.'}), 500

    companies_data = hybrid_scraper(city, industry, google_api_key)

    if not companies_data.get("results"):
        logger.info(f"Geen bedrijven gevonden voor stad: {city}, branche: {industry}.")
        return jsonify({'message': 'Geen bedrijven gevonden met de opgegeven criteria.'}), 404

    companies = []
    for company_info in companies_data["results"]:
        try:
            # Controleer of het bedrijf al bestaat in de database
            existing_company = Company.query.filter_by(name=company_info.get('name')).first()
            if not existing_company:
                # Voeg nieuw bedrijf toe aan de database
                new_company = Company(
                    name=company_info.get('name'),
                    contact=company_info.get('contact'),
                    contact_form_url=company_info.get('contact_form_url'),
                    linkedin_profile=company_info.get('linkedin_profile'),
                    twitter_handle=company_info.get('twitter_handle'),
                    telegram_handle=company_info.get('telegram_handle'),
                    live_chat_url=company_info.get('live_chat_url')
                )
                db.session.add(new_company)
                db.session.commit()
                companies.append({
                    'id': new_company.id,
                    'name': new_company.name,
                    'contact': new_company.contact,
                    'contact_form_url': new_company.contact_form_url,
                    'linkedin_profile': new_company.linkedin_profile,
                    'twitter_handle': new_company.twitter_handle,
                    'telegram_handle': new_company.telegram_handle,
                    'live_chat_url': new_company.live_chat_url
                })
                logger.info(f"Nieuw bedrijf toegevoegd: {new_company.name}")
            else:
                companies.append({
                    'id': existing_company.id,
                    'name': existing_company.name,
                    'contact': existing_company.contact,
                    'contact_form_url': existing_company.contact_form_url,
                    'linkedin_profile': existing_company.linkedin_profile,
                    'twitter_handle': existing_company.twitter_handle,
                    'telegram_handle': existing_company.telegram_handle,
                    'live_chat_url': existing_company.live_chat_url
                })
                logger.info(f"Bedrijf al bestaand: {existing_company.name}")
        except Exception as e:
            logger.error(f"Fout bij verwerken van bedrijf '{company_info.get('name', 'onbekend')}': {e}")
            continue

    return jsonify({'companies': companies}), 200

@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    company_id = data.get('company_id')
    contact_method = data.get('contact_method')

    if not company_id or not contact_method:
        logger.warning("Bedrijf ID en contactmethode zijn vereist.")
        return jsonify({'error': 'Bedrijf ID en contactmethode zijn vereist.'}), 400

    # Haal het bedrijf op uit de database
    company = Company.query.get(company_id)
    if not company:
        logger.warning(f"Bedrijf niet gevonden met ID: {company_id}")
        return jsonify({'error': 'Bedrijf niet gevonden.'}), 404

    # Validatie van contact_method
    allowed_methods = {'email', 'whatsapp', 'call', 'contact_form', 'linkedin', 'twitter', 'sms', 'telegram', 'live_chat'}
    contact_method_lower = contact_method.lower()
    if contact_method_lower not in allowed_methods:
        logger.warning(f"Ongeldige contactmethode: {contact_method}")
        return jsonify({'error': f'Ongeldige contactmethode: {contact_method}.'}), 400

    # Initiëer contact
    try:
        if contact_method_lower in {'contact_form', 'live_chat'}:
            contact_url = company.live_chat_url or company.contact_form_url
            if not contact_url:
                logger.warning(f"Geen contactformulier of live chat beschikbaar voor bedrijf ID: {company_id}")
                return jsonify({'error': 'Geen contactformulier of live chat beschikbaar voor dit bedrijf.'}), 404
            logger.info(f"Contactformulier of live chat beschikbaar via {contact_url}")
            return jsonify({'status': 'Contactformulier of Live Chat beschikbaar.', 'contact_url': contact_url}), 200
        else:
            initiate_contact({
                'name': company.name,
                'contact': company.contact,
                'linkedin_profile': company.linkedin_profile,
                'twitter_handle': company.twitter_handle,
                'telegram_handle': company.telegram_handle
            }, contact_method_lower)
            logger.info(f"Contactpoging gestart voor bedrijf ID: {company_id} via {contact_method_lower}")
    except Exception as e:
        logger.error(f"Fout bij het initiëren van contact voor bedrijf ID {company_id}: {e}")
        return jsonify({'error': f'Fout bij het initiëren van contact: {str(e)}'}), 500

    # Log de contactpoging
    try:
        contact_log = Contact(
            company_id=company.id,
            method=contact_method_lower,
            status='Initiated',
            timestamp=datetime.utcnow()
        )
        db.session.add(contact_log)
        db.session.commit()
        logger.info(f"Contactpoging gelogd voor bedrijf ID: {company_id} via {contact_method_lower}")
    except Exception as e:
        logger.error(f"Fout bij het loggen van contactpoging voor bedrijf ID {company_id}: {e}")

    return jsonify({'status': 'Contactpoging succesvol gestart.'}), 200
