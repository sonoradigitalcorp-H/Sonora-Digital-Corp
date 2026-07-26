"""Lightweight booking API server for AztroTech calendar."""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import date, datetime
from urllib.parse import urlparse, parse_qs

from . import availability, store
from .models import AvailabilityConfig, BookingSlot, Booking

config = AvailabilityConfig()
HOST = "127.0.0.1"
PORT = 8901


class BookingAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def _send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(html.encode())

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        if path == "/api/slots":
            date_str = params.get("date", [None])[0]
            if date_str:
                target = date.fromisoformat(date_str)
            else:
                target = date.today()
            slots = availability.get_available_slots(target, config)
            self._send_json({"date": str(target), "slots": [s.model_dump() for s in slots]})

        elif path == "/api/days":
            days_str = params.get("days", ["14"])[0]
            days = availability.get_available_days(int(days_str), config)
            result = []
            for d in days:
                slots = availability.get_available_slots(d, config)
                if slots:
                    result.append({
                        "date": str(d),
                        "slots_count": len(slots),
                        "first_slot": slots[0].start_time.strftime("%H:%M"),
                        "last_slot": slots[-1].start_time.strftime("%H:%M"),
                    })
            self._send_json({"days": result})

        elif path == "/api/bookings":
            all_bookings = store.get_all_bookings()
            self._send_json({"bookings": [b.model_dump() for b in all_bookings]})

        elif path == "/calendar" or path == "":
            self._send_html(HTML_PAGE)

        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/api/book":
            body = self._read_body()
            required = ["name", "email", "date", "time"]
            for field in required:
                if field not in body:
                    self._send_json({"error": f"missing field: {field}"}, 400)
                    return

            slot = BookingSlot(
                date=date.fromisoformat(body["date"]),
                start_time=datetime.strptime(body["time"], "%H:%M").time(),
                end_time=datetime.strptime(body["time"], "%H:%M").time().replace(
                    hour=datetime.strptime(body["time"], "%H:%M").time().hour,
                    minute=datetime.strptime(body["time"], "%H:%M").time().minute + config.slot_duration_minutes
                ),
            )

            booking = store.create_booking(Booking(
                id="",
                created_at=datetime.utcnow(),
                prospect_name=body["name"],
                prospect_email=body["email"],
                prospect_phone=body.get("phone"),
                company=body.get("company"),
                slot=slot,
                notes=body.get("notes"),
            ))

            self._send_json({"ok": True, "booking": booking.model_dump()}, 201)

        elif path == "/api/cancel":
            body = self._read_body()
            booking_id = body.get("id")
            if not booking_id:
                self._send_json({"error": "missing booking id"}, 400)
                return
            result = store.cancel_booking(booking_id)
            if result:
                self._send_json({"ok": True, "booking": result.model_dump()})
            else:
                self._send_json({"error": "booking not found"}, 404)

        else:
            self._send_json({"error": "not found"}, 404)


