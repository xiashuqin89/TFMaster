
const ReplaceStaticUrl = require('./replace-static-url-plugin');
const mockServer = require('./mock-server');

module.exports = {
  host: process.env.BK_DEV_DOMAIN,
  port: 8080,
  cache: true,
  open: true,
  publicPath: '/',

  // webpack config 配置
  configureWebpack() {
    return {
      devServer: {
        setupMiddlewares: mockServer,
      },
      plugins: [
        new ReplaceStaticUrl({}),
      ],
    };
  },
};
