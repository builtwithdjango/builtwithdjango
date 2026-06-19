const Webpack = require("webpack");
const { merge } = require("webpack-merge");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { sentryWebpackPlugin } = require("@sentry/webpack-plugin");
const common = require("./webpack.common.js");

const sentryRelease = process.env.SENTRY_RELEASE || process.env.RENDER_GIT_COMMIT;
const sentryPluginEnabled = Boolean(
  process.env.SENTRY_AUTH_TOKEN && process.env.SENTRY_ORG && process.env.SENTRY_PROJECT
);
const sentryPluginOptions = {
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  authToken: process.env.SENTRY_AUTH_TOKEN,
  sourcemaps: {
    filesToDeleteAfterUpload: ["./frontend/build/**/*.map"],
  },
};

if (sentryRelease) {
  sentryPluginOptions.release = {
    name: sentryRelease,
  };
}

module.exports = merge(common, {
  mode: "production",
  devtool: "hidden-source-map",
  bail: true,
  output: {
    filename: "js/[name].[chunkhash:8].js",
    chunkFilename: "js/[name].[chunkhash:8].chunk.js",
  },
  plugins: [
    new Webpack.DefinePlugin({
      "process.env.NODE_ENV": JSON.stringify("production"),
    }),
    new MiniCssExtractPlugin({
      filename: "css/[name].[contenthash].css",
      chunkFilename: "css/[id].[contenthash].css",
    }),
  ].concat(sentryPluginEnabled ? [sentryWebpackPlugin(sentryPluginOptions)] : []),
  performance: {
    maxAssetSize: 244 * 1024,
    maxEntrypointSize: 244 * 1024,
    assetFilter: (assetFilename) => {
      if (/\.map$/.test(assetFilename)) return false;
      return !/^js\/sentry\.[a-f0-9]+\.chunk\.js$/.test(assetFilename);
    },
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: "babel-loader",
      },
      {
        test: /\.s?css/i,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader",
          "postcss-loader",
        ],
      },
    ],
  },
});
