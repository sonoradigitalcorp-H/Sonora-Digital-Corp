const { verifyToken } = require('./jwt');

const PUBLIC_PATHS = ['/api/auth/token', '/api/health', '/healthz', '/dashboard', '/api/dashboard', '/adk', '/api/adk', '/workflow-editor', '/api/workflow-editor'];

function parseAuthHeader(req) {
  const auth = req.headers['authorization'];
  if (!auth || !auth.startsWith('Bearer ')) return null;
  return auth.slice(7);
}

function authMiddleware(req, res, next) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const path = url.pathname;

  if (PUBLIC_PATHS.includes(path)) return next();
  if (req.method === 'OPTIONS') return next();

  const token = parseAuthHeader(req);
  if (!token) {
    res.statusCode = 401;
    res.end(JSON.stringify({ error: 'Se requiere token Bearer' }));
    return;
  }

  const decoded = verifyToken(token);
  if (!decoded) {
    res.statusCode = 401;
    res.end(JSON.stringify({ error: 'Token inválido o expirado' }));
    return;
  }

  req.auth = {
    tenant: decoded.tenant || decoded.sub,
    scope: decoded.scope || '',
    sub: decoded.sub,
    jti: decoded.jti,
  };

  if (!req.auth.tenant && decoded.sub) {
    req.auth.tenant = decoded.sub;
  }

  next();
}

function requireScope(scope) {
  return (req, res, next) => {
    if (!req.auth || !req.auth.scope) {
      res.statusCode = 403;
      res.end(JSON.stringify({ error: `Se requiere scope: ${scope}` }));
      return;
    }
    const scopes = req.auth.scope.split(' ');
    if (!scopes.some(s => scope === s || s === 'admin')) {
      res.statusCode = 403;
      res.end(JSON.stringify({ error: `Scope insuficiente. Requerido: ${scope}` }));
      return;
    }
    next();
  };
}

module.exports = { authMiddleware, requireScope };
