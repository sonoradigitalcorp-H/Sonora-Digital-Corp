#!/usr/bin/env python3
"""Onboarding Generator — Aztrotech.
Genera una landing page de onboarding estilo Mysticgrimoire con branding de César.
Input: logo_path, avatar_path, lora_assets
Output: index.html + assets/

Uso:
    python3 onboarding_generator.py --name cesar --tenant azrotech --output /path/to/landing
"""
import os, sys, argparse, json
from pathlib import Path
from datetime import datetime

TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{{
    --primary:#00d4ff;--primary-dim:rgba(0,212,255,0.15);
    --accent:#7c3aed;--accent-dim:rgba(124,58,237,0.12);
    --copper:#AC6D3E;--bg:#080c18;--card:rgba(15,23,42,0.75);
    --text:#e2e8f0;--muted:rgba(226,232,240,0.3);
    --border:rgba(0,212,255,0.1);
}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;flex-direction:column;overflow:hidden}}
#bg{{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.4}}
.app{{position:relative;z-index:1;flex:1;display:flex;flex-direction:column;max-width:800px;margin:0 auto;width:100%;padding:24px}}

/* HEADER */
header{{display:flex;align-items:center;gap:12px;padding:14px 4px;border-bottom:1px solid var(--border);background:rgba(8,12,24,0.6);backdrop-filter:blur(12px)}}
.logo{{width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,var(--primary),var(--accent));display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff}}
h1{{font-size:18px;font-weight:600;line-height:1.3}}
h1 span{{color:var(--primary);font-weight:300}}

/* HERO */
.hero{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px 20px}}
.hero h2{{font-size:28px;font-weight:700;margin-bottom:16px;background:linear-gradient(90deg,var(--primary),var(--accent));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.hero p{{font-size:16px;color:var(--muted);max-width:500px;margin-bottom:24px;line-height:1.6}}

/* CTAs */
.cta-grid{{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));max-width:600px;width:100%}}
.btn{{
    display:inline-flex;align-items:center;justify-content:center;gap:8px;
    padding:12px 20px;border-radius:12px;font-weight:500;transition:transform 0.2s,box-shadow 0.2s;
    text-decoration:none;border:1px solid var(--border);background:var(--card);color:var(--text)
}}
.btn:hover{{transform:translateY(-2px);box-shadow:0 4px 20px var(--primary-dim)}}
.btn-primary{{background:linear-gradient(135deg,var(--primary),var(--accent));border:none;color:#000}}
.btn-primary:hover{{box-shadow:0 4px 24px rgba(0,212,255,0.3)}}
.btn-cita{{background:#AC6D3E;border-color:#AC6D3E;color:#fff}}
.btn-cita:hover{{box-shadow:0 4px 20px rgba(172,109,62,0.3)}}

/* VOZ */
.voz-toggle{{display:flex;align-items:center;gap:8px;cursor:pointer}}
.voz-toggle input{{accent-color:var(--primary)}}

/* FOOTER */
footer{{padding:16px 4px;border-top:1px solid var(--border);text-align:center;color:var(--muted);font-size:13px}}

/* 3D Galaxy Background */
#galaxyCanvas{{position:absolute;top:0;left:0;width:100%;height:100%;z-index:-1;pointer-events:none;opacity:0.3}}
</style>
</head>
<body>
<div id="bg"></div>
<div class="app">
  <header>
    <div class="logo">{initials}</div>
    <h1><span>{name}</span> Assistant</h1>
  </header>
  <div class="hero">
    <h2>¡Hola! Soy {name}</h2>
    <p>{tagline}</p>
    <div class="cta-grid">
      <a href="{cta1_url}" class="btn btn-cita">{cta1_text}</a>
      <a href="{cta2_url}" class="btn">{cta2_text}</a>
    </div>
    <div class="voz-toggle">
      <input type="checkbox" id="vozSwitch" checked>
      <label for="vozSwitch">Responder con voz clonada</label>
    </div>
  </div>
  <footer>
    <p>© {year} {company} | <a href="{web}" target="_blank" style="color:var(--primary)">Web oficial</a></p>
  </footer>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// Galaxy background effect (stylized Three.js)
const canvas = document.createElement('canvas');
const renderer = new THREE.WebGLRenderer({canvas, alpha: true, antialias: true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('bg').appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 5;

const starsGeometry = new THREE.BufferGeometry();
const starCount = 1000;
const starPositions = new Float32Array(starCount * 3);
for(let i=0; i<starCount; i++){
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const r = 5 * Math.cbrt(Math.random());
    starPositions[i*3] = r * Math.sin(phi) * Math.cos(theta);
    starPositions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    starPositions[i*3+2] = r * Math.cos(phi);
}
starsGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
const starsMaterial = new THREE.PointsMaterial({color: new THREE.Color(0x00d4ff), size: 0.02});
const stars = new THREE.Points(starsGeometry, starsMaterial);
scene.add(stars);

function animate(){
    requestAnimationFrame(animate);
    stars.rotation.x += 0.001;
    stars.rotation.y += 0.001;
    renderer.render(scene, camera);
}
animate();

// Resize handler
window.addEventListener('resize',()=>{{
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
}});

// Voice toggle handler
document.getElementById('vozSwitch').addEventListener('change',(e)=>{
    if(e.target.checked){
        // TODO: Enable voice response via backend TTS
        console.log('Voz activada');
    }
});
</script>
</body>
</html>'''


def generate_onboarding(name: str, tenant: str = "Aztrotech", output_dir: str = None, configs: dict = None):
    """Genera la landing page completa."""
    configs = configs or {}
    
    cesar = {
        "company": "Aztrotech",
        "owner": "César Holguín",
        "web": configs.get("web", "https://aztrotech.mx"),
        "instagram": configs.get("instagram", "https://instagram.com/cesarholguin"),
        "linkedin": configs.get("linkedin", "https://linkedin.com/in/cesarholguin"),
        "whatsapp": configs.get("whatsapp", "https://wa.me/526621072254"),
        "telegram": configs.get("telegram", "https://t.me/CesarHolguin"),
    }
    
    # Fill template
    html = TEMPLATE.format(
        title=f"{name} | {cesar['company']}",
        initials=name[0].upper(),
        name=name,
        tagline="Tu asistente digital 24/7 para captar y atender clientes. Contáctame directamente.",
        cta1_text="📱 WhatsApp César",
        cta1_url=cesar["whatsapp"],
        cta2_text="🌐 Web de César",
        cta2_url=cesar["web"],
        year=datetime.now().year,
        company=cesar["company"],
        web=cesar["web"]
    )
    
    if output_dir is None:
        output_dir = Path("/home/mystic/Documentos/Sonora Digital Corp Nuevo/02_Client_Projects/Aztrotech/04_Deployment/onboarding")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    return {
        "status": "success",
        "path": str(output_dir / "index.html"),
        "tenant": tenant,
        "agent": name
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Onboarding Generator")
    ap.add_argument("--name", default="César", help="Nombre del dueño")
    ap.add_argument("--tenant", default="Aztrotech", help="Tenant/cliente")
    ap.add_argument("--output", default=None, help="Carpeta de salida")
    args = ap.parse_args()
    
    configs = {
        "web": "https://aztrotech.mx",
        "whatsapp": "https://wa.me/526621072254",
        "instagram": "https://instagram.com/cesarholguin",
        "linkedin": "https://linkedin.com/in/cesarholguin"
    }
    
    result = generate_onboarding(args.name, args.tenant, args.output, configs)
    print(json.dumps(result, indent=2, ensure_ascii=False))