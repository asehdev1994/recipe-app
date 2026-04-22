from types import SimpleNamespace

from recipe_app.services import storage


class FakeCookies(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saved = False

    def save(self):
        self.saved = True


class FakeSessionState(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


def test_ensure_valid_token_updates_session_and_rotated_cookie(monkeypatch):
    cookies = FakeCookies(refresh_token="old-refresh-token")
    monkeypatch.setattr(
        storage.st,
        "session_state",
        FakeSessionState(cookies=cookies, id_token=None),
    )
    monkeypatch.setattr(
        storage,
        "refresh_id_token",
        lambda refresh_token: {
            "id_token": "new-id-token",
            "refresh_token": "new-refresh-token",
            "user_id": "user-123",
        },
    )

    storage.ensure_valid_token()

    assert storage.st.session_state["id_token"] == "new-id-token"
    assert cookies["refresh_token"] == "new-refresh-token"
    assert cookies.saved is True


def test_load_data_returns_defaults_when_document_missing(monkeypatch):
    fake_doc = SimpleNamespace(exists=False)
    fake_ref = SimpleNamespace(get=lambda: fake_doc)
    monkeypatch.setattr(
        storage,
        "_get_user_ref",
        lambda: SimpleNamespace(
            collection=lambda name: SimpleNamespace(document=lambda doc_id: fake_ref)
        ),
    )

    assert storage.load_data() == {
        "units": ["g", "kg", "ml", "l", "tsp", "tbsp", "cup", "pcs"],
        "recipes": {},
    }


def test_save_data_persists_recipe_document(monkeypatch):
    saved = {}

    fake_doc_ref = SimpleNamespace(set=lambda data: saved.setdefault("data", data))
    monkeypatch.setattr(
        storage,
        "_get_user_ref",
        lambda: SimpleNamespace(
            collection=lambda name: SimpleNamespace(document=lambda doc_id: fake_doc_ref)
        ),
    )

    payload = {"units": ["pcs"], "recipes": {"Soup": {}}}
    storage.save_data(payload)

    assert saved["data"] == payload


def test_get_project_id_prefers_environment_for_emulator(monkeypatch):
    monkeypatch.setenv("FIREBASE_PROJECT_ID", "demo-recipe-app")

    assert storage._get_project_id() == "demo-recipe-app"
