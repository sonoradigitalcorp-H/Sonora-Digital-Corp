"""Campaign Orchestration Agent — Aztrotech Marketing Automation."""
import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncpg
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("campaign-agent")

DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")
NOTIF_BOT_TOKEN = os.getenv("NOTIF_BOT_TOKEN", "")
CESAR_CHAT_ID = "5738935134"

# Message templates by lead type
TEMPLATES = {
    "cold": {
        "subject": "¿Sabías que puedes automatizar tu negocio?",
        "body": "Hola {name}, somos Aztrotech. Ayudamos a negocios como {company} a automatizar su atención al cliente con IA. ¿Te gustaría saber más?",
        "followup": "Hola {name}, solo quería recordarte que tenemos una solución para {company}. ¿Agendamos una llamada rápida?"
    },
    "warm": {
        "subject": "Solución personalizada para {company}",
        "body": "Hola {name}, vi que {company} necesita {service}. Tenemos una solución a medida. ¿Hablamos esta semana?",
        "followup": "Hola {name}, ¿pudiste revisar nuestra propuesta para {company}? Estoy aquí para cualquier duda."
    },
    "hot": {
        "subject": "¡{name}, tu solución está lista!",
        "body": "Hola {name}, preparé una propuesta personalizada para {company}. Incluye {service}. ¿Agendamos una llamada hoy?",
        "followup": "Hola {name}, ¿ya revisaste la propuesta? Tenemos disponibilidad esta semana para {company}."
    }
}

# Geographic segments
GEO_SEGMENTS = {
    "hermosillo": {"prefix": "662", "timezone": "America/Hermosillo", "market": "primary"},
    "culiacan": {"prefix": "667", "timezone": "America/Mazatlan", "market": "expansion"},
    "mazatlan": {"prefix": "669", "timezone": "America/Mazatlan", "market": "tourism"},
    "los_cabos": {"prefix": "624", "timezone": "America/Mazatlan", "market": "high-end"},
}


