"""Radio Waver beheer-API.

Publiek:  GET /api/content  (mededeling + partners + agenda voor de website)
Beheer:   /api/admin/*      (achter Keycloak, rol 'beheerder')
"""
import os
import shutil
import uuid
from typing import Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile

from . import db
from .auth import require_admin

app = FastAPI(title="Radio Waver API")

UPLOAD_DIR = os.path.join(os.environ.get("DATA_DIR", "/data"), "uploads")
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MESSAGE_MAX = 200
AUTHOR_MAX = 40


@app.on_event("startup")
def _startup():
    db.init_db()
    os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/content")
def content():
    """Publieke inhoud voor de website."""
    return {
        "announcement": {
            "enabled": db.get_setting("announcement_enabled", "0") == "1",
            "text": db.get_setting("announcement_text", ""),
        },
        "messages": {
            "enabled": db.get_setting("messages_enabled", "0") == "1",
            "items": [
                {"text": m["text"], "author": m["author"]}
                for m in db.list_messages("approved")
            ],
        },
        "events": db.list_rows("events"),
        "partners": db.list_rows("partners"),
    }


@app.post("/api/messages")
def submit_message(payload: dict):
    """Publiek: een boodschap insturen (komt in moderatie, enkel als de module openstaat)."""
    if db.get_setting("messages_enabled", "0") != "1":
        raise HTTPException(status_code=403, detail="Live berichten staan momenteel niet open.")
    text = str(payload.get("text", "")).strip()[:MESSAGE_MAX]
    author = str(payload.get("author", "")).strip()[:AUTHOR_MAX]
    if not text:
        raise HTTPException(status_code=400, detail="Lege boodschap.")
    db.insert("messages", {"text": text, "author": author, "status": "pending"})
    return {"ok": True}


# --------------------------------------------------------------------------
# Uploads
# --------------------------------------------------------------------------
def _save_upload(file: Optional[UploadFile]):
    if file is None or not file.filename:
        return None
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="alleen afbeeldingen toegelaten")
    name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR, name), "wb") as out:
        shutil.copyfileobj(file.file, out)
    return f"/uploads/{name}"


def _delete_upload(url):
    if url and url.startswith("/uploads/"):
        try:
            os.remove(os.path.join(UPLOAD_DIR, os.path.basename(url)))
        except OSError:
            pass


# --------------------------------------------------------------------------
# Mededeling (live-update balk)
# --------------------------------------------------------------------------
@app.get("/api/admin/announcement")
def get_announcement(_=Depends(require_admin)):
    return {
        "enabled": db.get_setting("announcement_enabled", "0") == "1",
        "text": db.get_setting("announcement_text", ""),
    }


@app.put("/api/admin/announcement")
def put_announcement(payload: dict, _=Depends(require_admin)):
    db.set_setting("announcement_enabled", "1" if payload.get("enabled") else "0")
    db.set_setting("announcement_text", str(payload.get("text", "")).strip())
    return {"ok": True}


# --------------------------------------------------------------------------
# Live berichten (gemodereerd) — moderatie
# --------------------------------------------------------------------------
@app.get("/api/admin/messages")
def admin_messages(_=Depends(require_admin)):
    return {
        "enabled": db.get_setting("messages_enabled", "0") == "1",
        "items": db.list_messages(),
    }


@app.put("/api/admin/messages/settings")
def messages_settings(payload: dict, _=Depends(require_admin)):
    db.set_setting("messages_enabled", "1" if payload.get("enabled") else "0")
    return {"ok": True}


@app.post("/api/admin/messages")
def admin_create_message(payload: dict, _=Depends(require_admin)):
    """Beheerder maakt zelf een bericht (standaard meteen goedgekeurd)."""
    text = str(payload.get("text", "")).strip()[:MESSAGE_MAX]
    if not text:
        raise HTTPException(status_code=400, detail="Lege boodschap.")
    author = str(payload.get("author", "")).strip()[:AUTHOR_MAX]
    status = payload.get("status", "approved")
    if status not in ("pending", "approved"):
        status = "approved"
    rid = db.insert("messages", {"text": text, "author": author, "status": status})
    return db.get_row("messages", rid)


