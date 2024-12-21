# ai-contact-finder/backend/app/routes.py

from flask import request, jsonify
from . import db
from .models import Company, Contact
from .scraper import scrape_companies
from .contact_tools import initiate_contact
from datetime import datetime

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    city = data.get('city')
    industry = data.get('industry')
    company_types = data.get('company_types', [])
    areas = data.get('areas', [])

    # Validatie van verplichte velden
    if not city or not industry:
        return jsonify({'error': 'Stad en branche zijn vereist.'}), 400

    # Validatie van company_types en areas als lijsten
    if not isinstance(company_types, list):
        return jsonify({'error': 'company_types moet een lijst zijn.'}), 400
    if not isinstance(areas, list):
        return jsonify({'error': 'areas moet een lijst zijn.'}), 400

    # Optionele validatie van de inhoud van company_types en areas
    allowed_company_types = {'software', 'consultancy', 'hardware', 'services'}
    allowed_areas = {'centrum', 'westelijk deel', 'noordelijk deel', 'zuidelijk deel'}

    invalid_company_types = [ct for ct in company_types if ct.lower() not in allowed_company_types]
    invalid_areas = [ar for ar in areas if ar.lower() not in allowed_areas]

    if invalid_company_types:
        return jsonify({'error': f'Ongeldige company_types: {invalid_company_types}.'}), 400
    if invalid_areas:
        return jsonify({'error': f'Ongeldige areas: {invalid_areas}.'}), 400

    # Scrape bedrijven op basis van stad, branche, bedrijfstypes en gebieden
    companies_data = scrape_companies(city, industry, company_types, areas)

    if not companies_data:
        return jsonify({'message': 'Geen bedrijven gevonden met de opgegeven criteria.'}), 404

    companies = []
    for company_info in companies_data:
        # Controleer of het bedrijf al bestaat in de database
        existing_company = Company.query.filter_by(name=company_info['name']).first()
        if not existing_company:
            # Voeg nieuw bedrijf toe aan de database
            new_company = Company(
                name=company_info['name'],
                contact=company_info['contact'],
                contact_form_url=company_info.get('contact_form_url')  # Voeg contact_form_url toe
            )
            db.session.add(new_company)
            db.session.commit()
            companies.append({
                'id': new_company.id,
                'name': new_company.name,
                'contact': new_company.contact,
                'contact_form_url': new_company.contact_form_url  # Voeg contact_form_url toe
            })
        else:
            companies.append({
                'id': existing_company.id,
                'name': existing_company.name,
                'contact': existing_company.contact,
                'contact_form_url': existing_company.contact_form_url  # Voeg contact_form_url toe
            })

    return jsonify({'companies': companies}), 200

@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()
    company_id = data.get('company_id')
    contact_method = data.get('contact_method')

    if not company_id or not contact_method:
        return jsonify({'error': 'Bedrijf ID en contactmethode zijn vereist.'}), 400

    # Haal het bedrijf op uit de database
    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Bedrijf niet gevonden.'}), 404

    # Validatie van contact_method
    allowed_methods = {'email', 'whatsapp', 'call', 'contact_form'}
    if contact_method.lower() not in allowed_methods:
        return jsonify({'error': f'Ongeldige contactmethode: {contact_method}.'}), 400

    # Initiëer contact
    try:
        if contact_method.lower() == 'contact_form':
            contact_url = company.contact_form_url
            if not contact_url:
                return jsonify({'error': 'Geen contactformulier beschikbaar voor dit bedrijf.'}), 404
            # Voor contact_form, retourneer de URL naar de frontend
            return jsonify({'status': 'Contactformulier beschikbaar.', 'contact_form_url': contact_url}), 200
        else:
            initiate_contact({'name': company.name, 'contact': company.contact}, contact_method.lower())
    except Exception as e:
        return jsonify({'error': f'Fout bij het initiëren van contact: {str(e)}'}), 500

    # Log de contactpoging
    contact_log = Contact(
        company_id=company.id,
        method=contact_method.lower(),
        status='Initiated',
        timestamp=datetime.utcnow()
    )
    db.session.add(contact_log)
    db.session.commit()

    return jsonify({'status': 'Contactpoging succesvol gestart.'}), 200
