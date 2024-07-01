/** @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  prefix: 'tw-',
  darkMode: 'class',
  content: [
            "./src/api/templates/**/*.{html.jinja,html,css}",
            "./src/probability_api/templates/**/*.{html.jinja,html,css}",
            "./src/object_api/templates/**/*.{html.jinja,html,css}",
            "./src/magstats_api/templates/**/*.{html.jinja,html,css}",
            "./node_modules/flowbite/**/*.js",
           ],
  theme: {
    extend: {},
  },
  plugins: [require('flowbite/plugin')],
  corePlugins: {
    preflight: false,
  }
}

