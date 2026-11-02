
import pytest
from app import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_homepage_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_existing_article_returns_200(client):
    response = client.get(
        "/posts/web-application-firewalls"
    )
    assert response.status_code == 200


def test_unknown_article_returns_404(client):
    response = client.get(
        "/posts/not-a-real-post"
    )
    assert response.status_code == 404


def test_homepage_has_expected_content(client):
    response = client.get("/")
    assert b"Azure Security Lab" in response.data


def test_server_does_not_expose_debugger(client):
    response = client.get("/")
    assert b"Werkzeug Debugger" not in response.data


def test_security_headers(client):
    response = client.get("/")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == (
        "strict-origin-when-cross-origin"
    )

    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp
