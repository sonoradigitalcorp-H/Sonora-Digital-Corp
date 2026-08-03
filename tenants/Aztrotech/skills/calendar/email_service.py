"""Email Service — Send booking confirmations and welcome emails."""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger("email-service")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@aztrotech.mx")
FROM_NAME = "Aztrotech AI"


def send_booking_confirmation(to_email: str, name: str, date: str, time: str, phone: str = "") -> bool:
    """Send booking confirmation email."""
    if not SMTP_USER:
        logger.warning("SMTP not configured, skipping email")
        return False
    
    try:
        subject = f"Confirmación de llamada con César - {date} {time}"
        
        html = f"""
        <div style="font-family:Inter,Arial,sans-serif;max-width:600px;margin:0 auto;padding:32px">
            <div style="text-align:center;margin-bottom:32px">
                <div style="display:inline-block;width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#00d4ff,#0066ff);color:white;font-weight:800;font-size:20px;line-height:48px">A</div>
                <h1 style="font-size:24px;margin-top:16px;color:#1a1a2e">Aztrotech AI</h1>
            </div>
            
            <div style="background:#f8fafc;border-radius:16px;padding:24px;margin-bottom:24px">
                <h2 style="font-size:18px;color:#1a1a2e;margin-bottom:16px">¡Hola {name}! Tu llamada está confirmada</h2>
                
                <div style="display:flex;gap:16px;margin-bottom:16px">
                    <div style="flex:1;background:white;border-radius:12px;padding:16px;text-align:center;border:1px solid #e2e8f0">
                        <div style="font-size:12px;color:#64748b;margin-bottom:4px">📅 Fecha</div>
                        <div style="font-size:16px;font-weight:600;color:#1a1a2e">{format_date(date)}</div>
                    </div>
                    <div style="flex:1;background:white;border-radius:12px;padding:16px;text-align:center;border:1px solid #e2e8f0">
                        <div style="font-size:12px;color:#64748b;margin-bottom:4px">🕐 Hora</div>
                        <div style="font-size:16px;font-weight:600;color:#00d4ff">{time}</div>
                    </div>
                </div>
                
                <div style="background:white;border-radius:12px;padding:16px;border:1px solid #e2e8f0">
                    <div style="font-size:13px;color:#64748b;margin-bottom:8px">Detalles de la llamada</div>
                    <div style="font-size:14px;color:#1a1a2e">
                        <strong>César Holguín</strong> — Fundador de Aztrotech<br>
                        Duración: 15 minutos<br>
                        Modalidad: Llamada telefónica
                    </div>
                </div>
            </div>
            
            <div style="text-align:center;margin-bottom:24px">
                <a href="https://wa.me/5216621072254" style="display:inline-block;padding:12px 24px;background:#25D366;color:white;text-decoration:none;border-radius:8px;font-weight:600">📱 WhatsApp con César</a>
            </div>
            
            <div style="text-align:center;font-size:12px;color:#94a3b8">
                <p>Si necesitas reprogramar, envía un mensaje por WhatsApp.</p>
                <p style="margin-top:8px">Aztrotech · Hermosillo, Sonora<br>aztrotech.mx</p>
            </div>
        </div>
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        logger.info(f"Confirmation email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False


def send_welcome_email(to_email: str, name: str) -> bool:
    """Send welcome email after first booking."""
    if not SMTP_USER:
        return False
    
    try:
        subject = f"Bienvenido a Aztrotech, {name}"
        
        html = f"""
        <div style="font-family:Inter,Arial,sans-serif;max-width:600px;margin:0 auto;padding:32px">
            <div style="text-align:center;margin-bottom:32px">
                <div style="display:inline-block;width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#00d4ff,#0066ff);color:white;font-weight:800;font-size:20px;line-height:48px">A</div>
                <h1 style="font-size:24px;margin-top:16px;color:#1a1a2e">¡Bienvenido, {name}!</h1>
                <p style="color:#64748b;margin-top:8px">Gracias por confiar en Aztrotech</p>
            </div>
            
            <div style="background:#f0f9ff;border-radius:16px;padding:24px;margin-bottom:24px;border:1px solid #bae6fd">
                <h3 style="font-size:16px;color:#1a1a2e;margin-bottom:12px">¿Qué sigue?</h3>
                <ul style="list-style:none;padding:0">
                    <li style="padding:8px 0;font-size:14px;color:#1a1a2e">✅ Llamada con César para conocerte</li>
                    <li style="padding:8px 0;font-size:14px;color:#1a1a2e">✅ Diagnóstico gratuito de tu negocio</li>
                    <li style="padding:8px 0;font-size:14px;color:#1a1a2e">✅ Propuesta personalizada en 48h</li>
                </ul>
            </div>
            
            <div style="text-align:center">
                <p style="font-size:13px;color:#64748b">Mientras tanto, puedes conocernos:</p>
                <div style="margin-top:12px">
                    <a href="https://aztrotech.mx" style="display:inline-block;padding:8px 16px;margin:4px;background:#00d4ff;color:white;text-decoration:none;border-radius:6px;font-size:13px">🌐 Web</a>
                    <a href="https://instagram.com/cesarholguin" style="display:inline-block;padding:8px 16px;margin:4px;background:#E4405F;color:white;text-decoration:none;border-radius:6px;font-size:13px">📸 Instagram</a>
                    <a href="https://wa.me/5216621072254" style="display:inline-block;padding:8px 16px;margin:4px;background:#25D366;color:white;text-decoration:none;border-radius:6px;font-size:13px">📱 WhatsApp</a>
                </div>
            </div>
        </div>
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        
        return True
    except Exception as e:
        logger.error(f"Welcome email error: {e}")
        return False


def format_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d de %B de %Y").replace("January","enero").replace("February","febrero").replace("March","marzo").replace("April","abril").replace("May","mayo").replace("June","junio").replace("July","julio").replace("August","agosto").replace("September","septiembre").replace("October","octubre").replace("November","noviembre").replace("December","diciembre")
    except:
        return date_str
