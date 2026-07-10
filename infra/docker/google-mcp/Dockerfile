FROM python:3.12-slim

WORKDIR /app

COPY products/google-mcp/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY products/google-mcp/ .

EXPOSE 8767
CMD ["python", "server.py"]
