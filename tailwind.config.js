module.exports = {
  content: [
    './templates/**/*.html',
  ],
  // https://nexxai.dev/tell-purgecss-to-ignore-purging-all-tailwind-colours/
  safelist: [
    {pattern: /(bg|text)-(.*)-(.*)/}
  ],
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
