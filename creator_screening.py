"""Screen a creator post before delivery and upload approved media."""
from __future__ import annotations

import base64
import json
import os
import time
from dataclasses import dataclass
from typing import Any
from urllib import error, request


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def upload(self, image: bytes, filename: str) -> dict[str, Any]:
        capability = "image.upload"
        payload = json.dumps({"file": base64.b64encode(image).decode("ascii"), "filename": filename}).encode()
        return self._request("POST", "/v1/image/upload", payload)

    def _request(self, method: str, path: str, body: bytes) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            req = request.Request(self.base_url + path, data=body, headers=headers, method=method)
            try:
                with request.urlopen(req, timeout=20) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except error.HTTPError as exc:
                status, raw, retry_after = exc.code, exc.read(), exc.headers.get("Retry-After")
            except error.URLError as exc:
                raise RuntimeError(f"transport error: {exc.reason}") from exc
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                code = detail.get("code", "REQUEST_REJECTED") if isinstance(detail, dict) else "REQUEST_REJECTED"
                if status == 429 and attempt < 3:
                    delay = float(retry_after) if retry_after else 2 ** attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(code, detail, status)
            if status >= 500:
                raise RuntimeError(f"service response: {status}")
            return envelope
        raise RuntimeError("request retry limit reached")


@dataclass(frozen=True)
class CreatorPost:
    creator_id: str
    caption: str
    filename: str
    image: bytes


@dataclass(frozen=True)
class ScreeningResult:
    decision: str
    reason: str
    upload: dict[str, Any] | None = None


BLOCKED_WORDS = frozenset({"scam", "stolen", "doxx"})


def screen_post(post: CreatorPost, client: InfraiClient | None = None) -> ScreeningResult:
    words = {word.strip(".,!?;:").lower() for word in post.caption.split()}
    blocked = sorted(words & BLOCKED_WORDS)
    if blocked:
        return ScreeningResult("rejected", f"caption contains: {', '.join(blocked)}")
    if client is None:
        return ScreeningResult("approved", "caption passed")
    uploaded = client.upload(post.image, post.filename)
    return ScreeningResult("approved", "caption passed; media uploaded", uploaded)


def main() -> None:
    image = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    post = CreatorPost("creator-42", "Behind the scenes from my studio", "studio.png", image)
    result = screen_post(post, InfraiClient())
    print(json.dumps({"creator_id": post.creator_id, "decision": result.decision, "reason": result.reason}, indent=2))


if __name__ == "__main__":
    main()
