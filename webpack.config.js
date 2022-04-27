const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');


module.exports = {
    context: __dirname,
    entry: './assets/js/index.js',
    output: {
        path: path.resolve('./assets/bundles/'),
        filename: 'app.js'
    },
    module: {
        rules:  [
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/
            },
            {
                test: /\.css$/,
                exclude: /node_modules/,
                use: [MiniCssExtractPlugin.loader, 'css-loader', 'postcss-loader'],
            }
        ],
    },
    resolve: {
        extensions: ['.js']
    },
    plugins: [
        new MiniCssExtractPlugin(),
    ]
};
