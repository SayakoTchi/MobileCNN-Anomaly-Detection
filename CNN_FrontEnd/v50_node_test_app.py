from __future__ import annotations

import argparse
import base64
import json
from dataclasses import dataclass, field
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Mapping
from urllib.parse import urlparse


SAMPLE_JPEG = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////"
    "2wBDAf//////////////////////////////////////////////////////////////////////////////////////"
    "wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA"
    "/9oADAMBAAIQAxAAAAH/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAEFAqf/xAAUEQEAAAAAAAAAAAAA"
    "AAAAAAAA/9oACAEDAQE/ASP/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAECAQE/ASP/xAAUEAEAAAAAAAAA"
    "AAAAAAAAAAAA/9oACAEBAAY/Al//xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAE/IV//2gAMAwEAAgAD"
    "AAAAEP/EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQMBAT8QH//EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAI"
    "AQIBAT8QH//EABQQAQAAAAAAAAAAAAAAAAAAABD/2gAIAQEAAT8QH//Z"
)


@dataclass
class MockResponse:
    status: int
    body: bytes = b""
    content_type: str = "application/json; charset=utf-8"
    headers: dict[str, str] = field(default_factory=dict)


class MockV50Node:
    def __init__(self) -> None:
        self.threshold = 0.7
        self.timeline: list[dict[str, object]] = [
            {
                "time": "2026-05-19 14:30:00",
                "object": "person",
                "confidence": 0.85,
                "clip_url": "/api/clip/anomaly_clip_sample.jpg",
            }
        ]

    def handle(
        self,
        method: str,
        path: str,
        body: bytes = b"",
        headers: Mapping[str, str] | None = None,
    ) -> MockResponse:
        method = method.upper()
        clean_path = urlparse(path).path
        headers = {key.lower(): value for key, value in (headers or {}).items()}

        if method == "OPTIONS":
            return self._response(204, b"", "text/plain; charset=utf-8")

        if method == "GET" and clean_path == "/ping":
            return self._text("V50 연산 노드 살아있음 ㅇㅇ")

        if method == "POST" and clean_path == "/api/config":
            return self._update_config(body, headers)

        if method == "POST" and clean_path == "/api/detect":
            return self._detect(body)

        if method == "GET" and clean_path == "/api/timeline":
            return self._json(self.timeline)

        if method == "GET" and clean_path.startswith("/api/clip/"):
            return self._clip(clean_path.rsplit("/", 1)[-1])

        if method == "POST" and clean_path == "/api/model/swap":
            return self._text("모델 교체 완료")

        return self._json({"error": f"Route not found: {method} {clean_path}"}, status=404)

    def _update_config(self, body: bytes, headers: Mapping[str, str]) -> MockResponse:
        if "application/json" not in headers.get("content-type", ""):
            return self._json({"status": "error", "msg": "Content-Type must be application/json"}, status=415)

        try:
            payload = json.loads(body.decode("utf-8") or "{}")
            threshold = float(payload["threshold"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            return self._json({"status": "error", "msg": "threshold must be a number"}, status=400)

        if threshold < 0 or threshold > 1:
            return self._json({"status": "error", "msg": "threshold must be between 0 and 1"}, status=400)

        self.threshold = threshold
        return self._json({"status": "success", "msg": "설정 변경 완료"})

    def _detect(self, body: bytes) -> MockResponse:
        if not body:
            return self._json({"error": "image binary body is required"}, status=400)

        confidence = max(0.8, min(0.99, 0.8 + (len(body) % 20) / 100))
        event = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "object": "person",
            "confidence": round(confidence, 2),
            "clip_url": "/api/clip/anomaly_clip_sample.jpg",
        }
        self.timeline.insert(0, event)

        return self._json(
            {
                "anomaly": True,
                "class": "person",
                "clip": "anomaly_clip_sample.jpg",
            }
        )

    def _clip(self, file_name: str) -> MockResponse:
        if file_name != "anomaly_clip_sample.jpg":
            return self._json({"error": f"clip not found: {file_name}"}, status=404)
        return self._response(200, SAMPLE_JPEG, "image/jpeg")

    def _json(self, payload: object, status: int = 200) -> MockResponse:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return self._response(status, body, "application/json; charset=utf-8")

    def _text(self, text: str, status: int = 200) -> MockResponse:
        return self._response(status, text.encode("utf-8"), "text/plain; charset=utf-8")

    def _response(self, status: int, body: bytes, content_type: str) -> MockResponse:
        return MockResponse(
            status=status,
            body=body,
            content_type=content_type,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
                "Cache-Control": "no-store",
            },
        )


class V50NodeRequestHandler(BaseHTTPRequestHandler):
    node = MockV50Node()

    def do_OPTIONS(self) -> None:
        self._send(self.node.handle("OPTIONS", self.path))

    def do_GET(self) -> None:
        self._send(self.node.handle("GET", self.path, headers=self.headers))

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        self._send(self.node.handle("POST", self.path, body=body, headers=self.headers))

    def log_message(self, format: str, *args: object) -> None:
        print(f"[v50_node_test_app] {self.address_string()} - {format % args}")

    def _send(self, response: MockResponse) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(len(response.body)))
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()
        if response.body:
            self.wfile.write(response.body)


def run(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = ThreadingHTTPServer((host, port), V50NodeRequestHandler)
    print(f"v50_node_test_app running at http://{host}:{port}")
    print("Frontend Base URL: http://127.0.0.1:8080")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nv50_node_test_app stopped")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock V50 edge node API server for frontend testing.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    args = parser.parse_args()
    run(args.host, args.port)


if __name__ == "__main__":
    main()
