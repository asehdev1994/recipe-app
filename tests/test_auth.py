import os
from types import SimpleNamespace

from recipe_app.services import auth


def test_sign_in_posts_expected_payload(monkeypatch):
    monkeypatch.setattr(auth.st, "secrets", {"FIREBASE_API_KEY": "test-api-key"})

    captured = {}

    def fake_post(url, json=None, data=None):
        captured["url"] = url
        captured["json"] = json
        captured["data"] = data
        return SimpleNamespace(json=lambda: {"ok": True})

    monkeypatch.setattr(auth.requests, "post", fake_post)

    result = auth.sign_in("user@example.com", "secret")

    assert result == {"ok": True}
    assert captured["url"].endswith("accounts:signInWithPassword?key=test-api-key")
    assert captured["json"] == {
        "email": "user@example.com",
        "password": "secret",
        "returnSecureToken": True,
    }
    assert captured["data"] is None


def test_refresh_id_token_returns_normalized_tokens(monkeypatch):
    monkeypatch.setattr(auth.st, "secrets", {"FIREBASE_API_KEY": "test-api-key"})

    def fake_post(url, json=None, data=None):
        assert url.endswith("/token?key=test-api-key")
        assert data == {
            "grant_type": "refresh_token",
            "refresh_token": "refresh-token",
        }
        return SimpleNamespace(
            status_code=200,
            json=lambda: {
                "id_token": "id-token",
                "refresh_token": "rotated-token",
                "user_id": "user-123",
            },
        )

    monkeypatch.setattr(auth.requests, "post", fake_post)

    assert auth.refresh_id_token("refresh-token") == {
        "id_token": "id-token",
        "refresh_token": "rotated-token",
        "user_id": "user-123",
    }


def test_refresh_id_token_returns_none_for_failed_request(monkeypatch):
    monkeypatch.setattr(auth.st, "secrets", {"FIREBASE_API_KEY": "test-api-key"})

    monkeypatch.setattr(
        auth.requests,
        "post",
        lambda url, json=None, data=None: SimpleNamespace(status_code=400),
    )

    assert auth.refresh_id_token("refresh-token") is None


def test_sign_in_uses_auth_emulator_when_configured(monkeypatch):
    monkeypatch.setenv("FIREBASE_API_KEY", "demo-api-key")
    monkeypatch.setenv("FIREBASE_AUTH_EMULATOR_HOST", "firebase:9099")

    captured = {}

    def fake_post(url, json=None, data=None):
        captured["url"] = url
        return SimpleNamespace(json=lambda: {"ok": True})

    monkeypatch.setattr(auth.requests, "post", fake_post)

    auth.sign_in("user@example.com", "secret")

    assert captured["url"] == (
        "http://firebase:9099/identitytoolkit.googleapis.com/v1/"
        "accounts:signInWithPassword?key=demo-api-key"
    )

    monkeypatch.delenv("FIREBASE_AUTH_EMULATOR_HOST", raising=False)
    monkeypatch.delenv("FIREBASE_API_KEY", raising=False)
