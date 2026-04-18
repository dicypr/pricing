import os
import re
import json
from http.server import BaseHTTPRequestHandler


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert product price estimator. Given a product description,
estimate its price to the nearest dollar. Respond with ONLY a number like: Price is $X.00"""


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_length))
            description = body.get("description", "")

            api_key = os.environ.get("GROQ_API_KEY", "")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set")

            import urllib.request

            payload = json.dumps({
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"What does this cost?\n\n{description}\n\nPrice is $"},
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
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())

            text = result["choices"][0]["message"]["content"]
            match = re.search(r"[\d,]+\.?\d*", text.replace("$", "").replace(",", ""))
            price = float(match.group()) if match else 0.0

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "price": price,
                "raw": text,
                "model": GROQ_MODEL,
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        pass
