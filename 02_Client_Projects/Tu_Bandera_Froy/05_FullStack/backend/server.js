require('dotenv').config();
const TENANT_ID = process.env.TENANT_ID || 'tu-bandera';
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fetch = require('node-fetch');
const sqlite3 = require('sqlite3').verbose();
const { exec } = require('child_process');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// SQLite DB initialization
const DB_PATH = path.join(__dirname, '..', 'tu_bandera_leads.db');
const db = new sqlite3.Database(DB_PATH, (err) => {
  if (err) {
    console.error('Error opening DB', err);
  } else {
    db.run(`CREATE TABLE IF NOT EXISTS leads (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tenant_id TEXT,
      full_name TEXT,
      contact TEXT,
      profile TEXT,
      urgency TEXT,
      service TEXT,
      message TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );`);
  }
});

// Helper: send WhatsApp notification via wacli
function notifyRoberto(data) {
  const { full_name, contact, profile, urgency, service, message } = data;
  const note = `🚨 *Nuevo Lead - Tu Bandera A.C.*\n\n👤 *Contacto*: ${full_name} (${contact})\n🏷 *Perfil*: ${profile}\n⚠️ *Urgencia*: ${urgency}\n🩺 *Servicio*: ${service}\n\n💬 *Mensaje*: ${message}`;
  const cmd = `wacli send text --store ${process.env.WACLI_STORE || '/home/mystic/.wacli'} --to ${process.env.ROBERTO_WA || '5216623645186@s.whatsapp.net'} --message "${note}"`;
  exec(cmd, (err, stdout, stderr) => {
    if (err) {
      console.error('WhatsApp notification error', err);
    } else {
      console.log('WhatsApp notification sent');
    }
  });
}

// Endpoint: Save lead and possibly notify
app.post('/api/lead', (req, res) => {
  const { full_name, contact, profile, urgency, service, message } = req.body;
  const stmt = db.prepare('INSERT INTO leads (full_name, contact, profile, urgency, service, message) VALUES (?,?,?,?,?,?)');
  stmt.run(TENANT_ID, full_name, contact, profile, urgency, service, message, function(err) {
    if (err) {
      console.error(err);
      return res.status(500).json({error: 'DB error'});
    }
    // Notify Roberto if high urgency
    if (['ATENCION_INMEDIATA', 'ALTA'].includes(urgency) || profile !== 'DIRECTO') {
      notifyRoberto({full_name, contact, profile, urgency, service, message});
    }
    res.json({ success: true, leadId: this.lastID });
  });
});

// Endpoint: Chat (text + optional audio)
app.post('/api/chat', upload.single('audio'), async (req, res) => {
  const userText = req.body.text || '';
  const audioFile = req.file; // optional
  // Simple classification using backend scoring module (could be imported)
  const scoring = require('./tubandera_scoring'); // assumes file exists
  const profile = scoring.classify_user_profile(userText);
  const urgencyEval = scoring.evaluate_urgency(userText);
  const service = urgencyEval.requiere_traslado ? 'Traslado 24/7' : (profile === 'INSTITUCION' ? 'Pláticas Preventivas' : 'Diagnóstico Gratuito');

  // Save lead
  const leadStmt = db.prepare('INSERT INTO leads (full_name, contact, profile, urgency, service, message) VALUES (?,?,?,?,?,?)');
  leadStmt.run(TENANT_ID, 'Anonimo', 'N/A', profile, urgencyEval.urgencia, service, userText);

  // Call OpenRouter LLM
  const systemPrompt = `Eres el asistente de Tu Bandera A.C., orientador clínico sin prescripciones ni juicios de valor. Responde en español, tono empático y profesional. Contexto: perfil ${profile}, urgencia ${urgencyEval.urgencia}.`; 
  const payload = {
    model: 'deepseek/deepseek-v4-flash-0731',
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userText }
    ],
    max_tokens: 500,
    temperature: 0.6
  };
  try {
    const apiRes = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    const data = await apiRes.json();
    const reply = data.choices && data.choices[0] && data.choices[0].message.content ? data.choices[0].message.content.trim() : 'Lo siento, no puedo responder en este momento.';

    // Generate voice using edge-tts (CLI) and send back URL path
    const tmpOgg = path.join(__dirname, '..', 'frontend', 'tmp', `${Date.now()}.ogg`);
    const ttsCmd = `edge-tts --voice es-MX-DaliaNeural --text "${reply.replace(/"/g, '\\"')}" --write-media ${tmpOgg} --rate +2%`;
    exec(ttsCmd, (err) => {
      if (err) {
        console.error('TTS error', err);
        return res.json({ reply, audioUrl: null });
      }
      const relativeUrl = path.relative(path.join(__dirname, '..', 'frontend'), tmpOgg).replace(/\\/g, '/');
      res.json({ reply, audioUrl: `/${relativeUrl}` });
    });
  } catch (e) {
    console.error('LLM error', e);
    res.status(500).json({ error: 'LLM failed' });
  }
});

// Endpoint: Mercado Pago donation link (sandbox placeholder)
app.get('/api/donation', (req, res) => {
  const mpLink = process.env.MP_DONATION_LINK || 'https://www.mercadopago.com/checkout/v1/redirect?preference-id=YOUR_PREF_ID';
  res.json({ url: mpLink });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Tu Bandera backend listening on port ${PORT}`);
});
