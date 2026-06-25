from Application.cors_origins import cors_origins


def test_cors_origins_splits_front_url(monkeypatch) -> None:
    monkeypatch.setenv(
        "FRONT_URL",
        "http://localhost:3000,https://app.example.com",
    )
    monkeypatch.delenv("VERCEL_URL", raising=False)
    monkeypatch.delenv("VERCEL_BRANCH_URL", raising=False)
    assert cors_origins() == [
        "http://localhost:3000",
        "https://app.example.com",
    ]


def test_cors_origins_adds_vercel_url(monkeypatch) -> None:
    monkeypatch.setenv("FRONT_URL", "https://front.vercel.app")
    monkeypatch.setenv("VERCEL_URL", "bytte-api.vercel.app")
    assert "https://front.vercel.app" in cors_origins()
    assert "https://bytte-api.vercel.app" in cors_origins()


def test_cors_origins_front_url_takes_precedence_over_wildcard_only_in_cors_origins(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "*")
    monkeypatch.setenv("FRONT_URL", "https://app.example.com")
    monkeypatch.delenv("VERCEL_URL", raising=False)
    monkeypatch.delenv("VERCEL_BRANCH_URL", raising=False)
    assert cors_origins() == ["*"]
