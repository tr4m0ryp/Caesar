// ai-contact-finder/frontend/src/utils/api.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000', // pas aan indien nodig
});

export const searchCompanies = async (payload) => {
  // payload = { city, industry, company_types, areas }
  const response = await API.post('/search', payload);
  return response.data;
};

export const contactCompany = async (payload) => {
  // payload = { company_id, contact_method }
  const response = await API.post('/contact', payload);
  return response.data;
};