class CampaignAgent:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(DB_URL, min_size=2, max_size=5)
    
    async def close(self):
        if self.pool:
            await self.pool.close()
    
    async def get_leads_by_type(self, lead_type: str) -> List[Dict]:
        """Get all leads of a specific type."""
        rows = await self.pool.fetch("""
            SELECT id, name, phone, lead_score, notes, created_at
            FROM leads WHERE lead_type = $1
            ORDER BY lead_score DESC
        """, lead_type)
        return [dict(r) for r in rows]
    
    def parse_notes(self, notes: str) -> Dict:
        """Parse notes field to extract company and service."""
        result = {}
        if "Empresa:" in notes:
            result["company"] = notes.split("Empresa:")[1].split("|")[0].strip()
        if "Servicio:" in notes:
            result["service"] = notes.split("Servicio:")[1].split("|")[0].strip()
        if "Presupuesto:" in notes:
            result["budget"] = notes.split("Presupuesto:")[1].strip()
        return result
    
    def get_geo_segment(self, phone: str) -> str:
        """Determine geographic segment from phone prefix."""
        clean_phone = phone.replace("+", "").replace("52", "")
        for segment, info in GEO_SEGMENTS.items():
            if clean_phone.startswith(info["prefix"]):
                return segment
        return "other"
    
    def personalize_message(self, template: str, lead: Dict, parsed: Dict) -> str:
        """Personalize message template with lead data."""
        return template.format(
            name=lead["name"].split()[0],
            company=parsed.get("company", "tu negocio"),
            service=parsed.get("service", "nuestros servicios"),
            budget=parsed.get("budget", "personalizado")
        )
    
    async def create_campaign(self, lead_type: str, campaign_name: str) -> Dict:
        """Create a new campaign for a lead type."""
        leads = await self.get_leads_by_type(lead_type)
        template = TEMPLATES[lead_type]
        
        campaign = {
            "name": campaign_name,
            "type": lead_type,
            "leads_count": len(leads),
            "leads": [],
            "created_at": datetime.now().isoformat()
        }
        
        for lead in leads:
            parsed = self.parse_notes(lead.get("notes", ""))
            geo = self.get_geo_segment(lead["phone"])
            
            campaign["leads"].append({
                "id": lead["id"],
                "name": lead["name"],
                "phone": lead["phone"],
                "company": parsed.get("company", ""),
                "service": parsed.get("service", ""),
                "budget": parsed.get("budget", ""),
                "geo": geo,
                "message": self.personalize_message(template["body"], lead, parsed),
                "followup": self.personalize_message(template["followup"], lead, parsed)
            })
        
        return campaign
    
    async def send_campaign_summary(self, campaign: Dict):
        """Send campaign summary to César via Telegram."""
        msg = f"📢 CAMPAÑA: {campaign['name']}\n\n"
        msg += f"Tipo: {campaign['type'].upper()}\n"
        msg += f"Leads: {campaign['leads_count']}\n\n"
        msg += "Leads:\n"
        
        for lead in campaign["leads"][:10]:
            msg += f"• {lead['name']} - {lead['company']} ({lead['geo']})\n"
        
        if len(campaign["leads"]) > 10:
            msg += f"\n... y {len(campaign['leads']) - 10} más\n"
        
        async with httpx.AsyncClient(timeout=15) as client:
            await client.post(
                f"https://api.telegram.org/bot{NOTIF_BOT_TOKEN}/sendMessage",
                json={"chat_id": CESAR_CHAT_ID, "text": msg}
            )
        
        logger.info(f"Campaign {campaign['name']} summary sent")
    
    def generate_market_study(self, leads: List[Dict]) -> Dict:
        """Generate market study by geographic area."""
        study = {
            "total_leads": len(leads),
            "by_geo": {},
            "by_industry": {},
            "by_budget": {"low": 0, "medium": 0, "high": 0}
        }
        
        for lead in leads:
            parsed = self.parse_notes(lead.get("notes", ""))
            geo = self.get_geo_segment(lead["phone"])
            
            if geo not in study["by_geo"]:
                study["by_geo"][geo] = {"count": 0, "leads": []}
            study["by_geo"][geo]["count"] += 1
            study["by_geo"][geo]["leads"].append(lead["name"])
            
            # Budget analysis
            budget = parsed.get("budget", "")
            if budget:
                try:
                    amount = int(budget.replace("k/mes", "").replace(",", ""))
                    if amount < 15:
                        study["by_budget"]["low"] += 1
                    elif amount < 30:
                        study["by_budget"]["medium"] += 1
                    else:
                        study["by_budget"]["high"] += 1
                except:
                    pass
        
        return study


async def main():
    agent = CampaignAgent()
    await agent.connect()
    
    print("=== CAMPAIGN ORCHESTRATION AGENT ===\n")
    
    # Create campaigns for each lead type
    for lead_type in ["hot", "warm", "cold"]:
        campaign = await agent.create_campaign(
            lead_type,
            f"Campaña {lead_type.capitalize()} - {datetime.now().strftime('%d/%m/%Y')}"
        )
        print(f"\n{'='*50}")
        print(f"Campaña {lead_type.upper()}: {campaign['leads_count']} leads")
        print(f"{'='*50}")
        
        for lead in campaign["leads"][:5]:
            print(f"  • {lead['name']} - {lead['company']} ({lead['geo']})")
            print(f"    Msg: {lead['message'][:80]}...")
        
        if len(campaign["leads"]) > 5:
            print(f"  ... y {len(campaign['leads']) - 5} más")
        
        await agent.send_campaign_summary(campaign)
    
    # Generate market study
    all_leads = []
    for lt in ["hot", "warm", "cold"]:
        leads = await agent.get_leads_by_type(lt)
        all_leads.extend(leads)
    
    study = agent.generate_market_study(all_leads)
    print(f"\n{'='*50}")
    print("ESTUDIO DE MERCADO")
    print(f"{'='*50}")
    print(f"Total leads: {study['total_leads']}")
    print(f"Por geografía: {json.dumps(study['by_geo'], indent=2)}")
    print(f"Por presupuesto: {json.dumps(study['by_budget'], indent=2)}")
    
    await agent.close()
    print("\n✅ Campañas creadas y enviadas a César")


if __name__ == "__main__":
    asyncio.run(main())
