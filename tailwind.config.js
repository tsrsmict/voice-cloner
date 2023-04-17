/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/*.html'],
  theme: {
    fontFamily: {
      'mono': ['Oxanium'],
      'sans': ['Montserrat']

    },
    extend: {},
  },
  plugins: [],
  safelist: [
    'text-red-500',
    'text-green-500',
  ]
}
