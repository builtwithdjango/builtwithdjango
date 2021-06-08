module.exports = {
  purge: {
    content: [
      './assets/js/*.js',
      './assets/js/**/*.js',
      './templates/*.html',
      './templates/**/*.html',
    ],
    options: {
      safelist: [/(from|via|to|border|bg|text)-(.*)-(\\d{1}0{1,2})/]
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
  ],
}
