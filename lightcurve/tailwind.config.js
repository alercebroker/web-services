/** @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  prefix: 'tw-',
  darkMode: 'class',
  content: ["./src/lightcurve_api/templates/**/*.html.jinja"],
  theme: {
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  }
}

