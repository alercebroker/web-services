/** @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  prefix: 'tw-',
  darkMode: 'class',
  content: [
    "./src/lightcurve_api/templates//*.{html.jinja,html,css}",
    "./src/magstats_api/templates//*.{html.jinja,html,css}",
    "./src/object_api/templates//*.{html.jinja,html,css}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  }
}

