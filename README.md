# TruthLens

**Hackathon ID:** `AZIS-DVBP77`

**Track:** Civic Tech — Misinformation Triage Platform (Code2Career hackathon by AzislyAI)

A neutral misinformation triage tool for a newsroom or citizen group: submit a viral claim, get automatic risk flags, and let a human reviewer verify it — without checking anyone's identity to do it.

## Tech stack

- **Backend + Frontend:** FastAPI + Jinja2 (server-rendered HTML, single deployable service)
- **Styling:** Tailwind CSS (CDN)
- **Database:** PostgreSQL (SQLAlchemy ORM); falls back to local SQLite if `DATABASE_URL` is not set
- **Hosting:** Render (single web service)

**Standard API:** Not implemented — no standard API spec was provided for this track. This submission is UI-driven and intended to be graded by a browser agent walking through the interface.

## Features

1. **Submit a claim** — `/submit` — text, source platform, category, optional source link
2. **Risk flags** — computed automatically on submit and on every edit (see `app/flagging.py`): Sensational (breaking/shocking/"share before deleted"), Shouting (>50% caps), Unsourced (no link). 2+ flags → High Risk.
3. **Review workflow** — `/claims/{id}` — a reviewer sets status (Unverified → Verified True / Verified False / Misleading) with a note
4. **Public feed** — `/feed` — all claims, filterable by category/status, sortable by Risk-first or Newest-first
5. **Detail view** — `/claims/{id}` — full text, flags, reviewer note, submitted/updated timestamps

No login/signup anywhere — every feature is open.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000`. Without a `DATABASE_URL` env var, it uses a local `truthlens.db` SQLite file automatically — no setup needed.

To use Postgres locally:
```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/truthlens
uvicorn app.main:app --reload
```

## Test flow (no credentials needed — nothing is gated)

1. Go to `/submit`, post a claim like `"BREAKING: shocking scandal, share before deleted!!"` with no source link → it lands as **High Risk** (2 flags: Sensational + Unsourced).
2. Go to `/feed` → see it pinned at the top under "🔥 Risk first" sort.
3. Click into it → see the flags, then set status to **Misleading** with a note → saved.
4. Edit the same claim, add a source link → flags recalculate and it drops out of High Risk.
5. Filter the feed by category/status to confirm filtering works.

## Deployment (Render)

1. Push this repo to GitHub.
2. On Render: **New → Web Service**, connect the repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. On Render: **New → PostgreSQL**, then copy its **Internal Database URL** into the web service's `DATABASE_URL` environment variable.
4. Deploy. The app creates its own tables on startup — no manual migration step.

## Project structure

```
app/
  main.py         # routes for all 5 features
  models.py       # Claim model
  flagging.py     # pure flag-detection logic (shared by submit + edit)
  database.py     # SQLAlchemy engine/session (Postgres or SQLite fallback)
  templates/       # Jinja2 templates (Tailwind CDN, no build step)
  static/
requirements.txt
DECISIONS.md
```

See `DECISIONS.md` for the reasoning behind the three Decision Points.
