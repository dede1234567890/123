import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from mailer import Mailer


@pytest.fixture
def sent_messages():
    return []


@pytest.fixture
def app(tmp_path, sent_messages):
    def fake_sender(_host, _port, _user, _password, _use_tls, message):
        sent_messages.append(message)

    mailer = Mailer(
        {
            "host": "smtp.exemplo",
            "port": 587,
            "user": "professor",
            "password": "segredo-smtp",
            "sender": "professor@escola.com",
            "recipient": "diogo.nascimento@institutojef.org.br",
            "tls": "true",
        },
        sender=fake_sender,
    )
    return create_app(
        data_dir=tmp_path,
        admin_password="segredo-teste",
        testing=True,
        secret_key="chave-de-teste",
        mailer=mailer,
    )


@pytest.fixture
def client(app):
    return app.test_client()
