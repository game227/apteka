#!/usr/bin/env bash
# Butun loyihani (DB + backend + frontend) bitta buyruq bilan ishga tushiradi.
# Ishlatish:  ./start.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== 1/4: PostGIS ma'lumotlar bazasi (Docker) =="
if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx apteka-postgis; then
  echo "allaqachon ishlab turibdi"
elif docker ps -a --format '{{.Names}}' 2>/dev/null | grep -qx apteka-postgis; then
  docker start apteka-postgis >/dev/null
else
  docker run -d --name apteka-postgis \
    -e POSTGRES_USER=neo -e POSTGRES_PASSWORD=neo -e POSTGRES_DB=apteka_db \
    -p 5433:5432 docker.io/postgis/postgis:16-3.4 >/dev/null
fi

echo -n "bazaga ulanishni kutish"
until docker exec apteka-postgis pg_isready -U neo >/dev/null 2>&1; do
  echo -n "."
  sleep 1
done
echo " tayyor"
docker exec apteka-postgis psql -U neo -d apteka_db -c "CREATE EXTENSION IF NOT EXISTS postgis;" >/dev/null

echo "== 2/4: Backend =="
cd backend
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi
.venv/bin/alembic upgrade head

HAS_DATA=$(.venv/bin/python -c "
from app.db import SessionLocal
from app.models.substance import Substance
s = SessionLocal()
print(s.query(Substance).count())
s.close()
" 2>/dev/null || echo 0)
if [ "$HAS_DATA" = "0" ]; then
  echo "demo ma'lumot kiritilmoqda..."
  .venv/bin/python -m scripts.seed
fi

pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/apteka-backend.log 2>&1 &
disown
cd ..

echo "== 3/4: Frontend build (bitta-portli rejim uchun) =="
cd frontend
if [ ! -d node_modules ]; then
  npm install --silent
fi
VITE_API_BASE_URL="" VITE_USE_MOCK=false npm run build --silent
cd ..

echo "== 4/4: Sog'liqni tekshirish =="
sleep 2
for i in $(seq 1 10); do
  if curl -sf http://localhost:8000/health > /dev/null; then break; fi
  sleep 1
done
curl -sf http://localhost:8000/health > /dev/null && echo "backend OK" || echo "backend JAVOB BERMAYAPTI — /tmp/apteka-backend.log ni tekshiring"

echo ""
echo "Tayyor. Brauzerda oching:  http://localhost:8000"
echo "(Backend + frontend shu bitta portda birga ishlaydi)"
