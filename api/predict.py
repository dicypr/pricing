from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        description = body.get("description", "")

        groq_key = os.environ.get("GROQ_API_KEY", "")
        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a product pricing expert. Reply with ONLY the numeric price, no $ sign or explanation."},
                {"role": "user", "content": f"What does this product cost to the nearest dollar?\n\n{description}\n\nPrice is $"}
            ],
            "max_tokens": 16
        }).encode()

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())

        raw = result["choices"][0]["message"]["content"].strip()
        try:
            price = float(raw.replace("$","").replace(",","").split()[0])
        except:
            price = 0.0

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"price": price, "raw": raw, "model": "llama-3.3-70b-versatile"}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
