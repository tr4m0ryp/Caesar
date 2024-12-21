/** @type {import('tailwindcss').Config} */
module.exports = {
  // Geef hier op welke bestanden Tailwind moet scannen voor class-namen:
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", 
    // Voeg ook andere mappen of bestandsformaten toe als je ze gebruikt
  ],
  theme: {
    extend: {
      // Hier kun je custom kleuren, lettertypes, spacing, etc. definiëren
      colors: {
        'caesar-blue': '#3B82F6',
      },
      fontFamily: {
        // Als je in index.css bijv. Inter hebt toegevoegd
        'inter': ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [
    // Je kunt hier optionele plugins toevoegen, bijvoorbeeld:
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
  ],
};
