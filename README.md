# Sheeghra Sahayata

**Smart Tourist Safety & Emergency Response Platform** — Hackathon MVP

Python end-to-end: **FastAPI** backend · **Supabase** (Postgres) · **HTML/CSS/JS** frontend (senior-friendly) · **Leaflet** maps · deploy to **Railway** + **Vercel**.

## Demo flow (core moment)

1. Tourist opens the app → phone login (any 6-digit OTP)
2. **Start Trip** → location sharing enabled
3. Tap big red **SOS** → `POST /sos` creates an `incidents` row
4. Authority **Dashboard** polls every 5s → marker + row appear live
5. Officer taps **Acknowledge** → **Resolve**

Silent SOS uses the same endpoint with `silent=true` (no flash animation).

---

## Project structure

```
/backend          FastAPI (auth, trip, sos, incidents, location, ai)
  /routers
  /scripts        privacy location cleanup cron
/web              HTML frontend (login, home/SOS, dashboard) + AI helper
/frontend         Legacy Reflex app (optional — HTML `/web` is the demo UI)
/supabase
  schema.sql      tables + seed incidents
```

---

## 1. Supabase setup

A project **sheeghra-sahayata** may already be provisioned. If you need to recreate:

1. Create a project at [supabase.com](https://supabase.com) (region: `ap-south-1` recommended)
2. Open **SQL Editor** → paste and run [`supabase/schema.sql`](supabase/schema.sql)
3. Copy **Project URL** + **service_role** key (Settings → API)
4. Put them in `backend/.env`:

```env
SUPABASE_URL=https://YOUR_REF.supabase.co
SUPABASE_KEY=your_service_role_or_anon_key
```

> The schema enables RLS with permissive demo policies so the anon key also works for judging. Prefer **service_role** on the backend in a real deployment.

### Tables

| Table | Purpose |
|-------|---------|
| `profiles` | Tourist profile (phone, medical, language, gender, age) |
| `trips` | Active / ended trips |
| `incidents` | SOS / Silent SOS events for the dashboard |
| `locations` | GPS breadcrumbs — **only while trip is active** |

Seed data includes 3 mock tourists + active/acknowledged/resolved incidents so the dashboard is not empty on first open.

---

## 2. Run backend locally

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # then fill SUPABASE_* 
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Endpoints

| Method | Path | Notes |
|--------|------|-------|
| POST | `/auth/signup` | Phone + any 6-digit OTP + profile |
| POST | `/auth/login` | Phone + any 6-digit OTP |
| POST | `/trip/start` | Creates `status=active` trip |
| POST | `/trip/end` | Sets `ended` — triggers privacy cleanup path |
| POST | `/sos` | `{user_id, trip_id?, lat, lon, silent?}` |
| GET | `/incidents` | Dashboard poll |
| PATCH | `/incidents/{id}` | `{status: acknowledged\|resolved}` |
| POST | `/location` | **403** if trip is not `active` |

---

## 3. Privacy-by-design (judging highlight)

Location rows are:

1. **Rejected by the API** unless `trip.status == 'active'` (`POST /location` → 403)
2. **Purged after trip ends** unless linked to an incident (`incident_id IS NOT NULL`)

Run the cleanup job:

```bash
cd backend
python scripts/cleanup_locations.py
```

Or schedule the SQL cron at the bottom of that script via Supabase `pg_cron`.

---

## 4. Run the HTML frontend (recommended)

The demo UI is plain **HTML/CSS/JS** (senior-friendly), served by FastAPI:

```bash
cd backend
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Open:
- Tourist login: http://127.0.0.1:8000/
- Home / SOS: http://127.0.0.1:8000/home
- Authority dashboard: http://127.0.0.1:8000/dashboard

Static files live in `/web`. The floating **AI** button answers safety questions via `POST /ai/chat` (built-in knowledge base; optional `OPENAI_API_KEY`).

> Legacy Reflex app remains under `/frontend` but is **not** required for the demo.

---

## 5. Deploy backend → Railway

```bash
cd backend
# Install Railway CLI, then:
railway login
railway init          # or: railway up -y
railway variable set SUPABASE_URL=https://YOUR_REF.supabase.co
railway variable set SUPABASE_KEY=your_key
railway up
railway domain        # get public HTTPS URL
```

Set Root Directory to `backend` if deploying from the monorepo root.  
`Procfile` / `railway.json` already start `uvicorn main:app`.

After deploy, set frontend:

```env
SHEEGHRA_API_URL=https://your-service.up.railway.app
```

---

## 6. Deploy frontend → Vercel

Reflex compiles to a web app. For a hackathon-friendly path:

**Option A — Vercel (static export)**

```bash
cd frontend
reflex export --frontend-only
# Deploy .web/build/client — vercel.json is included
vercel --cwd .
```

> Reflex state/WebSocket backend may still need a small always-on process. For a rock-solid live demo, also deploy the Reflex backend (`reflex run` / Reflex hosting) or keep `reflex run` on a laptop for the pitch.

**Option B — Run Reflex on Railway** (often more reliable for live demos)

```bash
cd frontend
railway up
# start: reflex run --env prod --backend-host 0.0.0.0
```

---

## 7. Geofence demo

Hardcoded in `frontend/sheeghra_sahayata/api.py`:

- Center: Connaught Place, New Delhi (`28.6315, 77.2167`)
- Radius: 800 m  
If the browser GPS (or demo coords) falls inside → red banner: *“You are entering a high-risk zone”*.

To force the banner in a pitch without being on site, temporarily set default `lat/lon` in `TouristState` to the zone center.

---

## Demo accounts (seeded)

| Phone | Name | Persona |
|-------|------|---------|
| `+919876543210` | Priya Sharma | Female 18–35 → Women’s helpline panel |
| `+919123456789` | Rajesh Kumar | 60+ → Hospital + Accessible Mode |
| `+919988877766` | Alex Tourist | Default emergency numbers |

OTP: any 6 digits (e.g. `123456`).

---