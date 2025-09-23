/** @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  prefix: 'tw-',
  darkMode: 'class',
  content: [
    "./src/**/templates/*.{html.jinja,html,css}",
    "./src/static/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        roboto: ['Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  }
}

