from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, case
from typing import Optional

from app.database import Base, engine, get_db
from app.models import Claim
from app.flagging import compute_flags

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TruthLens")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

PLATFORMS = ["WhatsApp", "X", "Instagram", "Other"]
CATEGORIES = ["Politics", "Health", "Finance", "Other"]
STATUSES = ["Unverified", "Verified True", "Verified False", "Misleading"]

STATUS_BADGE = {
    "Unverified": "bg-gray-200 text-gray-700",
    "Verified True": "bg-green-100 text-green-700",
    "Verified False": "bg-red-100 text-red-700",
    "Misleading": "bg-yellow-100 text-yellow-800",
}


# ---------- Home ----------
@app.get("/")
def home():
    return RedirectResponse(url="/feed")


# ---------- Feature 1: Submit a claim ----------
@app.get("/submit")
def submit_form(request: Request):
    return templates.TemplateResponse(
        "submit.html",
        {"request": request, "platforms": PLATFORMS, "categories": CATEGORIES},
    )


@app.post("/submit")
def submit_claim(
    text: str = Form(...),
    source_platform: str = Form(...),
    category: str = Form(...),
    source_link: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    flags, risk_level = compute_flags(text, source_link)
    claim = Claim(
        text=text.strip(),
        source_platform=source_platform,
        category=category,
        source_link=(source_link or "").strip() or None,
        flags=flags,
        risk_level=risk_level,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return RedirectResponse(url=f"/claims/{claim.id}?submitted=1", status_code=303)


# ---------- Feature 4: Public feed ----------
@app.get("/feed")
def feed(
    request: Request,
    category: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = "risk",  # "risk" (default, DP1) or "recent"
    db: Session = Depends(get_db),
):
    query = db.query(Claim)
    if category and category != "All":
        query = query.filter(Claim.category == category)
    if status and status != "All":
        query = query.filter(Claim.status == status)

    if sort == "risk":
        # DP1: High Risk first, then by recency within each group
        risk_rank = case((Claim.risk_level == "High Risk", 0), else_=1)
        query = query.order_by(asc(risk_rank), desc(Claim.submitted_at))
    else:
        query = query.order_by(desc(Claim.submitted_at))

    claims = query.all()
    return templates.TemplateResponse(
        "feed.html",
        {
            "request": request,
            "claims": claims,
            "categories": ["All"] + CATEGORIES,
            "statuses": ["All"] + STATUSES,
            "selected_category": category or "All",
            "selected_status": status or "All",
            "sort": sort,
            "status_badge": STATUS_BADGE,
        },
    )


# ---------- Feature 5: Detail view ----------
@app.get("/claims/{claim_id}")
def claim_detail(claim_id: int, request: Request, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        return templates.TemplateResponse(
            "not_found.html", {"request": request}, status_code=404
        )
    return templates.TemplateResponse(
        "detail.html",
        {
            "request": request,
            "claim": claim,
            "statuses": STATUSES,
            "status_badge": STATUS_BADGE,
            "submitted": request.query_params.get("submitted") == "1",
            "reviewed": request.query_params.get("reviewed") == "1",
            "edited": request.query_params.get("edited") == "1",
        },
    )


# ---------- Feature 3: Review workflow ----------
@app.post("/claims/{claim_id}/review")
def review_claim(
    claim_id: int,
    status: str = Form(...),
    reviewer_note: str = Form(""),
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if claim:
        claim.status = status
        claim.reviewer_note = reviewer_note.strip() or None
        db.commit()
    return RedirectResponse(url=f"/claims/{claim_id}?reviewed=1", status_code=303)


# ---------- DP3: Editing (allowed, flags recalculate) ----------
@app.get("/claims/{claim_id}/edit")
def edit_form(claim_id: int, request: Request, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        return templates.TemplateResponse(
            "not_found.html", {"request": request}, status_code=404
        )
    return templates.TemplateResponse(
        "edit.html",
        {
            "request": request,
            "claim": claim,
            "platforms": PLATFORMS,
            "categories": CATEGORIES,
        },
    )


@app.post("/claims/{claim_id}/edit")
def edit_claim(
    claim_id: int,
    text: str = Form(...),
    source_platform: str = Form(...),
    category: str = Form(...),
    source_link: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if claim:
        claim.text = text.strip()
        claim.source_platform = source_platform
        claim.category = category
        claim.source_link = (source_link or "").strip() or None
        # DP3: flags + risk_level recalculate on every edit
        flags, risk_level = compute_flags(claim.text, claim.source_link)
        claim.flags = flags
        claim.risk_level = risk_level
        db.commit()
    return RedirectResponse(url=f"/claims/{claim_id}?edited=1", status_code=303)
