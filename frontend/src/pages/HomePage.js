// ai-contact-finder/frontend/src/pages/HomePage.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchCompanies } from '../utils/api';

function HomePage() {
  const navigate = useNavigate();

  const [city, setCity] = useState('');
  const [industry, setIndustry] = useState('');
  const [companyTypes, setCompanyTypes] = useState('');
  const [areas, setAreas] = useState('');
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    setError('');

    const ctArr = companyTypes.split(',').map((i) => i.trim()).filter(Boolean);
    const arArr = areas.split(',').map((i) => i.trim()).filter(Boolean);

    if (!city || !industry) {
      setError('Stad en branche zijn vereist.');
      return;
    }

    try {
      const data = await searchCompanies({
        city,
        industry,
        company_types: ctArr,
        areas: arArr,
      });

      if (data.error) {
        setError(data.error);
      } else if (data.message) {
        setError(data.message); // bijv. "Geen bedrijven gevonden..."
      } else if (data.companies) {
        localStorage.setItem('searchResults', JSON.stringify(data.companies));
        navigate('/results');
      }
    } catch (err) {
      setError('Er ging iets fout bij het zoeken.');
    }
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-6 rounded shadow">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">
        Zoek naar bedrijven
      </h2>

      <form onSubmit={handleSearch} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Stad:
          </label>
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Bijv: Amsterdam"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Branche:
          </label>
          <input
            type="text"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Bijv: IT"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Bedrijfstypes (komma-gescheiden):
          </label>
          <input
            type="text"
            value={companyTypes}
            onChange={(e) => setCompanyTypes(e.target.value)}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Bijv: software, consultancy"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Gebieden (komma-gescheiden):
          </label>
          <input
            type="text"
            value={areas}
            onChange={(e) => setAreas(e.target.value)}
            className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Bijv: centrum, bedrijventerrein"
          />
        </div>

        {error && (
          <p className="text-red-600 font-medium">{error}</p>
        )}

        <button
          type="submit"
          className="w-full bg-blue-600 text-white font-semibold rounded py-2 hover:bg-blue-700 transition"
        >
          Zoeken
        </button>
      </form>
    </div>
  );
}

export default HomePage;
