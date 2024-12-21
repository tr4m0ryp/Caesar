// ai-contact-finder/frontend/src/pages/ResultPage.js
import React, { useState, useEffect } from 'react';
import ContactForm from '../components/ContactForm';
import { contactCompany } from '../utils/api';

function ResultPage() {
  const [companies, setCompanies] = useState([]);
  const [feedback, setFeedback] = useState('');

  useEffect(() => {
    const stored = localStorage.getItem('searchResults');
    if (stored) {
      setCompanies(JSON.parse(stored));
    }
  }, []);

  const handleContact = async (companyId, method) => {
    setFeedback('');

    try {
      const data = await contactCompany({
        company_id: companyId,
        contact_method: method,
      });

      if (data.error) {
        setFeedback(`Fout: ${data.error}`);
      } else {
        setFeedback(data.status || 'Contactpoging gestart');
        if (data.contact_url) {
          // open in nieuw tabblad
          window.open(data.contact_url, '_blank');
        }
      }
    } catch (error) {
      setFeedback('Er ging iets fout bij het initiëren van contact.');
    }
  };

  if (!companies || companies.length === 0) {
    return (
      <div className="max-w-3xl mx-auto mt-10 bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold text-gray-800">
          Geen resultaten gevonden
        </h2>
        <p className="mt-2 text-gray-600">Ga terug naar de homepagina om een nieuwe zoekopdracht te doen.</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto mt-10">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">
        Gevonden Bedrijven
      </h2>

      {feedback && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded">
          {feedback}
        </div>
      )}

      <ul className="space-y-4">
        {companies.map((company) => (
          <li key={company.id} className="bg-white p-4 rounded shadow">
            <h3 className="text-lg font-semibold text-gray-700">
              {company.name}
            </h3>
            <p className="text-gray-500">Contact: {company.contact || 'Onbekend'}</p>

            <ContactForm
              onSubmitContact={(method) => handleContact(company.id, method)}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ResultPage;
