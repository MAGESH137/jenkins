# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first for cache efficiency
COPY package*.json ./
RUN npm ci --frozen-lockfile

# Copy source and build
COPY public ./public
COPY src    ./src
RUN npm run build

# ── Stage 2: Serve with nginx ─────────────────────────────────────────────────
FROM nginx:1.25-alpine

LABEL maintainer="devops-team"
LABEL description="Task Manager Frontend — Jenkins Practice"

# Copy built React app
COPY --from=builder /app/build /usr/share/nginx/html

# Custom nginx config for React Router SPA
RUN echo 'server { \
  listen 80; \
  root /usr/share/nginx/html; \
  index index.html; \
  location / { try_files $uri $uri/ /index.html; } \
  location /health { return 200 "OK"; add_header Content-Type text/plain; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget -qO- http://localhost/health || exit 1
