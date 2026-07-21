FROM node:24-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates curl wget git \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g openclaw@latest

RUN mkdir -p /root/.openclaw /root/.openclaw/extensions /root/.openclaw/memory

EXPOSE 18789

ENV OPENCLAW_GATEWAY_PORT=18789

COPY openclaw.json /root/.openclaw/openclaw.json

CMD ["openclaw", "gateway", "run", "--port", "18789"]
