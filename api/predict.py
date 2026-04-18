import os
import re
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert product price estimator. Given a product description,
estimate its price to the nearest dollar. Respond with ONLY the number, no dollar sign, no explanation."""


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            description = body.get("description", "").strip()
            if not description:
                raise ValueError("No description provided")

            api_key = os.environ.get("GROQ_API_KEY", "")
            if not api_key:
                raise ValueError("GROQ_API_KEY is not configured")

            payload = json.dumps({
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"What does this cost to the nearest dollar?\n\n{description}\n\nPrice is $"},
                ],
                "max_tokens": 20,
                "temperature": 0.1,
            }).encode()

            req = urllib.request.Request(
                GROQ_API_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())

            text = result["choices"][0]["message"]["content"].strip()
            cleaned = text.replace("$", "").replace(",", "").strip()
            match = re.search(r"\d+\.?\d*", cleaned)
            price = float(match.group()) if match else 0.0

            self._respond(200, {"price": price, "raw": text, "model": GROQ_MODEL})

        except Exception as e:
            self._respond(500, {"error": str(e)})

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._set_cors()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass
