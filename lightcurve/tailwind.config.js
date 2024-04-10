/** @type {import('tailwindcss').Config} */
module.exports = {
  important: ".tw-preflight",
  prefix: 'tw-',
  darkMode: 'class',
  content: ["./src/api/templates/**/*.html.jinja"],
  theme: {
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  }
}

