"""
PDF Generator — Crea documentos PDF desde comandos de voz.
Usa reportlab o fpdf2.
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("voice-realtime.pdf")

class PDFGenerator:
    """
    Genera PDFs (facturas, reportes, documentos) desde texto.
    """
    
    async def generate(self, title: str, content: str, 
                       output_path: Optional[str] = None) -> dict:
        """
        Genera un PDF con título y contenido.
        Si no se especifica output_path, guarda en /tmp/.
        """
        try:
            # Intentar usar fpdf2
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Título
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, title, ln=True, align="C")
            pdf.ln(10)
            
            # Contenido
            pdf.set_font("Helvetica", "", 12)
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                # Detectar encabezados
                if line.startswith('# '):
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.cell(0, 10, line[2:], ln=True)
                    pdf.set_font("Helvetica", "", 12)
                elif line.startswith('## '):
                    pdf.set_font("Helvetica", "B", 13)
                    pdf.cell(0, 10, line[3:], ln=True)
                    pdf.set_font("Helvetica", "", 12)
                else:
                    pdf.multi_cell(0, 7, line)
            
            if not output_path:
                import time
                output_path = f"/tmp/mystic-pdf-{int(time.time())}.pdf"
            
            pdf.output(output_path)
            size = Path(output_path).stat().st_size
            
            return {
                "status": "ok",
                "path": output_path,
                "size": size,
                "filename": Path(output_path).name,
            }
            
        except ImportError:
            # Fallback: generar PDF básico con reportlab
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                
                if not output_path:
                    import time
                    output_path = f"/tmp/mystic-pdf-{int(time.time())}.pdf"
                
                doc = SimpleDocTemplate(output_path, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                
                story.append(Paragraph(f"<b>{title}</b>", styles['Title']))
                story.append(Spacer(1, 12))
                
                for line in content.split('\n'):
                    if line.strip():
                        story.append(Paragraph(line, styles['Normal']))
                        story.append(Spacer(1, 6))
                
                doc.build(story)
                size = Path(output_path).stat().st_size
                
                return {
                    "status": "ok",
                    "path": output_path,
                    "size": size,
                    "filename": Path(output_path).name,
                }
            except ImportError:
                return {
                    "status": "error",
                    "error": "No hay librería PDF instalada. Instala: pip install fpdf2"
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
