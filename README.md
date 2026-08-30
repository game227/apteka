# Dori narxlari platformasi

Retsept rasmidan dori nomlarini o'qib, ta'sir moddasi (INN) bo'yicha yaqin
dorixonalardagi narxlarni solishtiradi, referent narxdan oshgan narxlarni
belgilaydi. To'liq TZ: `TZ_BACKEND.md`.

## Ishga tushirish (bitta buyruq)

```bash
./start.sh
```

Talab qiladi: Docker (yoki podman, `docker` alias bilan), Python 3.11+,
Node.js. Birinchi ishga tushganda PostGIS konteynerini o'rnatadi, backend
`.venv`ni yaratadi, migratsiya va demo ma'lumotni kiritadi, frontendni
build qiladi. Tayyor bo'lgach:

**http://localhost:8000** — to'liq ilova (frontend + API bitta portda).

Swagger: http://localhost:8000/docs

## Loyiha tuzilishi

- `backend/` — FastAPI + PostgreSQL/PostGIS. Batafsil: `backend/README.md`
- `frontend/` — React + TypeScript + Tailwind. Batafsil: `frontend/README.md`

## Development rejimi

Frontend'da tez o'zgarish (hot-reload) kerak bo'lsa, backendni
`start.sh` orqali ishga tushirgandan keyin alohida:

```bash
cd frontend && npm run dev
```

`http://localhost:5173` backend'ga (`:8000`) CORS orqali ulanadi
(`frontend/.env` da `VITE_API_BASE_URL`).

## Demo hisoblar (mock login uchun)

Telegram bot sozlanmagan bo'lsa, login sahifasida test hisoblari
ko'rsatiladi: oddiy foydalanuvchi, dorixona xodimi (1-dorixonaga
biriktirilgan), admin. Haqiqiy Telegram Login Widget uchun
`backend/.env`ga `TELEGRAM_BOT_TOKEN` va `frontend/.env`ga
`VITE_TELEGRAM_BOT_USERNAME` qo'shing.
