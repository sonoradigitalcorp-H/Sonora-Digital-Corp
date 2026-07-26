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

    async def click(self, selector: str, text: str = None) -> dict:
        try:
            _, context = await self._get_browser()
            page = await context.new_page()

            if text:
                logger.info(f"Browser click text: {text}")
                await page.wait_for_selector(f"text={text}", timeout=10000)
                await page.click(f"text={text}")
            else:
                logger.info(f"Browser click selector: {selector}")
                await page.wait_for_selector(selector, timeout=10000)
                await page.click(selector)

            url = page.url
            await page.close()
            return {"status": "ok", "url": url}
        except Exception as e:
            logger.error(f"Browser click error: {e}")
            return {"status": "error", "error": str(e)}

    async def fill(self, selector: str, value: str, field_label: str = None) -> dict:
        try:
            _, context = await self._get_browser()
            page = await context.new_page()

            if field_label:
                label_selector = f'label:has-text("{field_label}")'
                input_selector = f'label:has-text("{field_label}") input, label:has-text("{field_label}") textarea, label:has-text("{field_label}") select'
                try:
                    await page.wait_for_selector(input_selector, timeout=10000)
                    await page.fill(input_selector, value)
                    field_name = field_label
                except:
                    input_by_for = f'//label[contains(text(), "{field_label}")]/@for'
                    for_attr = await page.evaluate(f"""() => {{
                        const label = document.querySelector('label:has-text("{field_label}")');
                        return label ? label.getAttribute('for') : null;
                    }}""")
                    if for_attr:
                        await page.wait_for_selector(f'#{for_attr}', timeout=10000)
                        await page.fill(f'#{for_attr}', value)
                    else:
                        raise Exception(f"Field with label '{field_label}' not found")
                    field_name = field_label
            else:
                logger.info(f"Browser fill selector: {selector}")
                await page.wait_for_selector(selector, timeout=10000)
                await page.fill(selector, value)
                field_name = selector

            await page.close()
            return {"status": "ok", "field": field_name}
        except Exception as e:
            logger.error(f"Browser fill error: {e}")
            return {"status": "error", "error": str(e)}

    async def extract(self, query: str) -> dict:
        try:
            _, context = await self._get_browser()
            page = await context.new_page()

            data = await page.evaluate(f"""() => {{
                const query = '{query.replace("'", "\\'")}';
                const results = [];

                const tables = document.querySelectorAll('table');
                if (tables.length > 0) {{
                    const rows = [];
                    tables[0].querySelectorAll('tr').forEach(tr => {{
                        const cells = [];
                        tr.querySelectorAll('th, td').forEach(td => cells.push(td.innerText.trim()));
                        if (cells.length > 0) rows.push(cells.join(' | '));
                    }});
                    if (rows.length > 0) {{
                        return {{ data: rows.join('\\n'), type: 'table' }};
                    }}
                }}

                const lists = document.querySelectorAll('ul, ol');
                if (lists.length > 0) {{
                    const items = [];
                    lists[0].querySelectorAll('li').forEach(li => items.push(li.innerText.trim()));
                    if (items.length > 0) {{
                        return {{ data: items.join('\\n'), type: 'list' }};
                    }}
                }}

                const body = document.body.innerText;
                const lines = body.split('\\n').filter(l => l.toLowerCase().includes(query.toLowerCase()));
                if (lines.length > 0) {{
                    return {{ data: lines.slice(0, 20).join('\\n'), type: 'text' }};
                }}

                return {{ data: body.slice(0, 2000), type: 'text' }};
            }}""")

            await page.close()
            return {"status": "ok", "data": data["data"], "type": data["type"]}
        except Exception as e:
            logger.error(f"Browser extract error: {e}")
            return {"status": "error", "error": str(e)}

    async def submit(self) -> dict:
        try:
            _, context = await self._get_browser()
            page = await context.new_page()

            submit_selector = 'button[type="submit"], input[type="submit"], button:has-text("Enviar"), button:has-text("Submit"), button:has-text("Send")'
            await page.wait_for_selector(submit_selector, timeout=10000)
            await page.click(submit_selector)

            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass

            url = page.url
            title = await page.title()
            await page.close()
            return {"status": "ok", "url": url, "title": title}
        except Exception as e:
            logger.error(f"Browser submit error: {e}")
            return {"status": "error", "error": str(e)}

    async def fill_form(self, fields: dict) -> dict:
        try:
            _, context = await self._get_browser()
            page = await context.new_page()
            filled = 0
            errors = []

            for field_name, value in fields.items():
                try:
                    selectors = [
                        f'input[name="{field_name}"]',
                        f'input[placeholder="{field_name}"]',
                        f'textarea[name="{field_name}"]',
                        f'textarea[placeholder="{field_name}"]',
                        f'label:has-text("{field_name}") input',
                        f'label:has-text("{field_name}") textarea',
                        f'input[id="{field_name}"]',
                        f'textarea[id="{field_name}"]',
                    ]
                    matched = False
                    for sel in selectors:
                        try:
                            await page.wait_for_selector(sel, timeout=3000)
                            await page.fill(sel, value)
                            filled += 1
                            matched = True
                            break
                        except:
                            continue
                    if not matched:
                        errors.append(f"Field '{field_name}' not found")
                except Exception as e:
                    errors.append(f"Field '{field_name}': {e}")

            await page.close()
            return {
                "status": "ok",
                "filled": filled,
                "total": len(fields),
                "errors": errors if errors else None,
            }
        except Exception as e:
            logger.error(f"Browser fill_form error: {e}")
            return {"status": "error", "error": str(e)}

    async def get_page_content(self) -> dict:
        try:
            _, context = await self._get_browser()
            page = await context.new_page()

            title = await page.title()
            url = page.url
            text = await page.evaluate("""
                () => {
                    const body = document.body.cloneNode(true);
                    const scripts = body.querySelectorAll('script, style, nav, footer, header, aside');
                    scripts.forEach(s => s.remove());
                    return body.innerText;
                }
            """)

            text = self._clean_text(text)
            await page.close()
            return {"status": "ok", "title": title, "url": url, "text": text}
        except Exception as e:
            logger.error(f"Browser get_page_content error: {e}")
            return {"status": "error", "error": str(e)}

    async def download_pdf(self, url: str = None) -> dict:
        try:
            _, context = await self._get_browser()
            page = await context.new_page()

            if url:
                logger.info(f"Browser navigate to PDF: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            else:
                pdf_link = await page.evaluate("""
                    () => {
                        const links = document.querySelectorAll('a[href$=".pdf"]');
                        return links.length > 0 ? links[0].href : null;
                    }
                """)
                if pdf_link:
                    logger.info(f"Browser found PDF link: {pdf_link}")
                    await page.goto(pdf_link, wait_until="domcontentloaded", timeout=30000)
                else:
                    raise Exception("No PDF link found on page")

            timestamp = int(asyncio.get_event_loop().time() * 1000)
            save_path = f"/tmp/mystic-pdf-{timestamp}.pdf"

            async with page.expect_download() as download_info:
                await page.evaluate("window.print()")
                download = await download_info
                await download.save_as(save_path)

            size = os.path.getsize(save_path)
            pages = 1
            await page.close()
            logger.info(f"PDF saved: {save_path} ({size} bytes)")
            return {"status": "ok", "path": save_path, "size": size, "pages": pages}
        except Exception as e:
            logger.error(f"Browser download_pdf error: {e}")
            return {"status": "error", "error": str(e)}

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
