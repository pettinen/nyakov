import {resolve} from "path";

import HtmlWebpackPlugin from "html-webpack-plugin";
import MiniCSSExtractPlugin from "mini-css-extract-plugin";
import {VueLoaderPlugin} from "vue-loader";
import {DefinePlugin} from "webpack";


const ROOT_PATH = "/nyakov";

export default {
  entry: "./src/main.ts",
  experiments: {
    outputModule: true,
  },
  module: {
    rules: [
      {
        test: /\.css$/u,
        use: [
          MiniCSSExtractPlugin.loader,
          "css-loader",
        ],
      },
      {
        test: /\.png$/u,
        type: "asset/resource",
      },
      {
        test: /\.scss$/u,
        use: [
          MiniCSSExtractPlugin.loader,
          "css-loader",
          "sass-loader",
        ]
      },
      {
        test: /\.ts$/u,
        loader: "ts-loader",
	options: {
          appendTsSuffixTo: [/\.vue$/u],
        },
      },
      {
        test: /\.(eot|svg|ttf|woff2?)$/u,
        type: "asset/resource",
      },
      {
        test: /\.vue$/u,
        loader: "vue-loader",
	options: {
          esModule: true,
        },
      },
    ]
  },
  output: {
    library: {
      type: "module",
    },
    publicPath: ROOT_PATH,
  },
  plugins: [
    new DefinePlugin({
      "process.env.ROOT_PATH": JSON.stringify(ROOT_PATH),
    }),
    new HtmlWebpackPlugin({
      favicon: "assets/favicon.png",			 
    }),
    new MiniCSSExtractPlugin(),
    new VueLoaderPlugin(),
  ],
  resolve: {
    alias: {
      "@": resolve("src"),
    },
  },
};