@app.put("/api/admin/messages/{message_id}")
def admin_update_message(message_id: int, payload: dict, _=Depends(require_admin)):
    row = db.get_row("messages", message_id)
    if not row:
        raise HTTPException(status_code=404, detail="bericht niet gevonden")
    data = {}
    if "text" in payload:
        data["text"] = str(payload["text"]).strip()[:MESSAGE_MAX]
    if "author" in payload:
        data["author"] = str(payload["author"]).strip()[:AUTHOR_MAX]
    if "status" in payload and payload["status"] in ("pending", "approved"):
        data["status"] = payload["status"]
    db.update("messages", message_id, data)
    return db.get_row("messages", message_id)


@app.post("/api/admin/messages/{message_id}/approve")
def approve_message(message_id: int, _=Depends(require_admin)):
    db.set_message_status(message_id, "approved")
    return {"ok": True}


@app.delete("/api/admin/messages/{message_id}")
def delete_message(message_id: int, _=Depends(require_admin)):
    db.delete("messages", message_id)
    return {"ok": True}


# --------------------------------------------------------------------------
# Agenda (events) — met affiche/logo
# --------------------------------------------------------------------------
@app.get("/api/admin/events")
def list_events(_=Depends(require_admin)):
    return db.list_rows("events")


@app.post("/api/admin/events")
def create_event(
    name: str = Form(""),
    label: str = Form(""),
    time: str = Form(""),
    description: str = Form(""),
    sort: int = Form(0),
    affiche: Optional[UploadFile] = File(None),
    _=Depends(require_admin),
):
    rid = db.insert(
        "events",
        {
            "name": name.strip(),
            "label": label.strip(),
            "time": time.strip(),
            "description": description.strip(),
            "affiche": _save_upload(affiche),
            "sort": sort,
        },
    )
    return db.get_row("events", rid)


@app.put("/api/admin/events/{event_id}")
def update_event(
    event_id: int,
    name: str = Form(""),
    label: str = Form(""),
    time: str = Form(""),
    description: str = Form(""),
    sort: int = Form(0),
    affiche: Optional[UploadFile] = File(None),
    _=Depends(require_admin),
):
    row = db.get_row("events", event_id)
    if not row:
        raise HTTPException(status_code=404, detail="event niet gevonden")
    data = {
        "name": name.strip(),
        "label": label.strip(),
        "time": time.strip(),
        "description": description.strip(),
        "sort": sort,
    }
    new_affiche = _save_upload(affiche)
    if new_affiche:
        _delete_upload(row.get("affiche"))
        data["affiche"] = new_affiche
    db.update("events", event_id, data)
    return db.get_row("events", event_id)


@app.delete("/api/admin/events/{event_id}")
def delete_event(event_id: int, _=Depends(require_admin)):
    row = db.get_row("events", event_id)
    if row:
        _delete_upload(row.get("affiche"))
        db.delete("events", event_id)
    return {"ok": True}


# --------------------------------------------------------------------------
# Partners — met logo
# --------------------------------------------------------------------------
@app.get("/api/admin/partners")
def list_partners(_=Depends(require_admin)):
    return db.list_rows("partners")


@app.post("/api/admin/partners")
def create_partner(
    name: str = Form(...),
    url: str = Form(""),
    sort: int = Form(0),
    logo: Optional[UploadFile] = File(None),
    _=Depends(require_admin),
):
    rid = db.insert(
        "partners",
        {"name": name.strip(), "url": url.strip(), "logo": _save_upload(logo), "sort": sort},
    )
    return db.get_row("partners", rid)


@app.put("/api/admin/partners/{partner_id}")
def update_partner(
    partner_id: int,
    name: str = Form(...),
    url: str = Form(""),
    sort: int = Form(0),
    logo: Optional[UploadFile] = File(None),
    _=Depends(require_admin),
):
    row = db.get_row("partners", partner_id)
    if not row:
        raise HTTPException(status_code=404, detail="partner niet gevonden")
    data = {"name": name.strip(), "url": url.strip(), "sort": sort}
    new_logo = _save_upload(logo)
    if new_logo:
        _delete_upload(row.get("logo"))
        data["logo"] = new_logo
    db.update("partners", partner_id, data)
    return db.get_row("partners", partner_id)


@app.delete("/api/admin/partners/{partner_id}")
def delete_partner(partner_id: int, _=Depends(require_admin)):
    row = db.get_row("partners", partner_id)
    if row:
        _delete_upload(row.get("logo"))
        db.delete("partners", partner_id)
    return {"ok": True}
