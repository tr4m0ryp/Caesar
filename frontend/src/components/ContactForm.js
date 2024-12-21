// ai-contact-finder/frontend/src/components/ContactForm.js
import React, { useState } from 'react';

const ContactForm = ({ onSubmitContact }) => {
  const [method, setMethod] = useState('whatsapp');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitContact(method);
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center space-x-2 mt-2">
      <select
        value={method}
        onChange={(e) => setMethod(e.target.value)}
        className="rounded border border-gray-300 px-2 py-1"
      >
        <option value="email">E-mail</option>
        <option value="whatsapp">WhatsApp</option>
        <option value="call">Bellen</option>
        <option value="sms">SMS</option>
        <option value="linkedin">LinkedIn</option>
        <option value="twitter">Twitter</option>
        <option value="telegram">Telegram</option>
        <option value="contact_form">Contactformulier</option>
        <option value="live_chat">Live Chat</option>
      </select>

      <button
        type="submit"
        className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition"
      >
        Start
      </button>
    </form>
  );
};

export default ContactForm;
