module.exports = {
  content: [
    './templates/**/*.html',
  ],
  // safelist: [
  //   {pattern: /(bg|text)-(.*)-(.*)/}
  // ],
  theme: {
    extend: {
      maxWidth: {
        '1/3': '33.333333%'
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
