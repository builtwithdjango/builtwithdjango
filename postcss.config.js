module.exports = {
  plugins: {
    'postcss-import': {},
    'tailwindcss/nesting': 'postcss-nesting',
    tailwindcss: {},
    'postcss-preset-env': {
      features: { 'nesting-rules': false },
    },
    // autoprefixer: {},
    ...(process.env.NODE_ENV === 'production' ? { cssnano: {} } : {})
  }
}
