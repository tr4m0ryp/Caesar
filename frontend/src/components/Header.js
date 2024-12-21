// ai-contact-finder/frontend/src/components/Header.js
import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="bg-blue-600 text-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <h1 className="text-xl font-semibold">
          <Link to="/" className="hover:text-blue-200 transition">
            CAESAR
          </Link>
        </h1>
        <nav>
          <Link to="/" className="mr-4 hover:text-blue-200 transition">
            Home
          </Link>
          <Link to="/results" className="hover:text-blue-200 transition">
            Resultaten
          </Link>
        </nav>
      </div>
    </header>
  );
}

export default Header;
