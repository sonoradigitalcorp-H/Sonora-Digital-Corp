# Manual de Producto — Open Notebook

## ¿Qué es?
Alternativa open-source a NotebookLM. RAG sobre PDFs, páginas web, y documentos. Genera podcasts y resúmenes.

## Acceso
- **UI**: http://149.56.46.173:8502
- **API**: http://149.56.46.173:5055

## Uso
1. Subir PDFs o ingresar URLs
2. El sistema ingesta y vectoriza el contenido (Qdrant)
3. Chat con tus documentos
4. Generar podcast/resumen con un click

## Stack
- Frontend: Gradio/R (UI en :8502)
- Backend: FastAPI (API en :5055)
- Vector store: Qdrant
- LLM: DeepSeek vía Ollama

## Despliegue
```bash
docker compose -f infra/docker-compose.products.yml up -d open-notebook
```
