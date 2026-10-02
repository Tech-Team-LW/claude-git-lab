import http.server
import threading
import unittest

from devops_portal import services, storage


class QuietHandler(http.server.BaseHTTPRequestHandler):
    """Answers 200 on /health and 500 everywhere else."""

    def do_GET(self):
        self.send_response(200 if self.path == "/health" else 500)
        self.end_headers()

    def log_message(self, *args):
        pass  # keep test output clean


class ServiceDataTests(unittest.TestCase):
    def setUp(self):
        self.data = storage.empty_data()

    def test_add_service(self):
        services.add_service(self.data, "web", "http://localhost:5000/health")
        self.assertEqual(services.find_service(self.data, "WEB")["url"],
                         "http://localhost:5000/health")

    def test_add_rejects_url_without_scheme(self):
        with self.assertRaises(ValueError):
            services.add_service(self.data, "web", "localhost:5000")

    def test_add_rejects_duplicate(self):
        services.add_service(self.data, "web", "http://a")
        with self.assertRaises(ValueError):
            services.add_service(self.data, "Web", "http://b")

    def test_remove_service(self):
        services.add_service(self.data, "web", "http://a")
        services.remove_service(self.data, "web")
        self.assertEqual(self.data["services"], [])

    def test_remove_missing_service(self):
        with self.assertRaises(ValueError):
            services.remove_service(self.data, "web")


class CheckUrlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Port 0 lets the OS pick a free port.
        cls.server = http.server.HTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_healthy_url_is_up(self):
        self.assertEqual(services.check_url(self.base + "/health"), (True, "HTTP 200"))

    def test_error_status_is_down(self):
        self.assertEqual(services.check_url(self.base + "/broken"), (False, "HTTP 500"))

    def test_unreachable_url_is_down(self):
        # Grab a free port, then close it so nothing is listening there.
        probe = http.server.HTTPServer(("127.0.0.1", 0), QuietHandler)
        port = probe.server_port
        probe.server_close()

        is_up, detail = services.check_url(f"http://127.0.0.1:{port}/", timeout=1)
        self.assertFalse(is_up)
        self.assertTrue(detail)


if __name__ == "__main__":
    unittest.main()
