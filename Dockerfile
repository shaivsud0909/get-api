# One image serving both the API (under /api) and the built frontend (at /).

FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# The browser calls the API on the same origin, under /api.
ENV VITE_API_BASE_URL=/api
RUN npm run build

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend /frontend/dist ./frontend/dist

ENV FRONTEND_DIST=/app/frontend/dist

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.server:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips=*"]
