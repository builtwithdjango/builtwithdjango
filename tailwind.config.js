module.exports = {
  purge: {
    content: [
      './assets/js/*.js',
      './assets/js/**/*.js',
      './templates/*.html',
      './templates/**/*.html',
    ],
    options: {
      // https://nexxai.dev/tell-purgecss-to-ignore-purging-all-tailwind-colours/
      safelist: [/(bg|text)-(.*)-(.*)/]
    }
  },
  theme: {
    extend: {
      maxWidth: {
        '1/3': '33.333333%'
      }
    },
  },
  variants: {},
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
}
