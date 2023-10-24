/** @type {import('next').NextConfig} */
const removeImports = require("next-remove-imports")();

let nextConfig = removeImports({
  experimental: { esmExternals: true }
});

nextConfig = {
  ...nextConfig,
  webpackDevMiddleware: config => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    }
    return config
  },
  reactStrictMode: true,
  images: {
    loader: "custom",
    loaderFile: './imageLoader.js'
  },
  removeImports: removeImports({
    experimental: { esmExternals: true }
  })
}

module.exports = nextConfig
