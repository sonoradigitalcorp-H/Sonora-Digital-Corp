# 🤖 DEMO CLIENTE — Aztrotech (César Holguín) — STAGING SANITIZADO

> **Propósito**: Entorno de demostración AISLADO para César. Expone SOLO
> información limpia y estable. NUNCA logs crudos, prompts internos,
> registry de tenants, rutas de archivos ni mensajes de debug.
>
> **Rama**: `next` (master/main intocadas).

---

## 1. ¿Qué ve César vs. qué ve MYSTIC?

| Elemento | César (cliente) | MYSTIC (interno) |
|---|---|---|
| Bot Telegram `@Aztro_tech_bot` | ✅ Respuestas limpias (modo cliente/CEO verificado) | ✅ Mismo bot + sesiones locales |
| `/status` en puerto `5290` | ✅ Health básico: `operativo`, `24/7` | ✅ Igual + ledger de acceso |
| Logs crudos (`~/.openclaw/logs/*.err`) | ❌ NO (perm 600, fuera del repo) | ✅ Lectura total |
| Registry tenants (`tenant_registry.json`) | ❌ NO expuesto en ningún endpoint | ✅ |
| Prompts / AGENTS.md internos | ❌ NO | ✅ |
| Repo git (`master`, estructura canónica) | ❌ NO accede al repo | ✅ Rama `next` |

## 2. Cómo accede César al demo

### A. Bot de Telegram (canal principal recomendado)
1. Abre Telegram y busca **`@Aztro_tech_bot`**.
2. Envía `hola`, pide un *diagnóstico IA*, *cotización* o *agendar llamada*.
3. El bot responde en texto + voz (es-MX), limpio y estable — sin errores internos.

### B. Health status visible (dashboard/cliente)
```bash
# Desde cualquier navegador / curl en la red local:
curl http://<IP_LOCAL>:5290/status
```
Respuesta (limpia, sin internos):
```json
{
  "status": "operativo",
  "servicio": "Asistente Virtual Aztrotech",
  "bot": "Aztro_tech_bot",
  "canal": "Telegram",
  "atencion": "24/7"
}
```

### C. Demo webhook (para pruebas controladas)
```bash
curl -X POST http://<IP_LOCAL>:5290/webhook -H "Content-Type: application/json" \
  -d '{"message":"cuánto cuesta el Empleado Digital"}'
```

> ⚠️ UFW: la máquina SOLO abre 22/80/443 desde LAN (`10.0.0.0/8` DENY).
> El puerto 5290 no se abre hacia afuera — queda accesible solo en la red
> local y por SSH túnel. Para exponerlo: `sudo ufw allow 5290 comment 'demo aztrotech'`.

## 3. Comandos de operación (MYSTIC)

```bash
# Arrancar/parar el demo
systemctl --user start sdc-aztrotech-demo
systemctl --user stop sdc-aztrotech-demo
systemctl --user status sdc-aztrotech-demo

# Ver salud del staging
curl -s http://127.0.0.1:5290/status

# Logs del demo (SOLO MYSTIC — perm 600)
tail -f ~/.openclaw/logs/demo-service.log

# Ledger de accesos demo (quién/quiénes consultaron el status)
cat ~/.openclaw/logs/demo-ledger.jsonl
```

## 4. Reglas de aislamiento (NO romper)

1. **NUNCA** escribir en `@Aztro_tech_bot` mensajes de debug/pruebas internas —
   César los vería. Usar el webhook demo (`/webhook` local) o el ledger.
2. **NUNCA** exponer `tenant_registry.json`, `AGENTS.md`, prompts, o rutas internas
   en respuestas del bot. El agente `cesar` tiene estas reglas en su AGENTS.md.
3. **NUNCA** abrir puertos de logs (5289/5290 no exponen archivos — el webhook de
   producción fue sanitizado en `next`).
4. Logs del bot activo viven en `~/.openclaw/logs/` (dir `700`, archivos `600`).
5. Todo código de este demo vive en rama `next`. master/main = producción estable.

## 5. Archivos de este directorio

| Archivo | Función |
|---|---|
| `demo_server.py` | Servidor staging sanitizado (puerto 5290). Sin fugas internas. |
| `sdc-aztrotech-demo.service` | Unit systemd user para arrancar el demo 24/7. |
| `README.md` | Este documento. |

## 6. Estado actual (2026-08-11)

- [x] Demo server sanitizado creado y probado (5/5 endpoints limpios).
- [x] Unit systemd listo (`sdc-aztrotech-demo.service`).
- [x] Rama `next` creada desde `master` (master intacto).
- [x] Logs crudos del bot: dir `700` + archivos `600` (solo MYSTIC).
- [x] Webhook de producción sanitizado en `next` (quita registry + echo de mensajes).
- [x] Sesiones del agente cesar protegidas (perm 600).
- [ ] Instalar y arrancar el servicio demo (pendiente OK de MYSTIC).
- [ ] Opcional: abrir 5290 en UFW si César debe ver /status desde otro equipo.