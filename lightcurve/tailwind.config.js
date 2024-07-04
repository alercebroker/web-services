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
          ],
  theme: {
    extend: {},
  },
  corePlugins: {
    preflight: false,
  },
  daisyui: {
    utils: true, // adds responsive and modifier utility classes
    prefix: "du-", // prefix for daisyUI classnames (components, 
  },
  plugins: [require('daisyui'),],

}

