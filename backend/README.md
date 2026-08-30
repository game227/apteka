# Dori narxlari platformasi — Backend

TZ_BACKEND.md asosida qurilgan FastAPI backend. Retsept rasmidan dori
nomlarini o'qib, ta'sir moddasi (INN) bo'yicha yaqin dorixonalardagi
narxlarni solishtiradi, referent narxdan chetlanishni belgilaydi.

## Texnologiya

- Python 3.11+ / FastAPI, SQLAlchemy 2.0 + Alembic
- PostgreSQL + PostGIS (geo-so'rovlar), GeoAlchemy2
- Gemini API (retsept skaneri + nom normalizatsiya yordamchisi)
- Telegram Login Widget orqali parolsiz auth (JWT)

## O'rnatish

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # keyin qiymatlarni to'ldiring
```

`.env`da kerakli maydonlar:
- `DATABASE_URL` — PostGIS yoqilgan Postgres bazasi. Unix socket orqali
  ulanish uchun host qismini bo'sh qoldiring: `postgresql+psycopg://user@/dbname`
- `TELEGRAM_BOT_TOKEN` — @BotFather'dan, Login Widget imzosini tekshirish uchun
- `GEMINI_API_KEY` — retsept skaneri va nom taxminlash uchun (bo'lmasa ham
  ishlaydi, faqat shu ikki funksiya cheklanadi)
- `JWT_SECRET` — production'da albatta o'zgartiring

## Baza va migratsiya

```bash
# PostGIS kengaytmasi yoqilgan bo'lishi kerak:
psql -d <dbname> -c "CREATE EXTENSION IF NOT EXISTS postgis;"

.venv/bin/alembic upgrade head
```

## Ishga tushirish

```bash
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs

## Demo ma'lumot (seed)

`scripts/seed_data.py` — **demo ma'lumot**, haqiqiy narx reestri emas: ~60 ta
ta'sir moddasi (INN), ularga biriktirilgan ~250 ta savdo nomi (kirillcha
alias'lari bilan), va Toshkentning 25 ta tumani bo'yicha taxminiy
dorixonalar. `scripts/seed.py` shu ma'lumotni bazaga yozadi (har bir
dorixonaga tasodifiy 30-50 ta dori narxi biriktiradi, ba'zilarini atayin
referent narxdan 20%+ oshirib qo'yadi — "qimmat" belgisini sinash uchun):

```bash
.venv/bin/python -m scripts.seed
```

## Testlar

```bash
.venv/bin/pytest tests/ -v
```

`app/services/normalization.py`dagi `normalize_and_match` — retsept
skaneri va qo'lda qidiruvning ikkalasi ham foydalanadigan asosiy modul —
izolyatsiyalangan (in-memory SQLite) testlar bilan qoplangan.

## Arxitektura qisqacha

```
app/
  models/       — SQLAlchemy 2.0 modellar (TZ 3-bo'lim sxemasi)
  schemas/      — Pydantic request/response modellari
  core/         — JWT (security.py), Telegram Login imzo tekshiruvi (telegram_auth.py)
  services/
    normalization.py — 4 qatlamli nom moslashtirish (aniq → translit → fuzzy → Gemini)
    geo.py            — PostGIS masofa so'rovlari
    pricing.py        — referent narxdan chetlanish, narx upsert + tarix
    gemini_vision.py  — retsept rasmini o'qish, noma'lum nom uchun taxmin
  routers/      — auth, drugs, prescriptions, pharmacy, admin
```

### Muhim qoidalar (TZ'dan)

- `pharmacy_drug_prices`da (pharmacy_id, drug_id) juftligi uchun bitta
  "joriy" yozuv — upsert. To'liq tarix `price_history`da (append-only).
- Referent narxdan chetlanish > 20% (`PRICE_DEVIATION_THRESHOLD`) —
  "shubhali/qimmat" deb belgilanadi.
- `pharmacy_staff` faqat o'z `pharmacy_id`siga tegishli narxlarni yozadi —
  har bir yozish endpointi `require_pharmacy_staff` dependency orqali buni
  majburlaydi.
- Alternativalar javobida doim tibbiy maslahat ogohlantirishi (`warning`
  maydoni) qaytadi.
- CSV yuklashda moslashmagan qatorlar hech narsa "taxmin qilib" saqlanmaydi
  — xatolar ro'yxatida qaytariladi, muvaffaqiyatli qatorlar alohida saqlanadi.

### TZ kontraktidan kengaytma

`POST /auth/telegram` request body'ga ixtiyoriy `invite_token` maydoni
qo'shildi (TZ 4-bo'limda yo'q edi). Sabab: `pharmacy_invites.used_by_user_id`
ustunini haqiqiy to'ldiradigan boshqa yo'l yo'q edi — admin yaratgan taklif
havolasidan Telegram login qilinganda frontend shu tokenni yuborsa,
foydalanuvchi avtomatik `pharmacy_staff` bo'ladi va `pharmacy_id`
biriktiriladi.

## Nima kiritilmagan (TZ 8-bo'lim)

Kraudsorsing (chek rasmi), kurs eslatmalari, butun respublika qamrovi,
`price_history` bo'yicha alohida ko'rish endpointi (jadval bor, yoziladi,
lekin uni o'qish uchun endpoint hali yo'q).
