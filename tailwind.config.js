module.exports = {
  content: [
    './templates/**/*.html',
    './frontend/src/**/*.js',
  ],
  // Dynamic classes that come from template data rather than static markup.
  safelist: [
    'h-12',
    'h-20',
    'h-40',
    'w-12',
    'w-20',
    'w-40',
    {
      pattern: /^(bg|text)-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(50|100|200|300|400|500|600|700|800|900)$/,
    },
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
