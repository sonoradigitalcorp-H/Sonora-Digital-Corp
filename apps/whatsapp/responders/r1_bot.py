"""
Ce-Son WhatsApp Bot — Responder automático para línea 6623446953.
Flujo: Saludo → Menú → Selección → Carrito → Dirección → Pago → Confirmar → Dispatch.
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

WACLI = os.path.expanduser("~/.local/bin/wacli")
WACLI_STORE = os.path.expanduser("~/.config/wacli/r1-6623446953")
MENU_PATH = REPO / "clients" / "r1" / "menu.json"
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
SEEN_FILE = REPO / "state" / "whatsapp" / "clients" / "r1" / "responded.json"

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL = "opencode-go/deepseek-v4-flash"

# Session store: number → {"step": str, "cart": list, "data": dict}
_sessions: dict[str, dict] = {}


def _load_menu() -> dict:
    with open(MENU_PATH) as f:
        return json.load(f)


def _wacli(args: list, timeout: int = 30) -> dict:
    if not os.path.exists(WACLI):
        return {"success": False, "error": "wacli not found"}
    cmd = [WACLI] + args + ["--store", WACLI_STORE, "--json"]
    try:
        r = __import__("subprocess").run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if out:
            return json.loads(out)
        return {"success": False, "error": r.stderr.strip() or "no output"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_text(to: str, text: str) -> dict:
    jid = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    return _wacli(["send", "text", "--message", text, "--to", jid, "--post-send-wait", "2s"])


def _ask_llm(messages: list, system: str = "") -> str:
    if not OPENROUTER_KEY:
        return ""
    try:
        import httpx
        body = {
            "model": LLM_MODEL,
            "messages": ([{"role": "system", "content": system}] if system else []) + messages,
            "max_tokens": 300,
            "temperature": 0.7,
        }
        r = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
            json=body,
            timeout=15,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return ""


# ─── Menu Formatting ──────────────────────────────────────────

def format_menu() -> str:
    menu = _load_menu()
    lines = [f"🌟 *{menu['business']['name']}*", menu['business']['tagline'], ""]
    for cat in menu["categories"]:
        lines.append(f"*{cat['emoji']} {cat['name']}*")
        for item in cat["items"]:
            prices = " / ".join(f"${p}" for p in item["prices"].values())
            lines.append(f"  {item['emoji']} *{item['name']}* — {prices}")
        lines.append("")
    lines.append("Responde con lo que quieras ordenar (ej: '2 uva 250 y 1 fresa 350')")
    return "\n".join(lines)


def format_payment_methods() -> str:
    menu = _load_menu()
    lines = ["💳 *¿Cómo deseas pagar?*", ""]
    for pm in menu["payment_methods"]:
        lines.append(f"{pm['emoji']} *{pm['name']}*")
    lines.append("")
    lines.append("Responde el número o nombre del método:")
    return "\n".join(lines)


def format_cart(session: dict) -> str:
    cart = session.get("cart", [])
    if not cart:
        return "🛒 *Tu carrito está vacío*"
    lines = ["🛒 *Resumen de tu pedido:*", ""]
    total = 0
    for item in cart:
        lines.append(f"  {item['emoji']} {item['qty']}x {item['name']} (${item['price']})")
        total += item['qty'] * item['price']
    lines.append("")
    lines.append(f"*Total: ${total}*")
    session["_total"] = total
    return "\n".join(lines)


# ─── Intent Detection & LLM Parsing ─────────────────────────

SYSTEM_PROMPT = """Eres el asistente de ventas de Ce-Son, una marca de pastillas efervescentes.
Sabores: Uva 🍇, Fresa 🍓, Natural 🌿, Boobaloo 🧪, Plátano 🍌, Coco 🥥, Nuez 🥜.
Precios por unidad: $250, $350, $550.
Métodos de pago: Efectivo, Tarjeta (terminal), SPEI, Mercado Pago (link), Bitcoin.

Tu trabajo:
1. Ayudar al cliente a armar su pedido
2. Preguntar dirección cuando tenga los productos
3. Preguntar método de pago
4. Confirmar el pedido completo
5. Ser amable, directo, en español mexicano
6. NO inventar precios ni sabores
7. Si algo no queda claro, pregunta específicamente"""


def parse_order_with_llm(text: str) -> Optional[list[dict]]:
    """Use LLM to extract items from natural language order."""
    menu = _load_menu()
    flavors_text = ", ".join(f"{i['name']} ({i['emoji']})" for cat in menu["categories"] for i in cat["items"])
    prompt = f"""Del siguiente mensaje, extrae los productos ordenados en formato JSON.
