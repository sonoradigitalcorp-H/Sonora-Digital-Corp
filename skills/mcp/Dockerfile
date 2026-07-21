FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine
WORKDIR /app
RUN apk add --no-cache docker-cli git python3 make g++
COPY --from=builder /app/node_modules ./node_modules
COPY . .

RUN mkdir -p /app/adk/agents

ENV NODE_ENV=production
EXPOSE 18989

HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3   CMD wget --no-verbose --tries=1 -O /dev/null http://127.0.0.1:18989/api/health 2>/dev/null || exit 1

CMD ["node", "gateway/mcp-server-http.js"]
