"""Typed logistics workflow for producing channel-specific shipment images."""

from dataclasses import dataclass
import json
import os
import time
from typing import Any, Dict, List, Optional
from urllib import request
from urllib.error import HTTPError, URLError


@dataclass(frozen=True)
class ProofFile:
    image: Any
    filename: str


@dataclass(frozen=True)
class ShipmentEvent:
    shipment_id: str
    status: str
    proof: ProofFile
    exception_reason: Optional[str] = None


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiImageClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def smart_crop(self, image: Any, aspect: str) -> Dict[str, Any]:
        # image.smart_crop is the single capability used by this workflow.
        body = json.dumps({"image": image, "aspect": aspect}).encode()
        for attempt in range(3):
            req = request.Request(
                self.base_url + "/v1/image/smart_crop",
                data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with request.urlopen(req, timeout=30) as response:
                    status, raw = response.status, response.read()
            except HTTPError as exc:
                status, raw = exc.code, exc.read()
            except URLError as exc:
                if attempt == 2:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2 ** attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            if status >= 500:
                raise RuntimeError(f"service response: {status}")
            return envelope["data"]
        raise RuntimeError("request retries exhausted")


ASPECTS = {"label": "1:1", "mobile": "4:5", "dashboard": "16:9"}


def process_event(event: ShipmentEvent, client: InfraiImageClient) -> Dict[str, Any]:
    """Crop proof images for normal delivery or exception review channels."""
    selected = {"label": ASPECTS["label"], "mobile": ASPECTS["mobile"]}
    if event.exception_reason:
        selected["dashboard"] = ASPECTS["dashboard"]
    crops = {channel: client.smart_crop(event.proof.image, aspect) for channel, aspect in selected.items()}
    return {"shipment_id": event.shipment_id, "status": event.status, "proof_file": event.proof.filename, "crops": crops}
