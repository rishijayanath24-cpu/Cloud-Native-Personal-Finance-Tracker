const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const router = express.Router();

const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://user-service:8001';
const TRANSACTION_SERVICE_URL = process.env.TRANSACTION_SERVICE_URL || 'http://transaction-service:8002';
const BUDGET_SERVICE_URL = process.env.BUDGET_SERVICE_URL || 'http://budget-service:8003';
const NOTIFICATION_SERVICE_URL = process.env.NOTIFICATION_SERVICE_URL || 'http://notification-service:8004';
const ANALYTICS_SERVICE_URL = process.env.ANALYTICS_SERVICE_URL || 'http://analytics-service:8005';

const proxyOptions = (target) => ({
  target,
  changeOrigin: true,
  on: {
    error: (err, req, res) => {
      console.error(`Proxy error: ${err.message}`);
      res.status(503).json({ error: 'Service temporarily unavailable', details: err.message });
    },
    proxyReq: (proxyReq, req) => {
      console.log(`Proxying ${req.method} ${req.url} -> ${target}`);
    },
  },
});

// User Service routes
router.use('/users', createProxyMiddleware(proxyOptions(USER_SERVICE_URL)));

// Transaction Service routes
router.use('/transactions', createProxyMiddleware(proxyOptions(TRANSACTION_SERVICE_URL)));

// Budget Service routes
router.use('/budgets', createProxyMiddleware(proxyOptions(BUDGET_SERVICE_URL)));

// Notification Service routes
router.use('/notifications', createProxyMiddleware(proxyOptions(NOTIFICATION_SERVICE_URL)));

// Analytics Service routes
router.use('/analytics', createProxyMiddleware(proxyOptions(ANALYTICS_SERVICE_URL)));

module.exports = router;
