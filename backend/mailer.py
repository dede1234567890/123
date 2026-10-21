"""Envio de e-mail ao professor. As credenciais vêm somente do ambiente."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from questions_bank import MAX_SCORE_CENTS, format_score
from storage import format_br

TEACHER_EMAIL = "diogo.nascimento@institutojef.org.br"


class MailError(Exception):
    pass


class MailNotConfigured(MailError):
    pass


class Mailer:
    def __init__(self, settings: dict | None = None, sender=None):
        settings = settings or {}
        self.host = (settings.get("host") or "").strip()
        self.port = int(settings.get("port") or 587)
        self.user = (settings.get("user") or "").strip()
        self.password = settings.get("password") or ""
        self.sender_address = (settings.get("sender") or self.user or "").strip()
        self.recipient = (settings.get("recipient") or TEACHER_EMAIL).strip()
        self.use_tls = str(settings.get("tls", "true")).lower() not in {"0", "false", "nao", "não"}
        self._sender = sender or smtp_send

    @property
    def configured(self) -> bool:
        return bool(self.host and self.sender_address and self.recipient and self.password)

    def send_result(self, row: dict) -> None:
        if not self.configured:
            raise MailNotConfigured("Servidor de e-mail não configurado.")
        acertos = int(row["acertos"])
        cents = int(row.get("nota_cents") or 0)
        message = EmailMessage()
        message["Subject"] = f"Resultado da avaliação de Python — {row['nome']} ({row['turma']})"
        message["From"] = self.sender_address
        message["To"] = self.recipient
        message.set_content(
            "\n".join(
                [
                    "Uma avaliação de Python do 8º ano foi concluída.",
                    "",
                    f"Aluno: {row['nome']}",
                    f"Turma: {row['turma']}",
                    f"Nota: {format_score(cents)}",
                    f"Acertos: {acertos}",
                    f"Aproveitamento: {int(cents * 100 / MAX_SCORE_CENTS)}%",
                    f"Erros: {int(row['erros'])}",
                    f"Início: {format_br(row['started_at'])}",
                    f"Conclusão: {format_br(row['finished_at'])}",
                    f"Identificador: {row['attempt_id']}",
                    (
                        "Encerramento: Prova encerrada por tentativa de burlar a segurança."
                        if row.get("encerramento") == "seguranca"
                        else "Encerramento: Concluída pelo aluno."
                    ),
                    "",
                    "O registro foi realizado com sucesso no armazenamento central.",
                ]
            )
        )
        try:
            self._sender(
                self.host,
                self.port,
                self.user,
                self.password,
                self.use_tls,
                message,
            )
        except MailNotConfigured:
            raise
        except Exception as exc:
            raise MailError("Não foi possível enviar o e-mail.") from exc


def smtp_send(host: str, port: int, user: str, password: str, use_tls: bool, message: EmailMessage) -> None:
    with smtplib.SMTP(host, port, timeout=20) as client:
        client.ehlo()
        if use_tls:
            client.starttls()
            client.ehlo()
        if user:
            client.login(user, password)
        client.send_message(message)


def student_message(saved: bool, excel_ok: bool, email_ok: bool, email_configured: bool) -> str:
    if not saved:
        return "A avaliação ainda não foi salva. Tente registrar novamente."
    if excel_ok and email_ok:
        return (
            "Avaliação registrada com sucesso. "
            "A planilha da turma foi atualizada e o professor foi avisado."
        )
    if excel_ok and not email_configured:
        return (
            "Avaliação registrada com sucesso. "
            "A planilha da turma foi atualizada. "
            "O aviso por e-mail será enviado quando o servidor de e-mail estiver configurado."
        )
    if excel_ok:
        return (
            "Avaliação registrada com sucesso. "
            "A planilha da turma foi atualizada. "
            "O aviso por e-mail será reenviado automaticamente."
        )
    return (
        "Avaliação registrada com sucesso. "
        "A atualização da planilha será concluída automaticamente em instantes."
    )


def incentive(cents: int) -> str:
    if cents >= 630:
        return "Excelente trabalho! Você demonstrou segurança nos conteúdos desta avaliação."
    if cents >= 490:
        return "Muito bem! Você concluiu a avaliação com um bom desempenho."
    if cents >= 350:
        return "Avaliação concluída. Continue praticando para fortalecer o que você já aprendeu."
    return (
        "Avaliação concluída. Revise os conteúdos com calma e pratique mais um pouco. "
        "Você é capaz de avançar."
    )
