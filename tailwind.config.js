/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.html', // Flask templates
    './app/static/**/*.js',      // JS files in the static folder
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

