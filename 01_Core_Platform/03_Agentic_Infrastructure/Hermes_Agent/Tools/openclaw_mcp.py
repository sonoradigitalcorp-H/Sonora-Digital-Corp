# Wrapper para OpenClaw MCP - Sonora Digital Corp
import subprocess
import sys
import json
import requests

def send_whatsapp_message(to_number, message, client_name="Unknown"):
    """
    Envía un mensaje de WhatsApp usando OpenClaw/wacli.
    """
    print(f"[Hermes Tool] Enviando WhatsApp a {client_name} ({to_number})...")
    try:
        result = subprocess.run(
            ['wacli', 'send', 'text',
             '--store', '/home/mystic/.config/wacli',
             '--to', f"{to_number}@s.whatsapp.net",
             '--message', message,
             '--post-send-wait', '5s'],
            capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error enviando WhatsApp: {e}"

def send_whatsapp_file(to_number, file_path, client_name="Unknown", mime_type="auto", caption="", ptt=False):
    """
    Envía un archivo por WhatsApp usando OpenClaw/wacli.
    """
    print(f"[Hermes Tool] Enviando archivo a {client_name} ({to_number})...")
    cmd = ['wacli', 'send', 'file',
           '--store', '/home/mystic/.config/wacli',
           '--to', f"{to_number}@s.whatsapp.net",
           '--file', file_path]
    if mime_type != "auto":
        cmd.extend(['--mime', mime_type])
    if caption:
        cmd.extend(['--caption', caption])
    if ptt:
        cmd.append('--ptt')
    cmd.extend(['--post-send-wait', '5s'])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error enviando archivo: {e}"

def trigger_n8n_workflow(workflow_id, client_name="Unknown", payload=None):
    """
    Dispara un workflow de n8n para un cliente específico.
    """
    print(f"[Hermes Tool] Disparando workflow n8n para {client_name}: {workflow_id}")
    try:
        url = f"http://localhost:5678/webhook/{workflow_id}"
        response = requests.post(url, json=payload or {}, timeout=30)
        return response.text
    except Exception as e:
        return f"Error disparando workflow: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "whatsapp":
            action = sys.argv[2]
            to = sys.argv[3]
            if action == "text":
                msg = sys.argv[4]
                client = sys.argv[5] if len(sys.argv) > 5 else "Unknown"
                print(send_whatsapp_message(to, msg, client))
            elif action == "file":
                filepath = sys.argv[4]
                client = sys.argv[5] if len(sys.argv) > 5 else "Unknown"
                mime = sys.argv[6] if len(sys.argv) > 6 else "auto"
                caption = sys.argv[7] if len(sys.argv) > 7 else ""
                ptt = sys.argv[8] == "--ptt" if len(sys.argv) > 8 else False
                print(send_whatsapp_file(to, filepath, client, mime, caption, ptt))
        elif cmd == "workflow":
            wid = sys.argv[2]
            client = sys.argv[3] if len(sys.argv) > 3 else "Unknown"
            payload = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
            print(trigger_n8n_workflow(wid, client, payload))
