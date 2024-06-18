/** @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  prefix: 'tw-',
  darkMode: 'class',
  content: ["./src/probability_api/templates/**/*.{html.jinja,html}",
            "./src/object_api/templates/**/*.{html.jinja,html}",
            "./src/magstats_api/templates/**/*.{html.jinja,html}"
           ],
  theme: {
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  }
}

