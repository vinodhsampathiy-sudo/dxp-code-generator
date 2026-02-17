const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
    // Proxy all /api requests to the backend
    app.use(
        '/api',
        createProxyMiddleware({
            target: 'http://localhost:8000',
            changeOrigin: true,
            logLevel: 'debug',
            onProxyReq: (proxyReq, req, res) => {
                console.log(`[Proxy] ${req.method} ${req.path} -> http://localhost:8000${req.path}`);
            },
            onError: (err, req, res) => {
                console.error('[Proxy Error]', err);
                res.status(500).json({ error: 'Proxy error', details: err.message });
            }
        })
    );
};
