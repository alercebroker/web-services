/ @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  mode: 'jit',
  prefix: 'tw-',
  darkMode: 'class',
  content: [
            "./src/api/templates//*.{html.jinja,html,css}",
            "./src/probability_api/templates//*.{html.jinja,html,css}",
            "./src/object_api/templates//*.{html.jinja,html,css}",
            "./src/magstats_api/templates//*.{html.jinja,html,css}",
            "./src/scores_api/templates//*.{html.jinja,html,css}",
            "./src/banner_api/templates//*.{html.jinja,html,css}"
           ],
  theme: {
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  }
}