from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_file
import pandas as pd
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path
import uuid
import json
from io import BytesIO
import re
from urllib.parse import urlparse
import os
import logging
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)

# ----------
# App config
# ----------
def _get_env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default


def _configure_app(a: Flask) -> None:
    a.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")
    max_mb = _get_env_int("MAX_UPLOAD_MB", 16)
    a.config["MAX_CONTENT_LENGTH"] = max_mb * 1024 * 1024


_configure_app(app)

# Temp upload root (system temp dir by default)
UPLOAD_ROOT = Path(os.getenv("UPLOAD_ROOT", str(Path(tempfile.gettempdir()) / "excel_viewer_uploads")))
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

# TTL for uploaded sessions (hours)
UPLOAD_TTL_HOURS = _get_env_int("UPLOAD_TTL_HOURS", 24)

# Logger
logger = logging.getLogger("excel_viewer")
if not logger.handlers:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

ALLOWED_EXTENSIONS = {"xlsx", "csv"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_token_dir(token: str) -> Path:
    d = UPLOAD_ROOT / token
    d.mkdir(parents=True, exist_ok=True)
    return d


def _cleanup_old_tokens_loop():
    """Background loop to delete old token directories by mtime."""
    interval_seconds = 30 * 60  # every 30 minutes
    ttl = timedelta(hours=UPLOAD_TTL_HOURS)
    while True:
        try:
            now = datetime.utcnow()
            if UPLOAD_ROOT.exists():
                for p in UPLOAD_ROOT.iterdir():
                    try:
                        if not p.is_dir():
                            continue
                        mtime = datetime.utcfromtimestamp(p.stat().st_mtime)
                        if now - mtime > ttl:
                            for sub in p.glob("**/*"):
                                try:
                                    if sub.is_file():
                                        sub.unlink(missing_ok=True)
                                except Exception:
                                    pass
                            try:
                                p.rmdir()
                            except Exception:
                                pass
                    except Exception:
                        continue
        except Exception as e:
            logger.warning("cleanup loop error: %s", e)
        time.sleep(interval_seconds)


# Start cleanup thread (daemon)
try:
    t = threading.Thread(target=_cleanup_old_tokens_loop, name="uploads-cleaner", daemon=True)
    t.start()
except Exception as e:
    logger.warning("failed starting cleanup thread: %s", e)


# -----------------
# Simple i18n layer
# -----------------
I18N_DIR = Path(__file__).parent / "i18n"
SUPPORTED_LANGS = ("en", "vi")
_locale_cache: dict[str, dict] = {}


def _load_locale_from_disk(code: str) -> dict:
    try:
        with open(I18N_DIR / f"{code}.json", "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("failed to load locale %s: %s", code, exc)
        return {}


def _get_locale(code: str) -> dict:
    if code not in SUPPORTED_LANGS:
        return {}
    path = I18N_DIR / f"{code}.json"
    try:
        mtime = path.stat().st_mtime
    except FileNotFoundError:
        mtime = None
    cached = _locale_cache.get(code)
    if cached and cached.get("mtime") == mtime:
        return cached.get("data", {})
    data = _load_locale_from_disk(code) if mtime is not None else {}
    _locale_cache[code] = {"mtime": mtime, "data": data}
    return data


def _detect_lang_from_header() -> str:
    header = request.headers.get("Accept-Language", "").lower()
    if header.startswith("vi"):
        return "vi"
    return "en"


def get_lang() -> str:
    lang = request.args.get("lang") or session.get("lang")
    if lang not in SUPPORTED_LANGS:
        lang = _detect_lang_from_header()
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    session["lang"] = lang
    return lang


def tr(key: str) -> str:
    lang = getattr(g, "lang", None) or session.get("lang") or "en"
    locale = _get_locale(lang)
    if key in locale:
        return locale[key]
    fallback = _get_locale("en")
    return fallback.get(key, key)


@app.before_request
def _bind_lang():
    g.lang = get_lang()


@app.context_processor
def _inject_t():
    return {"t": tr, "current_lang": getattr(g, "lang", "en")}


@app.route("/set-lang/<lang>")
def set_lang_route(lang: str):
    if lang not in SUPPORTED_LANGS:
        lang = "en"
    session["lang"] = lang
    nxt = request.args.get("next") or request.referrer or url_for("index")
    try:
        p = urlparse(nxt)
        # Only allow relative paths
        path = p.path or "/"
        unsafe = {url_for("render_view"), url_for("render_multi"), url_for("upload_files")}
        if path in unsafe:
            nxt = url_for("index")
    except Exception:
        nxt = url_for("index")
    return redirect(nxt)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.files.getlist("files")
    if not files:
        flash(tr("flash_choose_at_least_one_file"))
        return redirect(url_for("index"))

    token = uuid.uuid4().hex
    dest_dir = get_token_dir(token)

    saved_any = False
    for f in files:
        if not f or f.filename == "":
            continue
        if not allowed_file(f.filename):
            continue
        filename = secure_filename(f.filename)
        path = dest_dir / filename
        f.save(path)
        saved_any = True

    if not saved_any:
        flash(tr("flash_no_valid_files"))
        return redirect(url_for("index"))

    return redirect(url_for("select", token=token))


@app.route("/select/<token>", methods=["GET"])
def select(token: str):
    dest_dir = get_token_dir(token)
    files = []
    for p in sorted(dest_dir.iterdir()):
        if not p.is_file():
            continue
        filename = p.name
        if not allowed_file(filename):
            continue
        ext = filename.rsplit(".", 1)[1].lower()
        if ext == "csv":
            sheets = ["CSV"]
        else:
            try:
                xls = pd.ExcelFile(p)
                sheets = list(xls.sheet_names)
            except Exception:
                sheets = []
        files.append({"filename": filename, "ext": ext, "sheets": sheets})

    if not files:
        flash(tr("flash_uploaded_unreadable"))
        return redirect(url_for("index"))

    return render_template("select.html", token=token, files=files)


@app.route("/render", methods=["POST"])
def render_view():
    token = request.form.get("token")
    selection = request.form.get("selection")
    if not token or not selection:
        flash(tr("flash_invalid_selection"))
        return redirect(url_for("index"))

    if "::" in selection:
        filename, sheet_name = selection.split("::", 1)
    else:
        filename, sheet_name = selection, ""

    dest_dir = get_token_dir(token)
    path = dest_dir / filename
    if not path.exists():
        flash(tr("flash_selected_file_not_found"))
        return redirect(url_for("index"))

    ext = filename.rsplit(".", 1)[1].lower()

    try:
        if ext == "csv":
            df = pd.read_csv(path)
            df = df.fillna("")
            table_html = df.to_html(classes="table table-striped table-sm", index=False, border=0, na_rep="")
            return render_template("view.html", filename=filename, sheet_name=None, table_html=table_html, token=token)
        else:
            xls = pd.ExcelFile(path)
            target_sheet = sheet_name or (xls.sheet_names[0] if xls.sheet_names else None)
            if not target_sheet:
                flash(tr("flash_no_sheets_found"))
                return redirect(url_for("select", token=token))
            df = xls.parse(target_sheet)
            df = df.fillna("")
            table_html = df.to_html(classes="table table-striped table-sm", index=False, border=0, na_rep="")
            return render_template("view.html", filename=filename, sheet_name=target_sheet, table_html=table_html, token=token)
    except Exception as e:
        flash(f"{tr('flash_failed_open_file')}: {e}")
        return redirect(url_for("select", token=token))


@app.route("/render_multi", methods=["POST"])
def render_multi():
    token = request.form.get("token")
    selections = request.form.getlist("selection")
    if not token or not selections:
        flash(tr("flash_select_at_least_one_sheet"))
        return redirect(url_for("index"))

    dest_dir = get_token_dir(token)

    views = []
    for sel in selections:
        if "::" in sel:
            filename, sheet_name = sel.split("::", 1)
        else:
            filename, sheet_name = sel, ""

        path = dest_dir / filename
        if not path.exists():
            continue

        ext = filename.rsplit(".", 1)[1].lower()
        try:
            if ext == "csv":
                df = pd.read_csv(path)
                df = df.fillna("")
                label = f"{filename}"
                table_html = df.to_html(classes="table table-striped table-sm", index=False, border=0, na_rep="")
                views.append({
                    "id": f"v_{len(views)}",
                    "label": label,
                    "filename": filename,
                    "sheet_name": None,
                    "table_html": table_html,
                })
            else:
                xls = pd.ExcelFile(path)
                target_sheet = sheet_name or (xls.sheet_names[0] if xls.sheet_names else None)
                if not target_sheet:
                    continue
                df = xls.parse(target_sheet)
                df = df.fillna("")
                label = f"{filename} - {target_sheet}"
                table_html = df.to_html(classes="table table-striped table-sm", index=False, border=0, na_rep="")
                views.append({
                    "id": f"v_{len(views)}",
                    "label": label,
                    "filename": filename,
                    "sheet_name": target_sheet,
                    "table_html": table_html,
                })
        except Exception:
            continue

    if not views:
        flash(tr("flash_selected_sheets_could_not_be_opened"))
        return redirect(url_for("select", token=token))

    return render_template("multi_view.html", token=token, views=views)


def _sanitize_sheet_name(name: str) -> str:
    # Remove invalid characters: : \ / ? * [ ]
    name = re.sub(r"[:\\/\?\*\[\]]", " ", name)
    name = name.strip() or "Sheet"
    return name[:31]


@app.route("/export", methods=["POST"])
def export_excel():
    payload = request.get_json(silent=True) or {}
    sheets = payload.get("sheets")
    out_name = payload.get("filename") or "export.xlsx"
    if not sheets or not isinstance(sheets, list):
        return {"error": tr("flash_select_at_least_one_sheet")}, 400

    buf = BytesIO()
    used_names = set()

    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for item in sheets:
            headers = item.get("headers") or []
            rows = item.get("rows") or []
            sheet_name = item.get("name") or "Sheet"
            sheet_name = _sanitize_sheet_name(sheet_name)
            # Ensure uniqueness
            base = sheet_name
            i = 1
            while sheet_name in used_names:
                suffix = f"_{i}"
                sheet_name = _sanitize_sheet_name(base[: (31 - len(suffix))] + suffix)
                i += 1
            used_names.add(sheet_name)

            try:
                df = pd.DataFrame(rows, columns=headers)
            except Exception:
                # Fallback: best-effort
                df = pd.DataFrame(rows)
                if headers:
                    df.columns = headers[: len(df.columns)]
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=out_name, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)






