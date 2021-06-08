module.exports = {
  purge: {
    content: [
      './assets/js/*.js',
      './assets/js/**/*.js',
      './templates/*.html',
      './templates/**/*.html',
    ],
    options: {
      safelist: {
        deep: [
          /gray$/,
          /red$/,
          /yellow$/,
          /green$/,
          /blue$/,
          /indigo$/,
          /purple$/,
          /pink$/,
        ]
      }
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
