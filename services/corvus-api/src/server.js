import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import http from 'http';
import { WebSocketServer } from 'ws';
import { validateDirectives } from './validator.js';

const app = express();
app.use(express.json({ limit: '256kb' }));
app.use(cors());
app.use(helmet());

// Simple healthcheck
app.get('/v1/health', (_req, res) => {
  res.json({ status: 'ok' });
});

// POST /v1/directives → validate then broadcast
let wss; // initialized below
function broadcast(obj) {
  if (!wss) return;
  const msg = typeof obj === 'string' ? obj : JSON.stringify(obj);
  wss.clients.forEach(client => {
    try { client.send(msg); } catch {}
  });
}

app.post('/v1/directives', (req, res) => {
  const payload = req.body;
  const result = validateDirectives(payload);
  if (!result.valid) {
    return res.status(400).json({ ok: false, errors: result.errors });
  }
  // Broadcast to subscribers
  broadcast({ type: 'directives', payload });
  return res.json({ ok: true });
});

// Create HTTP server and attach WS at /v1/events
const server = http.createServer(app);
wss = new WebSocketServer({ server, path: '/v1/events' });
wss.on('connection', (ws) => {
  try { ws.send(JSON.stringify({ type: 'hello', message: 'Connected to corvus events' })); } catch {}
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`corvus-api listening on http://localhost:${PORT}`);
});

