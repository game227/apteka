# Dori narxlari platformasi — Frontend

React 19 + TypeScript + React Router + Tailwind CSS. Backend'ning
TZ_BACKEND.md 4-bo'limidagi 14 endpoint kontraktiga to'liq mos ravishda
qurilgan (tiplar: `src/types/api.ts`).

Butun loyihani ishga tushirish uchun repo ildizidagi `../start.sh`dan
foydalaning. Faqat frontend ustida ishlayotgan bo'lsangiz:

## O'rnatish va ishga tushirish

```bash
npm install
cp .env.example .env   # kerak bo'lsa qiymatlarni tahrirlang
npm run dev
```

http://localhost:5173 — backend `.env`dagi `VITE_API_BASE_URL` orqali
(standart: `http://localhost:8000`, CORS orqali) ulanadi.

## `.env` maydonlari

- `VITE_API_BASE_URL` — backend manzili. Backend bilan bitta portda ishlash
  uchun (production build) bo'sh qoldiring — nisbiy so'rovlar ishlatiladi.
- `VITE_USE_MOCK` — `true` bo'lsa, backend'siz to'liq ishlaydigan mock
  server (`src/api/mock/`) ishlatiladi — dizayn/UI ustida backend'siz
  ishlash uchun qulay.
- `VITE_TELEGRAM_BOT_USERNAME` — bo'lsa, haqiqiy Telegram Login Widget
  ko'rsatiladi; bo'lmasa (yoki mock rejimda) login sahifasida test
  hisoblari bilan kirish tugmalari chiqadi (oddiy foydalanuvchi, dorixona
  xodimi, admin).

## Sahifalar

- `/` — dori qidirish
- `/dori/:drugId` — narxlar (masofa bo'yicha saralangan) + muqobil dorilar
- `/retsept` — retsept rasmini yuklash, aniqlangan dorilarni tasdiqlash
- `/kirish` — Telegram login (`?invite=` bilan — dorixona xodimi taklifi)
- `/dorixona` — dorixona paneli (faqat `pharmacy_staff`): narxlarni
  qo'lda/CSV orqali yangilash
- `/admin` — admin panel (faqat `admin`): dorixona qo'shish, taklif
  havolasi yaratish

## Build

```bash
npm run build   # tsc -b && vite build -> dist/
npm run lint
```

`dist/`ni backend orqali bitta portda serve qilish uchun `VITE_API_BASE_URL=""`
bilan build qiling (`../start.sh` shuni avtomatik bajaradi).
