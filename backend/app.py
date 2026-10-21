"""Servidor da avaliação de Python do 8º ano."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import socket
import threading
import time
import uuid
from datetime import timedelta
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory, session
from werkzeug.exceptions import HTTPException

from excel_sync import encerramento_texto, situacao, sync_all, sync_class
from grader import grade
from mailer import TEACHER_EMAIL, incentive, student_message
from mailer import Mailer
from questions_bank import (
    MAX_SCORE_CENTS,
    QUESTIONS,
    TOTAL_QUESTIONS,
    explanation_for,
    format_score,
    public_question,
    question_points_cents,
)
from storage import TURMAS, Store, format_br

ROOT = Path(__file__).resolve().parent.parent
BACKEND = Path(__file__).resolve().parent
NAME_RE = re.compile(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]*(?: [A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'’\-]*)+$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{32,80}$")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def json_error(message: str, status: int):
    response = jsonify({"error": message, "salvo": False})
    response.status_code = status
    return response


def parse_uuid(value: str) -> str | None:
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, TypeError, AttributeError):
        return None


def normalize_name(nome: str) -> str:
    if not isinstance(nome, str):
        raise ValueError("Informe o nome completo.")
    cleaned = " ".join(nome.strip().split())
    if len(cleaned) < 5 or len(cleaned) > 120 or NAME_RE.fullmatch(cleaned) is None:
        raise ValueError("Informe o nome e o sobrenome, usando apenas letras.")
    return cleaned


def passwords_match(given: str, expected: str) -> bool:
    return hmac.compare_digest(
        hashlib.sha256(given.encode("utf-8")).hexdigest(),
        hashlib.sha256(expected.encode("utf-8")).hexdigest(),
    )


def mail_from_env() -> dict:
    return {
        "host": os.environ.get("SMTP_HOST", ""),
        "port": os.environ.get("SMTP_PORT", "587"),
        "user": os.environ.get("SMTP_USER", ""),
        "password": os.environ.get("SMTP_PASSWORD", ""),
        "sender": os.environ.get("SMTP_FROM", ""),
        "recipient": os.environ.get("SMTP_TO", TEACHER_EMAIL),
        "tls": os.environ.get("SMTP_TLS", "true"),
    }


def load_secret(data_dir: Path) -> str:
    path = data_dir / "secret_key.txt"
    if path.exists():
        current = path.read_text(encoding="utf-8").strip()
        if current:
            return current
    secret = secrets.token_hex(32)
    path.write_text(secret, encoding="utf-8")
    return secret


def progress_of(row: dict) -> dict:
    answered = int(row["acertos"]) + int(row["erros"])
    cents = int(row.get("nota_cents") or 0)
    return {
        "question": row["current_question"],
        "total": TOTAL_QUESTIONS,
        "respondidas": answered,
        "acertos": row["acertos"],
        "erros": row["erros"],
        "nota_cents": cents,
        "pontuacao": round(cents / 100, 2),
        "pontuacao_formatada": format_score(cents),
        "progresso": int(answered / TOTAL_QUESTIONS * 100),
        "phase": row["phase"],
    }


def student_card(row: dict) -> dict:
    return {
        "nome": row["nome"],
        "turma": row["turma"],
        "started_at": format_br(row["started_at"]),
    }


def public_response(response: dict) -> dict:
    if isinstance(response.get("answers"), dict):
        return {"answers": response["answers"]}
    if isinstance(response.get("option"), str):
        return {"option": response["option"]}
    if isinstance(response.get("code"), str):
        return {"code": response["code"]}
    return {}


def result_of(store: Store, row: dict, email_configured: bool) -> dict:
    acertos = int(row["acertos"])
    cents = int(row.get("nota_cents") or 0)
    return {
        "nome": row["nome"],
        "turma": row["turma"],
        "started_at": format_br(row["started_at"]),
        "finished_at": format_br(row["finished_at"]),
        "acertos": acertos,
        "erros": int(row["erros"]),
        "nota": round(cents / 100, 2),
        "nota_formatada": format_score(cents),
        "aproveitamento": int(cents * 100 / MAX_SCORE_CENTS),
        "mensagem": (
            "A avaliação foi encerrada porque houve mais de 3 tentativas de copiar, colar ou capturar a tela."
            if row.get("encerramento") == "seguranca"
            else incentive(cents)
        ),
        "encerramento": encerramento_texto(row),
        "registro": (
            "O professor foi avisado na planilha: prova encerrada por tentativa de burlar a segurança. "
            if row.get("encerramento") == "seguranca"
            else ""
        ) + student_message(
            True,
            bool(row["excel_synced"]),
            bool(row["email_sent"]),
            email_configured,
        ),
        "salvo": True,
        "revisao": store.review(row["attempt_id"]),
    }


def admin_view(row: dict, email_configured: bool) -> dict:
    saved = bool(row["saved"])
    if row["email_sent"]:
        email_status = "Enviado"
    elif not email_configured:
        email_status = "Não configurado"
    else:
        email_status = "Pendente"
    return {
        "attempt_id": row["attempt_id"],
        "nome": row["nome"],
        "turma": row["turma"],
        "started_at": format_br(row["started_at"]),
        "finished_at": format_br(row["finished_at"]) if row["finished_at"] else "",
        "acertos": row["acertos"] if saved else None,
        "erros": row["erros"] if saved else None,
        "nota": round(int(row.get("nota_cents") or 0) / 100, 2) if saved else None,
        "nota_formatada": format_score(int(row.get("nota_cents") or 0)) if saved else None,
        "aproveitamento": int(int(row.get("nota_cents") or 0) * 100 / MAX_SCORE_CENTS) if saved else None,
        "status": "Concluída" if saved else "Em andamento",
        "encerramento": encerramento_texto(row) if saved else "Em andamento",
        "situacao": situacao(row) if saved else "Em andamento",
        "email_status": email_status if saved else "—",
        "excel_synced": bool(row["excel_synced"]),
        "resume_count": row["resume_count"],
        "current_question": row["current_question"],
    }


def feedback_of(store: Store, row: dict) -> dict | None:
    if row["phase"] != "feedback":
        return None
    answer = store.get_answer(row["attempt_id"], row["current_question"])
    if answer is None:
        return None
    response = json.loads(answer["response_json"])
    correct = bool(answer["correct"])
    number = row["current_question"]
    earned = question_points_cents(number) if correct else 0
    payload = {
        "correct": correct,
        "points": round(earned / 100, 2),
        "points_formatada": format_score(earned),
        "explanation": explanation_for(number, correct),
        "response": public_response(response),
    }
    question = QUESTIONS[number]
    if question["type"] == "true_false":
        chosen = response.get("answers", {})
        payload["detail"] = [
            {"id": item_id, "is_right": chosen.get(item_id) is expected}
            for item_id, expected in question["key"].items()
        ]
    return payload


def state_of(store: Store, row: dict, email_configured: bool) -> dict:
    payload = {
        "status": row["status"],
        "finished": row["status"] == "concluida",
        "student": student_card(row),
        "progress": progress_of(row),
    }
    if row["status"] == "concluida":
        payload["result"] = result_of(store, row, email_configured)
        return payload
    payload["question"] = public_question(row["current_question"])
    payload["feedback"] = feedback_of(store, row)
    return payload


def _write_workbooks(app: Flask) -> None:
    store: Store = app.extensions["store"]
    with app.extensions["excel_lock"]:
        try:
            sync_all(store, app.config["DATA_DIR"])
        except Exception:
            app.logger.exception("Falha ao atualizar as planilhas.")


def run_sync(app: Flask) -> None:
    store: Store = app.extensions["store"]
    mailer: Mailer = app.extensions["mailer"]
    _write_workbooks(app)
    if not mailer.configured:
        return
    delivered = False
    for pending in store.pending_emails():
        if not store.claim_email(pending["attempt_id"]):
            continue
        fresh = store.get_attempt(pending["attempt_id"])
        try:
            mailer.send_result(fresh)
        except Exception:
            store.release_email_claim(fresh["attempt_id"], "Falha temporária no envio do e-mail.")
        else:
            store.mark_email_sent(fresh["attempt_id"])
            delivered = True
    if delivered:
        _write_workbooks(app)


def create_app(
    data_dir: Path | None = None,
    admin_password: str | None = None,
    mail_settings: dict | None = None,
    testing: bool = False,
    cors_origin: str | None = None,
    secret_key: str | None = None,
    mailer: Mailer | None = None,
) -> Flask:
    folder = Path(data_dir) if data_dir else Path(os.environ.get("DATA_DIR", ROOT / "data"))
    folder.mkdir(parents=True, exist_ok=True)
    app = Flask(__name__)
    app.config["TESTING"] = testing
    app.config["PROPAGATE_EXCEPTIONS"] = testing
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
    app.config["DATA_DIR"] = folder
    app.config["ADMIN_USER"] = "diogo"
    configured_password = admin_password if admin_password is not None else os.environ.get("ADMIN_PASSWORD", "")
    app.config["ADMIN_PASSWORD"] = configured_password or "diogo123"
    app.config["CORS_ORIGIN"] = (
        cors_origin if cors_origin is not None else os.environ.get("CORS_ORIGIN", "")
    )
    app.config["JSON_AS_ASCII"] = False
    app.json.ensure_ascii = False
    app.secret_key = secret_key or load_secret(folder)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "").lower() == "true"
    app.permanent_session_lifetime = timedelta(hours=8)

    store = Store(folder / "avaliacao.sqlite3")
    if mailer is None:
        mailer = Mailer(mail_settings if mail_settings is not None else mail_from_env())
    app.extensions["store"] = store
    app.extensions["mailer"] = mailer
    app.extensions["excel_lock"] = threading.Lock()
    app.extensions["login_failures"] = {}
    store.release_stale_email_claims()
    try:
        with app.extensions["excel_lock"]:
            sync_all(store, folder)
    except Exception:
        app.logger.exception("Falha ao preparar as planilhas.")

    register_routes(app)
    return app


def register_routes(app: Flask) -> None:
    @app.after_request
    def secure_headers(response):
        origin = app.config.get("CORS_ORIGIN") or ""
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Attempt-Id, X-Browser-Session"
            )
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Vary"] = "Origin"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        )
        return response

    @app.before_request
    def preflight():
        if request.method == "OPTIONS":
            return ("", 204)
        return None

    @app.errorhandler(HTTPException)
    def http_error(error):
        description = error.description or "Não foi possível concluir a operação."
        if not isinstance(description, str):
            description = "Não foi possível concluir a operação."
        return json_error(description, error.code)

    @app.get("/api/health")
    def health():
        mailer: Mailer = app.extensions["mailer"]
        return jsonify(
            {
                "ok": True,
                "email_configured": mailer.configured,
                "admin_configured": bool(app.config["ADMIN_PASSWORD"]),
                "turmas": list(TURMAS),
            }
        )

    @app.post("/api/start")
    def start():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return json_error("Dados inválidos.", 400)
        try:
            nome = normalize_name(data.get("nome", ""))
        except ValueError as exc:
            return json_error(str(exc), 400)
        turma = data.get("turma")
        if turma not in TURMAS:
            return json_error("Selecione uma turma válida.", 400)
        browser = parse_uuid(data.get("browser_session", ""))
        token = data.get("token", "")
        if browser is None or not isinstance(token, str) or TOKEN_RE.fullmatch(token) is None:
            return json_error("Não foi possível abrir a sessão da avaliação.", 400)
        store: Store = app.extensions["store"]
        created = store.create_attempt(browser, nome, turma, token)
        row = created["row"]
        if not created["authorized"]:
            return json_error(
                "Esta sessão do navegador já possui uma avaliação. Continue na aba em que ela foi iniciada.",
                409,
            )
        return jsonify(
            {
                "attempt_id": row["attempt_id"],
                "resumed": not created["created"],
                "finished": row["status"] == "concluida",
                "nome": row["nome"],
                "turma": row["turma"],
                "started_at": format_br(row["started_at"]),
            }
        )

    @app.get("/api/state")
    def state():
        row, error = authenticated_attempt(app)
        if error is not None:
            return error
        store: Store = app.extensions["store"]
        if request.args.get("count_resume") == "1" and row["status"] == "em_andamento":
            store.note_resume(row["attempt_id"])
            row = store.get_attempt(row["attempt_id"])
        mailer: Mailer = app.extensions["mailer"]
        return jsonify(state_of(store, row, mailer.configured))

    @app.post("/api/answer")
    def answer():
        row, error = authenticated_attempt(app)
        if error is not None:
            return error
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return json_error("Dados inválidos.", 400)
        number = data.get("question")
        response = data.get("response")
        if isinstance(number, bool) or not isinstance(number, int) or not isinstance(response, dict):
            return json_error("Resposta inválida.", 400)
        if number != row["current_question"] or row["status"] != "em_andamento":
            return json_error("Esta questão não está aberta para resposta.", 409)
        try:
            graded = grade(number, response)
        except ValueError as exc:
            return json_error(str(exc), 400)
        encoded = json.dumps(public_response(response), ensure_ascii=False)
        if len(encoded) > 4000:
            return json_error("A resposta está longa demais.", 400)
        store: Store = app.extensions["store"]
        saved = store.save_answer(row["attempt_id"], number, encoded, graded["correct"])
        if saved["conflict"]:
            return json_error(saved["reason"], 409)
        body = {
            "correct": graded["correct"],
            "points": graded["points"],
            "points_formatada": graded["points_formatada"],
            "explanation": graded["explanation"],
            "locked": True,
            "progress": progress_of(saved["row"]),
        }
        if "detail" in graded:
            body["detail"] = graded["detail"]
        return jsonify(body)

    @app.post("/api/next")
    def next_question():
        row, error = authenticated_attempt(app)
        if error is not None:
            return error
        store: Store = app.extensions["store"]
        moved = store.advance(row["attempt_id"])
        if moved["conflict"]:
            return json_error(moved["reason"], 409)
        updated = moved["row"]
        if moved["ready_to_finish"]:
            return jsonify({"ready_to_finish": True, "progress": progress_of(updated)})
        return jsonify(
            {
                "ready_to_finish": False,
                "progress": progress_of(updated),
                "question": public_question(updated["current_question"]),
                "feedback": None,
            }
        )

    @app.post("/api/finish")
    def finish():
        row, error = authenticated_attempt(app)
        if error is not None:
            return error
        store: Store = app.extensions["store"]
        data = request.get_json(silent=True)
        security = isinstance(data, dict) and data.get("encerramento") == "seguranca"
        try:
            outcome = store.finish(row["attempt_id"], security=security)
        except Exception:
            app.logger.exception("Falha ao salvar a avaliação.")
            return json_error(
                "O armazenamento está indisponível no momento. Tente salvar novamente.",
                503,
            )
        if outcome["conflict"]:
            return json_error(outcome["reason"], 409)
        run_sync(app)
        fresh = store.get_attempt(row["attempt_id"])
        mailer: Mailer = app.extensions["mailer"]
        return jsonify({"salvo": True, "result": result_of(store, fresh, mailer.configured)})

    @app.post("/api/admin/login")
    def admin_login():
        data = request.get_json(silent=True)
        username = data.get("username") if isinstance(data, dict) else ""
        password = data.get("password") if isinstance(data, dict) else ""
        if not isinstance(username, str):
            username = ""
        if not isinstance(password, str):
            password = ""
        address = request.remote_addr or "local"
        failures: dict = app.extensions["login_failures"]
        recent = [item for item in failures.get(address, []) if time.time() - item < 600]
        if len(recent) >= 8:
            failures[address] = recent
            return json_error("Muitas tentativas. Aguarde alguns minutos.", 429)
        user_ok = passwords_match(username.strip(), app.config["ADMIN_USER"])
        password_ok = passwords_match(password, app.config["ADMIN_PASSWORD"])
        if not user_ok or not password_ok:
            recent.append(time.time())
            failures[address] = recent
            return json_error("Usuário ou senha incorretos.", 401)
        failures[address] = []
        session.clear()
        session["admin"] = True
        session.permanent = True
        return jsonify({"ok": True})

    @app.post("/api/admin/logout")
    def admin_logout():
        session.clear()
        return jsonify({"ok": True})

    @app.get("/api/admin/results")
    def admin_results():
        denied = require_admin(app)
        if denied is not None:
            return denied
        turma = request.args.get("turma", "").strip()
        if turma and turma not in TURMAS:
            return json_error("Turma inválida.", 400)
        store: Store = app.extensions["store"]
        mailer: Mailer = app.extensions["mailer"]
        rows = store.list_all()
        if turma:
            rows = [row for row in rows if row["turma"] == turma]
        return jsonify(
            {
                "email_configured": mailer.configured,
                "results": [admin_view(row, mailer.configured) for row in rows],
            }
        )

    @app.post("/api/admin/sync")
    def admin_sync():
        denied = require_admin(app)
        if denied is not None:
            return denied
        run_sync(app)
        return jsonify({"ok": True})

    @app.get("/api/admin/export/<turma>")
    def admin_export(turma: str):
        denied = require_admin(app)
        if denied is not None:
            return denied
        if turma not in TURMAS:
            return json_error("Turma inválida.", 404)
        store: Store = app.extensions["store"]
        with app.extensions["excel_lock"]:
            path = sync_class(store, app.config["DATA_DIR"], turma)
        return send_file(
            path,
            as_attachment=True,
            download_name=f"notas_{turma}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    @app.get("/")
    def home():
        return send_from_directory(ROOT, "index.html")

    @app.get("/admin")
    def admin_page():
        return send_from_directory(ROOT, "admin.html")

    @app.get("/css/<path:filename>")
    def styles(filename: str):
        return send_from_directory(ROOT / "css", filename)

    @app.get("/js/<path:filename>")
    def scripts(filename: str):
        return send_from_directory(ROOT / "js", filename)

    @app.get("/assets/<path:filename>")
    def assets(filename: str):
        return send_from_directory(ROOT / "assets", filename)


def authenticated_attempt(app: Flask):
    attempt_id = parse_uuid(request.headers.get("X-Attempt-Id", ""))
    authorization = request.headers.get("Authorization", "")
    token = authorization[7:].strip() if authorization.startswith("Bearer ") else ""
    if attempt_id is None or TOKEN_RE.fullmatch(token) is None:
        return None, json_error("Não foi possível reconhecer esta tentativa.", 401)
    store: Store = app.extensions["store"]
    row = store.authenticate(attempt_id, token)
    if row is None:
        return None, json_error("Não foi possível reconhecer esta tentativa.", 401)
    return row, None


def require_admin(app: Flask):
    if session.get("admin") is True:
        return None
    return json_error("Acesso não autorizado.", 401)


def local_ip() -> str:
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("8.8.8.8", 80))
        address = probe.getsockname()[0]
        probe.close()
        return address
    except OSError:
        return "127.0.0.1"


def main() -> None:
    load_env_file(BACKEND / ".env")
    load_env_file(ROOT / ".env")
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    application = create_app()
    mailer: Mailer = application.extensions["mailer"]
    print("Avaliação de Python — 8º ano — JBS FoodTech")
    print(f"Prova neste computador: http://127.0.0.1:{port}")
    print(f"Prova na rede da escola: http://{local_ip()}:{port}")
    print(f"Área do professor:       http://127.0.0.1:{port}/admin")
    print("Login da área do professor: diogo")
    if mailer.configured:
        print(f"E-mail de resultados:    {mailer.recipient}")
    else:
        print("E-mail não configurado: as notas serão salvas e as planilhas atualizadas mesmo assim.")
    application.run(host=host, port=port, threaded=True, debug=False)


if __name__ == "__main__":
    main()