Sabores disponibles: {flavors_text}
Precios: $250, $350, $550 por unidad.

Reglas:
- Responde SOLO JSON, nada más
- Formato: [{{"flavor": "uva", "price": 250, "qty": 2}}, ...]
- Si no puedes extraer nada, responde: null
- Si falta información (sabor o precio), infiere por contexto

Mensaje del cliente: {text}"""
    resp = _ask_llm([{"role": "user", "content": prompt}])
    if not resp:
        return None
    try:
        # Clean markdown code blocks
        clean = re.sub(r'```json\s*|\s*```', '', resp).strip()
        items = json.loads(clean)
        if not isinstance(items, list):
            return None
        for item in items:
            item.setdefault("qty", 1)
        return items
    except (json.JSONDecodeError, KeyError):
        return None


def detect_general_intent(text: str) -> str:
    t = text.lower().strip()
    if any(k in t for k in ["menu", "menú", "catálogo", "catalogo", "que vendes", "productos", "que tienes"]):
        return "menu"
    if any(k in t for k in ["pago", "pagar", "tarjeta", "efectivo", "spei", "transferencia", "mercadopago", "bitcoin"]):
        return "payment_method"
    if any(k in t for k in ["dirección", "direccion", "domicilio", "envia", "mandar", "ubicación", "ubicacion"]):
        return "address"
    if any(k in t for k in ["confirmo", "confirmar", "si", "dale", "adelante", "ok", "sale", "arre"]):
        return "confirm"
    if any(k in t for k in ["cancelar", "cancel", "no gracias", "despues", "después"]):
        return "cancel"
    if any(k in t for k in ["gracias", "grax", "thanks"]):
        return "thanks"
    return "order"


# ─── Session Management ──────────────────────────────────────

def get_session(phone: str) -> dict:
    if phone not in _sessions:
        _sessions[phone] = {"step": "new", "cart": [], "data": {}}
    return _sessions[phone]


def reset_session(phone: str) -> dict:
    _sessions[phone] = {"step": "new", "cart": [], "data": {}}
    return _sessions[phone]


# ─── Message Handler ─────────────────────────────────────────

def handle_message(sender: str, text: str) -> Optional[str]:
    session = get_session(sender)
    intent = detect_general_intent(text)
    step = session["step"]

    # Saludo inicial / nuevo cliente
    if step == "new" or intent == "menu":
        session["step"] = "ordering"
        return format_menu()

    # Cancelar
    if intent == "cancel":
        reset_session(sender)
        return "✅ Pedido cancelado. Si necesitas algo más, aquí estoy."

    if intent == "thanks":
        return "¡A ti! 🙌 Si necesitas algo más, solo dime."

    # Procesar orden (LLM parsing)
    if step == "ordering" or step == "adding":
        items = parse_order_with_llm(text)
        if items:
            menu = _load_menu()
            flavor_map = {}
            for cat in menu["categories"]:
                for item in cat["items"]:
                    flavor_map[item["id"]] = item
            cart = session.setdefault("cart", [])
            for it in items:
                flavor_id = it["flavor"].lower()
                if flavor_id in flavor_map:
                    fi = flavor_map[flavor_id]
                    cart.append({
                        "name": fi["name"],
                        "emoji": fi["emoji"],
                        "flavor": flavor_id,
                        "price": it["price"],
                        "qty": it["qty"],
                    })
            if cart:
                session["step"] = "address"
                return format_cart(session) + "\n\n📍 ¿Cuál es tu dirección para la entrega?"
            else:
                return "No entendí bien tu pedido. Intenta con: '2 uva 250 y 1 fresa 350'"
        else:
            # Fallback: usar LLM directo para responder
            resp = _ask_llm(
                [{"role": "user", "content": f"Cliente dice: {text}\n\nResponde como vendedor de Ce-Son (pastillas efervescentes). Ayúdale a ordenar."}],
                system=SYSTEM_PROMPT
            )
            return resp or "¿Podrías repetirme tu pedido? Ejemplo: '2 uva de 250 y 1 fresa 350'"

    # Dirección
    if step == "address" or intent == "address":
        session["data"]["address"] = text
        session["step"] = "payment"
        return format_cart(session) + "\n\n" + format_payment_methods()

    # Método de pago
    if step == "payment" or intent == "payment_method":
        t = text.lower()
        method_map = {
            "efectivo": "efectivo", "1": "efectivo",
            "tarjeta": "tarjeta", "terminal": "tarjeta", "2": "tarjeta",
            "spei": "spei", "transferencia": "spei", "3": "spei",
            "mercadopago": "mercadopago", "mp": "mercadopago", "4": "mercadopago",
            "bitcoin": "bitcoin", "cripto": "bitcoin", "5": "bitcoin",
        }
        method = None
        for k, v in method_map.items():
            if k in t:
                method = v
                break
        if not method:
            return "Método no válido. Elige: 1 Efectivo, 2 Tarjeta, 3 SPEI, 4 Mercado Pago, 5 Bitcoin"
        session["data"]["payment_method"] = method
        session["step"] = "confirm"
        emoji_map = {"efectivo": "💵", "tarjeta": "💳", "spei": "🏦", "mercadopago": "🟡", "bitcoin": "₿"}
        lines = [
            "📋 *CONFIRMA TU PEDIDO*",
            "",
            format_cart(session),
            f"📍 *Dirección:* {session['data']['address']}",
            f"💳 *Pago:* {emoji_map.get(method, '')} {method.capitalize()}",
            "",
            "¿Todo correcto? Responde: *Sí* para confirmar",
        ]
        return "\n".join(lines)

    # Confirmación final
    if step == "confirm" and intent == "confirm":
        cart = session.get("cart", [])
        total = session.get("_total", 0)
        data = session["data"]
        # Aquí se crea la orden en DB y se dispara dispatch
        from apps.whatsapp.dispatch import dispatch_order
        from apps.whatsapp.order_store import get_db, create_order

        conn = get_db()
        order = create_order(conn, {
            "client_name": data.get("client_name", sender),
            "client_phone": sender,
            "client_address": data.get("address", ""),
            "items": cart,
            "total": total,
            "payment_method": data.get("payment_method", "efectivo"),
        })
        conn.close()
        dispatch_result = dispatch_order(order["id"])
        reset_session(sender)
        return (
            f"✅ *PEDIDO CONFIRMADO* #{order['id']}\n\n"
            f"Total: ${total}\n"
            f"Pago: {data.get('payment_method', 'efectivo').capitalize()}\n"
            f"Dirección: {data.get('address', '')}\n\n"
            f"📦 En breve un repartidor tomará tu pedido.\n"
            f"Te notificaremos cualquier cambio 🙌"
        )

    # Fallback: responder con LLM
    resp = _ask_llm(
        [{"role": "user", "content": f"Cliente: {text}\n\nContexto: está en paso '{step}' del pedido. Responde como vendedor de Ce-Son."}],
        system=SYSTEM_PROMPT
    )
    return resp or "¿En qué puedo ayudarte? Responde 'Menú' para ver nuestros productos."


# ─── Responder Loop ─────────────────────────────────────────

def _load_responded() -> set:
    if not SEEN_FILE.exists():
        return set()
    try:
        with open(SEEN_FILE) as f:
            return set(json.load(f).get("ids", []))
    except Exception:
        return set()


def _save_responded(ids: set) -> None:
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump({"ids": sorted(ids), "updated": datetime.now(timezone.utc).isoformat()}, f)


def _log_event(event: str, payload: dict) -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), "payload": payload}
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_responder(once: bool = False):
    print(f"[r1-bot] Starting Ce-Son WhatsApp Bot...", file=sys.stderr)
    responded = _load_responded()

    while True:
        result = _wacli(["messages", "list", "--from-them", "--limit", "20"])
        if not result.get("success"):
            time.sleep(5)
            continue

        messages = result.get("data", [])
        if isinstance(messages, dict):
            messages = messages.get("messages", [])

        for msg in messages:
            msg_id = msg.get("id") or msg.get("message_id") or ""
            if not msg_id or msg_id in responded:
                continue

            sender = msg.get("sender", "")
            if "@" in sender:
                sender = sender.split("@", 1)[0]
            text = msg.get("text", "") or msg.get("body", "") or msg.get("message", "")

            if not text.strip():
                continue

            responded.add(msg_id)
            try:
                response = handle_message(sender, text)
                if response:
                    send_text(sender, response)
                    _log_event("r1:response:sent", {
                        "to": sender, "msg_id": msg_id,
                        "response_preview": response[:100],
                    })
                    print(f"[r1-bot] {sender}: {text[:50]} → respondido", file=sys.stderr)
            except Exception as e:
                print(f"[r1-bot] Error handling {sender}: {e}", file=sys.stderr)
                _log_event("r1:error", {"sender": sender, "error": str(e)})

        _save_responded(responded)

        if once:
            break
        time.sleep(3)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ce-Son WhatsApp Bot")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    run_responder(once=args.once)


if __name__ == "__main__":
    main()