def serve():
    server = HTTPServer((HOST, PORT), BookingAPIHandler)
    print(f"AztroTech Calendar API running on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agenda diagnóstico gratuito — AztroTech</title>
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #14141e;
    --surface2: #1c1c2a;
    --border: #2a2a3e;
    --text: #e8e8f0;
    --text2: #9090a8;
    --accent: #6c5ce7;
    --accent2: #a29bfe;
    --green: #00b894;
    --radius: 12px;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem 1rem;
  }
  .container {
    max-width: 640px;
    width: 100%;
  }
  header {
    text-align: center;
    margin-bottom: 2rem;
  }
  header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  header p {
    color: var(--text2);
    margin-top: 0.5rem;
    font-size: 0.9rem;
  }
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
  }
  .card h2 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text2);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .days-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.5rem;
  }
  .day-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
  }
  .day-card:hover { border-color: var(--accent); background: #1e1e30; }
  .day-card.selected { border-color: var(--accent); background: #2a1f5e; }
  .day-card .day-name { font-size: 0.85rem; font-weight: 600; }
  .day-card .day-date { font-size: 0.75rem; color: var(--text2); margin-top: 0.2rem; }
  .day-card .day-slots { font-size: 0.7rem; color: var(--green); margin-top: 0.3rem; }
  .slots-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
  .slot-btn {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.5rem 1rem;
    color: var(--text);
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s;
  }
  .slot-btn:hover { border-color: var(--accent); background: #1e1e30; }
  .slot-btn.selected { border-color: var(--accent); background: #2a1f5e; }
  .slot-btn:disabled { opacity: 0.3; cursor: not-allowed; }
  .form-group { margin-bottom: 1rem; }
  .form-group label {
    display: block;
    font-size: 0.8rem;
    color: var(--text2);
    margin-bottom: 0.3rem;
  }
  .form-group input {
    width: 100%;
    padding: 0.7rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.2s;
  }
  .form-group input:focus { border-color: var(--accent); }
  .btn-primary {
    width: 100%;
    padding: 0.8rem;
    background: linear-gradient(135deg, var(--accent), #5a4bd1);
    border: none;
    border-radius: 8px;
    color: white;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  .btn-primary:hover { opacity: 0.9; }
  .btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
  .hidden { display: none !important; }
  .success-box {
    background: #003d2e;
    border: 1px solid var(--green);
    border-radius: var(--radius);
    padding: 1.5rem;
    text-align: center;
  }
  .success-box h3 { color: var(--green); margin-bottom: 0.5rem; }
  .success-box p { color: var(--text2); font-size: 0.9rem; }
  .loading { text-align: center; color: var(--text2); padding: 2rem; }
  .error-msg { color: #e74c3c; font-size: 0.85rem; margin-top: 0.5rem; }
  @media (max-width: 480px) {
    .days-grid { grid-template-columns: repeat(2, 1fr); }
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Diagnóstico gratuito con César</h1>
    <p>Elige un horario para tu llamada de 15 minutos</p>
  </header>

  <div id="step-days" class="card">
    <h2>Elige un día</h2>
    <div id="days-container" class="days-grid"><div class="loading">Cargando...</div></div>
  </div>

  <div id="step-slots" class="card hidden">
    <h2>Elige una hora para <span id="selected-day-label"></span></h2>
    <div id="slots-container" class="slots-grid"></div>
  </div>

  <div id="step-form" class="card hidden">
    <h2>Tus datos</h2>
    <div class="form-group">
      <label>Nombre completo</label>
      <input type="text" id="input-name" placeholder="Ej: Juan Pérez" />
    </div>
    <div class="form-group">
      <label>Correo electrónico</label>
      <input type="email" id="input-email" placeholder="ejemplo@correo.com" />
    </div>
    <div class="form-group">
      <label>Teléfono (opcional)</label>
      <input type="tel" id="input-phone" placeholder="+52 662 123 4567" />
    </div>
    <div class="form-group">
      <label>Empresa (opcional)</label>
      <input type="text" id="input-company" placeholder="Tu empresa" />
    </div>
    <div id="form-error" class="error-msg hidden"></div>
    <button id="btn-confirm" class="btn-primary" onclick="confirmBooking()">Confirmar cita</button>
  </div>

  <div id="step-success" class="hidden">
    <div class="success-box">
      <h3>Cita agendada</h3>
      <p id="success-message"></p>
    </div>
  </div>
</div>

<script>
const API = window.location.origin;

let selectedDate = null;
let selectedTime = null;

async function loadDays() {
  try {
    const r = await fetch('/api/days?days=14');
    const data = await r.json();
    if (!data.days || data.days.length === 0) {
      document.getElementById('days-container').innerHTML =
        '<p style="color: var(--text2)">No hay horarios disponibles en los próximos 14 días.</p>';
      return;
    }
    const names = ['domingo','lunes','martes','miércoles','jueves','viernes','sábado'];
    document.getElementById('days-container').innerHTML = data.days.map(d => {
      const dt = new Date(d.date + 'T12:00:00');
      return `<div class="day-card" onclick="selectDay('${d.date}')">
        <div class="day-name">${names[dt.getDay()]}</div>
        <div class="day-date">${dt.getDate()}/${dt.getMonth()+1}</div>
        <div class="day-slots">${d.slots_count} horarios</div>
      </div>`;
    }).join('');
  } catch(e) {
    document.getElementById('days-container').innerHTML =
      '<p style="color: #e74c3c">Error al cargar. Intenta de nuevo.</p>';
  }
}

async function selectDay(dateStr) {
  selectedDate = dateStr;
  selectedTime = null;
  document.querySelectorAll('.day-card').forEach(c => c.classList.remove('selected'));
  event.currentTarget.classList.add('selected');

  const names = ['domingo','lunes','martes','miércoles','jueves','viernes','sábado'];
  const dt = new Date(dateStr + 'T12:00:00');
  document.getElementById('selected-day-label').textContent =
    `${names[dt.getDay()]} ${dt.getDate()}/${dt.getMonth()+1}`;

  document.getElementById('step-slots').classList.remove('hidden');
  document.getElementById('step-form').classList.add('hidden');
  document.getElementById('step-success').classList.add('hidden');
  document.getElementById('slots-container').innerHTML = '<div class="loading">Cargando...</div>';

  try {
    const r = await fetch('/api/slots?date=' + dateStr);
    const data = await r.json();
    if (!data.slots || data.slots.length === 0) {
      document.getElementById('slots-container').innerHTML =
        '<p style="color: var(--text2)">No hay horarios disponibles este día.</p>';
      return;
    }
    document.getElementById('slots-container').innerHTML = data.slots.map(s =>
      `<button class="slot-btn" onclick="selectTime('${s.start_time}', this)">${s.start_time}</button>`
    ).join('');
  } catch(e) {
    document.getElementById('slots-container').innerHTML =
      '<p style="color: #e74c3c">Error al cargar horarios.</p>';
  }
}

function selectTime(time, btn) {
  selectedTime = time;
  document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  document.getElementById('step-form').classList.remove('hidden');
  document.getElementById('form-error').classList.add('hidden');
}

async function confirmBooking() {
  const name = document.getElementById('input-name').value.trim();
  const email = document.getElementById('input-email').value.trim();
  const phone = document.getElementById('input-phone').value.trim();
  const company = document.getElementById('input-company').value.trim();
  const err = document.getElementById('form-error');

  if (!name) { showError('Nombre requerido'); return; }
  if (!email) { showError('Correo requerido'); return; }

  document.getElementById('btn-confirm').disabled = true;
  document.getElementById('btn-confirm').textContent = 'Agendando...';

  try {
    const r = await fetch('/api/book', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ name, email, phone, company, date: selectedDate, time: selectedTime }),
    });
    const data = await r.json();
    if (data.ok) {
      const names = ['domingo','lunes','martes','miércoles','jueves','viernes','sábado'];
      const dt = new Date(selectedDate + 'T12:00:00');
      document.getElementById('success-message').textContent =
        `Tu diagnóstico gratuito con César quedó agendado ${names[dt.getDay()]} ${dt.getDate()}/${dt.getMonth()+1} a las ${selectedTime}.`;
      document.getElementById('step-days').classList.add('hidden');
      document.getElementById('step-slots').classList.add('hidden');
      document.getElementById('step-form').classList.add('hidden');
      document.getElementById('step-success').classList.remove('hidden');
    } else {
      showError(data.error || 'Error al agendar');
    }
  } catch(e) {
    showError('Error de conexión. Intenta de nuevo.');
  }
  document.getElementById('btn-confirm').disabled = false;
  document.getElementById('btn-confirm').textContent = 'Confirmar cita';
}

function showError(msg) {
  const err = document.getElementById('form-error');
  err.textContent = msg;
  err.classList.remove('hidden');
}

loadDays();
</script>
</body>
</html>"""

if __name__ == "__main__":
    serve()
