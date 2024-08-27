/** @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  prefix: 'tw-',
  darkMode: 'class',
<<<<<<< HEAD
  content: ["./src/lightcurve_api/templates/**/*.html.jinja"],
=======
  content: [
    "./src/lightcurve_api/templates//*.{html.jinja,html,css}",
    "./src/magstats_api/templates//*.{html.jinja,html,css}",
  ],
>>>>>>> 60b68d3f1787f078b9430ee3624a859c89e0207e
  theme: {
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  }
}

