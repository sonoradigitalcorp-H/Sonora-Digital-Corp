const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const KEY_DIR = path.join(__dirname, '..', 'keys');
const PRIV_KEY_PATH = path.join(KEY_DIR, 'rs256-private.pem');
const PUB_KEY_PATH = path.join(KEY_DIR, 'rs256-public.pem');

function ensureKeys() {
  if (fs.existsSync(PRIV_KEY_PATH)) return;
  fs.mkdirSync(KEY_DIR, { recursive: true });
  const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
  });
  fs.writeFileSync(PRIV_KEY_PATH, privateKey, { mode: 0o600 });
  fs.writeFileSync(PUB_KEY_PATH, publicKey, { mode: 0o644 });
}

ensureKeys();

const PRIVATE_KEY = fs.readFileSync(PRIV_KEY_PATH, 'utf-8');
const PUBLIC_KEY = fs.readFileSync(PUB_KEY_PATH, 'utf-8');

const TOKEN_EXPIRY = '1h';
const REFRESH_EXPIRY = '7d';

function signToken(payload) {
  return jwt.sign(payload, PRIVATE_KEY, {
    algorithm: 'RS256',
    expiresIn: TOKEN_EXPIRY,
    jwtid: crypto.randomUUID(),
  });
}

function verifyToken(token) {
  try {
    return jwt.verify(token, PUBLIC_KEY, { algorithms: ['RS256'] });
  } catch (e) {
    return null;
  }
}

function signRefreshToken(payload) {
  return jwt.sign(payload, PRIVATE_KEY, {
    algorithm: 'RS256',
    expiresIn: REFRESH_EXPIRY,
    jwtid: crypto.randomUUID(),
  });
}

module.exports = { signToken, verifyToken, signRefreshToken, PUBLIC_KEY };
