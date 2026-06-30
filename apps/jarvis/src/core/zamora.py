"""
Alejandro Zamora — Brand Studio backend module.
Portfolio, services, pricing for the personal brand studio.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field

log = logging.getLogger("jarvis.zamora")


@dataclass(frozen=True)
class PortfolioItem:
    title: str
    description: str
    image_url: str
    category: str
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Service:
    name: str
    description: str
    icon: str
    price_mxn: str


class ZamoraStudio:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._data_file = os.path.join(data_dir, "zamora.json")
        self._portfolio: list[PortfolioItem] = []
        self._services: list[Service] = []
        self._pricing: list[dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self._data_file):
            try:
                with open(self._data_file, encoding="utf-8") as f:
                    data = json.load(f)
                self._portfolio = [PortfolioItem(**p) for p in data.get("portfolio", [])]
                self._services = [Service(**s) for s in data.get("services", [])]
                self._pricing = data.get("pricing", [])
                log.info("Zamora data loaded from %s", self._data_file)
                return
            except Exception as e:
                log.warning("Failed to load zamora data: %s", e)
        self._seed()

    def _seed(self):
        self._services = [
            Service("Identidad de Marca", "Logo, paleta de colores, tipografía, guía de marca completa", "🎨", "Consultar"),
            Service("Landing Page", "Tu sitio web profesional con diseño premium y dominio propio", "🌐", "Consultar"),
            Service("Contenido Visual", "Fotos, videos y gráficos generados con IA para tus redes", "📸", "Consultar"),
            Service("Asistente Personal", "Un asistente inteligente que trabaja 24/7 para tu marca", "🤖", "Consultar"),
            Service("Analytics", "Métricas de engagement, crecimiento y ROI de tu contenido", "📊", "Consultar"),
            Service("Tienda Online", "Merch y productos digitales con pago SPEI y crypto", "🛒", "Consultar"),
        ]
        self._pricing = [
            {"name": "Conquistador", "price": 780, "currency": "MXN", "period": "mes",
             "features": ["Asistente 24/7", "150 fotos + 50 videos", "3 páginas web", "Tienda online", "5 automatizaciones", "Analytics básico"]},
            {"name": "Agente IA", "price": 1380, "currency": "MXN", "period": "mes",
             "features": ["Asistente prioritario", "750 fotos + 250 videos", "10 páginas web", "Tienda + Printful", "Clon de voz y video", "30 automatizaciones", "CRM + KPIs", "7% comisión afiliado"]},
            {"name": "Imperio", "price": 2980, "currency": "MXN", "period": "mes",
             "features": ["Asistente dedicado", "Todo ilimitado", "Marketplace", "White-label completo", "API pública", "15% comisión afiliado", "Acceso beta features"]},
        ]
        self._save()
        log.info("Zamora seeded with default data")

    def _save(self):
        os.makedirs(self.data_dir, exist_ok=True)
        data = {
            "services": [asdict(s) for s in self._services],
            "portfolio": [asdict(p) for p in self._portfolio],
            "pricing": self._pricing,
        }
        with open(self._data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def list_services(self) -> list[Service]:
        return self._services

    def list_portfolio(self) -> list[PortfolioItem]:
        return self._portfolio

    def get_pricing(self) -> list[dict]:
        return self._pricing

    def add_portfolio_item(self, item: PortfolioItem):
        self._portfolio.append(item)
        self._save()

    def remove_portfolio_item(self, title: str) -> bool:
        before = len(self._portfolio)
        self._portfolio = [p for p in self._portfolio if p.title != title]
        if len(self._portfolio) < before:
            self._save()
            return True
        return False
