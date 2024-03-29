module.exports = (middlewares, devServer) => {
  devServer.app.use(require('cookie-parser')());
  /** mock 接口 */
  devServer.app.get('/table', (req, res) => {
    res.json({
      code: 0,
      message: '',
      data: {
        list: [
          {
            id: 1,
            ip: '127.0.0.1',
            source: '微信',
            status: '正常',
            create_time: '2018-05-25 15:02:24',
            children: [],
          },
        ],
      },
    });
  });
  devServer.app.post('/v1/state/upload_json/null/-1', (req, res) => {
    res.json({
      code: 0,
      message: '',
      data: {},
      result: true,
    });
  });
  devServer.app.post('/v1/analyze/query/null/-1', (req, res) => {
    res.json({
      data: [],
      code: 200,
      message: 'OK',
      result: true,
      request_id: 'f477c6b8-b875-4254-b842-6708f49dac81',
    });
  });
  devServer.app.use(require('../paas-server/middleware/user'));
  return middlewares;
};
