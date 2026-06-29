from __future__ import annotations

import asyncio
import threading

from fastapi.testclient import TestClient

from gateway import feishu


def _cfg(*, encrypt_key: str = "") -> dict[str, str]:
    return {
        "app_id": "app",
        "app_secret": "secret",
        "verify_token": "expected-token",
        "encrypt_key": encrypt_key,
        "domain": "open.feishu.cn",
    }


def _message(message_id: str, *, token: str | None = "expected-token") -> dict:
    header = {"event_type": "im.message.receive_v1"}
    if token is not None:
        header["token"] = token
    return {
        "header": header,
        "event": {
            "sender": {"sender_id": {"open_id": "user-1"}},
            "message": {
                "message_id": message_id,
                "chat_id": "chat-1",
                "chat_type": "p2p",
                "content": '{"text":"hello"}',
            },
        },
    }


def test_webhook_rejects_event_without_verify_token() -> None:
    with TestClient(feishu.build_app(_cfg())) as client:
        response = client.post("/feishu/webhook", json=_message("m1", token=None))

    assert response.status_code == 403


def test_webhook_requires_encrypted_envelope_when_encrypt_key_configured() -> None:
    with TestClient(feishu.build_app(_cfg(encrypt_key="configured"))) as client:
        response = client.post("/feishu/webhook", json=_message("m1"))

    assert response.status_code == 403


def test_webhook_processes_duplicate_message_only_once(monkeypatch) -> None:
    calls: list[str] = []

    async def fake_handle(app, cfg, event, bot_open_id) -> None:
        calls.append(event["message"]["message_id"])

    monkeypatch.setattr(feishu, "_handle_message", fake_handle)
    feishu._seen_msg_ids.clear()

    with TestClient(feishu.build_app(_cfg())) as client:
        first = client.post("/feishu/webhook", json=_message("m1"))
        second = client.post("/feishu/webhook", json=_message("m1"))
        asyncio.run(asyncio.sleep(0))

    assert first.status_code == 200
    assert second.status_code == 200
    assert calls == ["m1"]


def test_token_cache_is_isolated_per_feishu_application() -> None:
    class FakeResponse:
        def __init__(self, token: str) -> None:
            self._token = token

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "code": 0,
                "tenant_access_token": self._token,
                "expire": 7200,
            }

    class FakeClient:
        def __init__(self) -> None:
            self.calls: list[str] = []

        async def post(self, url: str, *, json: dict, timeout: float):
            app_id = json["app_id"]
            self.calls.append(app_id)
            return FakeResponse(f"token-{app_id}")

    async def exercise() -> tuple[str, str, list[str]]:
        cache = feishu._TokenCache()
        client = FakeClient()
        first = await cache.get(
            client,
            {
                "domain": "open.feishu.cn",
                "app_id": "app-a",
                "app_secret": "secret-a",
            },
        )
        second = await cache.get(
            client,
            {
                "domain": "open.feishu.cn",
                "app_id": "app-b",
                "app_secret": "secret-b",
            },
        )
        return first, second, client.calls

    first, second, calls = asyncio.run(exercise())

    assert first == "token-app-a"
    assert second == "token-app-b"
    assert calls == ["app-a", "app-b"]


def test_token_cache_supports_multiple_event_loops_concurrently() -> None:
    class FakeResponse:
        def __init__(self, token: str) -> None:
            self._token = token

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "code": 0,
                "tenant_access_token": self._token,
                "expire": 7200,
            }

    class FakeClient:
        async def post(self, url: str, *, json: dict, timeout: float):
            await asyncio.sleep(0.05)
            return FakeResponse(f"token-{json['app_id']}")

    cache = feishu._TokenCache()
    barrier = threading.Barrier(2)
    results: list[str] = []
    errors: list[BaseException] = []

    def worker(app_id: str) -> None:
        async def exercise() -> str:
            barrier.wait()
            return await cache.get(
                FakeClient(),
                {
                    "domain": "open.feishu.cn",
                    "app_id": app_id,
                    "app_secret": f"secret-{app_id}",
                },
            )

        try:
            results.append(asyncio.run(exercise()))
        except BaseException as exc:
            errors.append(exc)

    threads = [
        threading.Thread(target=worker, args=(app_id,), daemon=True)
        for app_id in ("app-a", "app-b")
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=1.0)

    assert not any(thread.is_alive() for thread in threads)
    assert errors == []
    assert sorted(results) == ["token-app-a", "token-app-b"]
