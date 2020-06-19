const path = require('path');
const webpack = require('webpack');

module.exports = {
    mode: 'development',
    context: __dirname,
    entry: './assets/js/index.js',
    output: {
        path: path.resolve('./assets/bundles/'),
        filename: 'app.js'
    },
    module: {
        rules:  [
            {test: /\.js$/, loader: 'babel-loader', exclude: /node_modules/},
        ],
    },
    resolve: {
        extensions: ['.js']
    }
};
