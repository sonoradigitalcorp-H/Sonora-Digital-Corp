"""
Browser Actions — Navegación web por voz con Playwright + Kokoro.

Permite que Mystic:
- Navegue a URLs por comando de voz
- Extraiga contenido de páginas web
- Lea el contenido en voz alta con Kokoro TTS
- Tome screenshots de páginas

Uso:
    browser = BrowserActions()
    result = await browser.navigate_and_read("https://example.com")
    print(result["text"])  # contenido extraído
    audio = result["audio"]  # bytes WAV para Kokoro
"""

import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger("voice-realtime.browser")

# Cache de páginas para no recargar iguales
_PAGE_CACHE: dict[str, dict] = {}
_MAX_CACHE = 10


class BrowserActions:
    """
    Acciones de navegación web usando Playwright.
    Se conecta al pipeline de voz para leer resultados.
    """

    def __init__(self):
        self._browser = None
        self._context = None

    async def _get_browser(self):
        """Obtiene o crea instancia de Playwright (lazy, singleton)."""
        if self._browser is not None:
            return self._browser, self._context
        
        try:
            from playwright.async_api import async_playwright
            
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-gpu"]
            )
            self._context = await self._browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="MysticVoice/1.0 (Sonora Digital Corp)"
            )
            logger.info("Playwright browser launched ✓")
            return self._browser, self._context
        except Exception as e:
            logger.error(f"Failed to launch Playwright: {e}")
            raise

    async def navigate_and_read(self, url: str, max_chars: int = 2000) -> dict:
        """
        Navega a una URL, extrae el contenido principal y lo prepara para TTS.
        
        Args:
            url: URL a navegar
            max_chars: Máximo de caracteres a extraer (para no leer páginas enormes)
            
        Returns:
            dict con:
                - title: título de la página
                - text: texto extraído (limpiado)
                - url: URL final (puede tener redirect)
                - status: "ok" | "error"
                - error: mensaje de error si aplica
        """
        # Verificar cache
        cache_key = f"{url}_{max_chars}"
        if cache_key in _PAGE_CACHE:
            logger.info(f"Browser cache hit: {url}")
            return _PAGE_CACHE[cache_key]
        
        try:
            _, context = await self._get_browser()
            page = await context.new_page()
            
            logger.info(f"Browser navigating: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Esperar un poco más para carga completa
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except:
                pass  # si no termina en 5s, seguimos con lo que hay
            
            # Extraer información
            title = await page.title()
            final_url = page.url
            
            # Extraer contenido principal
            text = await page.evaluate("""
                () => {
                    // Intentar obtener el contenido principal
                    const main = document.querySelector('main, article, .content, #content, .post, .article');
                    if (main) return main.innerText;
                    
                    // Fallback: body sin scripts/styles
                    const body = document.body.cloneNode(true);
                    const scripts = body.querySelectorAll('script, style, nav, footer, header, aside');
                    scripts.forEach(s => s.remove());
                    return body.innerText;
                }
            """)
            
            await page.close()
            
            # Limpiar texto
            text = self._clean_text(text)
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            result = {
                "title": title,
                "text": text,
                "url": final_url,
                "status": "ok",
            }
            
            # Guardar en cache
            _PAGE_CACHE[cache_key] = result
            if len(_PAGE_CACHE) > _MAX_CACHE:
                _PAGE_CACHE.pop(next(iter(_PAGE_CACHE)))
            
            logger.info(f"Browser read: {title} ({len(text)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"Browser error: {e}")
            return {
                "title": "",
                "text": "",
                "url": url,
                "status": "error",
                "error": str(e),
            }

    async def search_and_read(self, query: str, search_engine: str = "google") -> dict:
        """
        Busca en Google/Bing y lee el primer resultado.
        
        Args:
            query: texto a buscar
            search_engine: "google" | "bing"
        """
        if search_engine == "google":
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=es"
        else:
            url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&cc=es"
        
        result = await self.navigate_and_read(url, max_chars=1500)
        if result["status"] == "ok":
            result["text"] = f"Resultados de búsqueda para '{query}':\\n\\n{result['text']}"
        
        return result

    async def screenshot(self, url: str) -> Optional[str]:
        """
        Toma un screenshot de una URL.
        Returns: ruta al archivo PNG o None.
        """
        try:
            _, context = await self._get_browser()
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            screenshot_path = f"/tmp/mystic-screenshot-{abs(hash(url))}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            await page.close()
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return None

    async def close(self):
        """Cierra el navegador."""
        if self._browser:
            try:
                await self._browser.close()
            except:
                pass
            self._browser = None
        if hasattr(self, '_playwright'):
            try:
                await self._playwright.stop()
            except:
                pass

    def _clean_text(self, text: str) -> str:
        """Limpia texto extraído para lectura TTS."""
        if not text:
            return ""
        # Eliminar líneas muy cortas (ruido)
        lines = [l.strip() for l in text.split("\\n") if len(l.strip()) > 3]
        # Eliminar URLs
        text = "\\n".join(lines)
        text = re.sub(r'https?://\\S+', '', text)
        # Eliminar espacios múltiples
        text = re.sub(r'\\s+', ' ', text).strip()
        return text

    @property
    def is_available(self) -> bool:
        """Verifica si Playwright está disponible."""
        try:
            import playwright
            return True
        except ImportError:
            return False
