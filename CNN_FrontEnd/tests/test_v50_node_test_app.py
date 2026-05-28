import json
import unittest

from v50_node_test_app import MockV50Node


class MockV50NodeTest(unittest.TestCase):
    def setUp(self):
        self.node = MockV50Node()

    def test_ping_returns_v50_health_text_with_cors(self):
        response = self.node.handle("GET", "/ping")

        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "text/plain; charset=utf-8")
        self.assertEqual(response.body.decode("utf-8"), "V50 연산 노드 살아있음 ㅇㅇ")
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")

    def test_config_updates_threshold_from_json(self):
        response = self.node.handle(
            "POST",
            "/api/config",
            body=json.dumps({"threshold": 0.7}).encode("utf-8"),
            headers={"content-type": "application/json"},
        )

        payload = json.loads(response.body.decode("utf-8"))
        self.assertEqual(response.status, 200)
        self.assertEqual(payload, {"status": "success", "msg": "설정 변경 완료"})
        self.assertEqual(self.node.threshold, 0.7)

    def test_detect_accepts_binary_image_and_returns_anomaly_payload(self):
        response = self.node.handle(
            "POST",
            "/api/detect",
            body=b"\xff\xd8fake-jpeg-bytes\xff\xd9",
            headers={"content-type": "image/jpeg"},
        )

        payload = json.loads(response.body.decode("utf-8"))
        self.assertEqual(response.status, 200)
        self.assertEqual(payload["anomaly"], True)
        self.assertEqual(payload["class"], "person")
        self.assertEqual(payload["clip"], "anomaly_clip_sample.jpg")
        self.assertEqual(len(self.node.timeline), 2)

    def test_timeline_returns_latest_detection_first(self):
        self.node.handle("POST", "/api/detect", body=b"image-one")
        self.node.handle("POST", "/api/detect", body=b"image-two")

        response = self.node.handle("GET", "/api/timeline")

        payload = json.loads(response.body.decode("utf-8"))
        self.assertEqual(response.status, 200)
        self.assertEqual(len(payload), 3)
        self.assertEqual(payload[0]["clip_url"], "/api/clip/anomaly_clip_sample.jpg")
        self.assertGreaterEqual(payload[0]["confidence"], 0.8)

    def test_clip_endpoint_returns_jpeg_bytes(self):
        response = self.node.handle("GET", "/api/clip/anomaly_clip_sample.jpg")

        self.assertEqual(response.status, 200)
        self.assertEqual(response.content_type, "image/jpeg")
        self.assertTrue(response.body.startswith(b"\xff\xd8"))

    def test_model_swap_returns_text(self):
        response = self.node.handle("POST", "/api/model/swap")

        self.assertEqual(response.status, 200)
        self.assertEqual(response.body.decode("utf-8"), "모델 교체 완료")

    def test_preflight_options_returns_cors_headers(self):
        response = self.node.handle("OPTIONS", "/api/detect")

        self.assertEqual(response.status, 204)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
        self.assertIn("POST", response.headers["Access-Control-Allow-Methods"])


if __name__ == "__main__":
    unittest.main()
