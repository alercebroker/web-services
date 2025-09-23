/** @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  prefix: 'tw-',
  darkMode: 'class',
  content: [
    "./src/multisurvey_stamps/templates/**/*.{html.jinja,html,css}",
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

