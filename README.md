# Dori Narxlari — Django fullstack platforma

Retsept rasmidan yoki qidiruv orqali dori nomini aniqlab, bir xil ta'sir
moddasiga (INN) ega dorilarni yaqin dorixonalar bo'yicha narx solishtiradi,
referent narxdan sezilarli oshgan narxlarni belgilaydi.

To'liq Django (server-rendered shablonlar + Tailwind/HTMX CDN) — alohida
frontend build tizimi yo'q.

## Texnologiya

- Django 5.1 (`LoginRequiredMiddleware` — butun platforma login talab qiladi)
- PostgreSQL (geo-masofa — Python'da Haversine, PostGIS shart emas)
- Gemini API — retsept skaneri + nom normalizatsiya yordamchisi
- Tailwind CSS + HTMX (CDN, build kerak emas)

## O'rnatish

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # qiymatlarni to'ldiring (GEMINI_API_KEY va h.k.)
```

PostgreSQL kerak (Docker orqali eng oson):

```bash
docker run -d --name apteka-postgis -e POSTGRES_USER=neo -e POSTGRES_PASSWORD=neo \
  -e POSTGRES_DB=apteka_db -p 5433:5432 postgres:16
```

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser   # admin — FAQAT shu yo'l bilan yaratiladi
.venv/bin/python manage.py seed_demo         # demo ma'lumot (ixtiyoriy)
.venv/bin/python manage.py runserver
```

http://localhost:8000

## Rol tizimi

Uchta rol: `user`, `pharmacy_staff`, admin (=Django superuser).

- **Ro'yxatdan o'tish** — har doim oddiy `user` yaratadi.
- **`pharmacy_staff`** — FAQAT admin yaratgan bir martalik taklif havolasi
  orqali beriladi (Admin panel → dorixona → "Taklif havolasi yaratish" →
  havolani xodimga yuboring → u shu havoladan ro'yxatdan o'tadi).
- **Admin** — FAQAT serverdan, `createsuperuser` bilan. Saytda "adminni
  admin qilish" imkoniyati yo'q (xavfsizlik uchun ataylab).
- **Butun platforma login talab qiladi** — anonim foydalanuvchi hech narsa
  ko'ra olmaydi, login/ro'yxatdan o'tish sahifalaridan tashqari.

## Demo hisoblar (`seed_demo` dan keyin)

- `aziz` / `demo12345` — oddiy foydalanuvchi
- `dilnoza` / `demo12345` — pharmacy_staff (1-dorixonaga biriktirilgan)
- `admin` — `createsuperuser` bilan alohida yarating

## Sahifalar

| Yo'l | Kim uchun | Nima |
|---|---|---|
| `/` | hamma (login qilgan) | Qidiruv, ommabop dorilar, turkumlar |
| `/dori/<slug>/` | | Narxlar (masofa bo'yicha), muqobillar, narx tarixi, sevimli |
| `/turkumlar/`, `/turkum/<slug>/` | | Turkum bo'yicha ko'rish |
| `/retsept/` | | Retsept rasmini yuklash → tasdiqlash → narxlar |
| `/dorixona/<slug>/` | | Dorixona sahifasi: narxlar ro'yxati + sharhlar |
| `/hisob/profil/` | | Sevimlilar, qidiruv tarixi, retsept tarixi |
| `/dorixona/panel/` | `pharmacy_staff` | Narx qo'shish/yangilash, CSV yuklash |
| `/dorixona/admin-panel/` | admin | Dorixona qo'shish, taklif havolasi, statistika |
| `/boshqaruv/` | admin | Django admin — dori/turkum/alias/narx to'liq CRUD |

## Testlar

```bash
.venv/bin/pytest -v
```

`catalog/services.py`dagi `normalize_and_match` (4 qatlamli nom
moslashtirish: aniq → translit → fuzzy → Gemini) va
`pharmacies/services.py`dagi masofa/narx hisob-kitoblari qoplangan.

## Arxitektura

```
config/          — settings, urls, umumiy form_utils
accounts/        — custom User (role, pharmacy), login/register/profil
catalog/         — Substance, Category, Drug, DrugAlias, Favorite, SearchQuery
                   services.py — normalize_and_match
pharmacies/      — Pharmacy, PharmacyDrugPrice, PriceHistory, PharmacyInvite, PharmacyReview
                   services.py — haversine masofa, narx upsert+tarix
prescriptions/   — PrescriptionScan(Item) — Gemini orqali skanerlash tarixi
templates/       — bazaviy layout + har bir app'ning shablonlari
```
