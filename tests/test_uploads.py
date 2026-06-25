from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from Application.services.upload_service import UploadService


def test_uploads_invalid_document_type_400(client: TestClient) -> None:
    r = client.post(
        "/api/v1/uploads/presigned",
        json={
            "document_type": "invalid",
            "filename": "logo.png",
            "mime_type": "image/png",
        },
        headers={"X-Restaurant-Id": "1"},
    )
    assert r.status_code == 400


def test_uploads_confirm_invalid_key_400(client: TestClient) -> None:
    with patch("Application.services.upload_service.require_storage_settings") as mock_cfg:
        mock_cfg.return_value = MagicMock(
            configured=True,
            public_url_base="https://example.supabase.co/storage/v1/object/public/restaurant-documents",
        )
        r = client.post(
            "/api/v1/uploads/confirm",
            json={
                "document_type": "logo",
                "storage_key": "999/logo/x.png",
            },
            headers={"X-Restaurant-Id": "1"},
        )
    assert r.status_code == 400


def test_presigned_returns_url_with_mock_httpx() -> None:
    svc = UploadService()
    mock_settings = MagicMock(
        configured=True,
        supabase_url="https://xxx.supabase.co",
        service_role_key="key",
        bucket="restaurant-documents",
        public_url_base="https://xxx.supabase.co/storage/v1/object/public/restaurant-documents",
    )
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "signedUrl": "https://xxx.supabase.co/storage/v1/object/upload/sign/restaurant-documents/1/logo/x",
        "token": "tok123",
        "path": "1/logo/x",
    }
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)

    with patch(
        "Application.services.upload_service.require_storage_settings",
        return_value=mock_settings,
    ), patch("Application.services.upload_service.httpx.Client", return_value=mock_client):
        result = svc.create_presigned_upload(1, "logo", "logo.png", "image/png")
    assert result.storage_key.startswith("1/logo/")
    assert "token=tok123" in result.upload_url
    assert result.token == "tok123"


def test_confirm_logo_persists_with_mock_infra() -> None:
    svc = UploadService()
    mock_settings = MagicMock(
        configured=True,
        public_url_base="https://xxx.supabase.co/storage/v1/object/public/restaurant-documents",
    )
    with patch(
        "Application.services.upload_service.require_storage_settings",
        return_value=mock_settings,
    ), patch.object(svc, "_verify_object_exists"), patch.object(
        svc._infra, "confirm_logo_upload"
    ) as mock_confirm:
        from Application.services.upload_service import ConfirmUploadRequest

        out = svc.confirm_upload(
            1,
            ConfirmUploadRequest(
                document_type="logo",
                storage_key="1/logo/abc_logo.png",
                filename="logo.png",
                mime_type="image/png",
            ),
        )
    mock_confirm.assert_called_once()
    assert out.public_url.endswith("1/logo/abc_logo.png")
    assert out.document_type == "logo"
