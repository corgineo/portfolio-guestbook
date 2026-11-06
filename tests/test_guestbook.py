import importlib
import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient


class GuestbookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = os.environ.get("GUESTBOOK_DB")
        os.environ["GUESTBOOK_DB"] = str(Path(self.temp.name) / "test.db")
        import main
        self.main = importlib.reload(main)
        self.client = TestClient(self.main.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        if self.previous is None:
            os.environ.pop("GUESTBOOK_DB", None)
        else:
            os.environ["GUESTBOOK_DB"] = self.previous
        self.temp.cleanup()

    def test_health_and_latest_first(self):
        self.assertEqual(self.client.get("/").json(), {"status": "ok"})
        first = self.client.post("/guestbook", json={"name": " 첫째 ", "content": "첫 글"})
        second = self.client.post("/guestbook", json={"name": "둘째", "content": "새 글"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["name"], "첫째")
        self.assertEqual([x["id"] for x in self.client.get("/guestbook").json()],
                         [second.json()["id"], first.json()["id"]])

    def test_invalid_input_is_rejected(self):
        for payload in [{"name": " ", "content": "글"},
                        {"name": "이름", "content": "x" * 501},
                        {"name": "x" * 51, "content": "글"},
                        {"name": "이름", "content": ""}]:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/guestbook", json=payload).status_code, 422)
        self.assertEqual(self.client.get("/guestbook").json(), [])

    def test_sql_text_is_stored_as_data_and_persists(self):
        text = "'); DROP TABLE guestbook; --"
        response = self.client.post("/guestbook", json={"name": "검증", "content": text})
        self.assertEqual(response.status_code, 200)
        with TestClient(self.main.app) as reopened:
            self.assertEqual(reopened.get("/guestbook").json()[0]["content"], text)

    def test_name_length_boundary(self):
        for length in (9, 10):
            response = self.client.post(
                "/guestbook", json={"name": "가" * length, "content": "경계값 확인"}
            )
            self.assertEqual(response.status_code, 200)
        rejected = self.client.post(
            "/guestbook", json={"name": "가" * 11, "content": "저장되면 안 되는 글"}
        )
        self.assertEqual(rejected.status_code, 422)
        self.assertEqual(len(self.client.get("/guestbook").json()), 2)

    def test_trimming_and_content_boundary(self):
        accepted = self.client.post(
            "/guestbook", json={"name": "  " + "가" * 10 + "  ", "content": " " + "글" * 500 + " "}
        )
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["name"], "가" * 10)
        self.assertEqual(accepted.json()["content"], "글" * 500)
        for content in (" \n\t ", "글" * 501):
            with self.subTest(content_length=len(content)):
                response = self.client.post("/guestbook", json={"name": "검증", "content": content})
                self.assertEqual(response.status_code, 422)
        self.assertEqual(len(self.client.get("/guestbook").json()), 1)

    def test_routes_are_unique_and_portfolio_still_opens(self):
        for method in ("GET", "POST"):
            routes = [route for route in self.main.app.routes
                      if getattr(route, "path", None) == "/guestbook"
                      and method in getattr(route, "methods", set())]
            self.assertEqual(len(routes), 1)
        self.assertEqual(self.client.get("/portfolio").status_code, 200)


if __name__ == "__main__":
    unittest.main()
