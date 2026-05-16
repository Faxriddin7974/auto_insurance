import os
from pathlib import Path
from google import genai
from flask import Blueprint, request, jsonify
from collections import deque
from threading import Lock
import time

chat_bp = Blueprint("chat", __name__)

# ---------------- RATE LIMIT ----------------
REQUEST_LIMIT = int(os.environ.get("CHAT_REQUEST_LIMIT", "10"))
WINDOW_SIZE = int(os.environ.get("CHAT_WINDOW_SECONDS", "60"))

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = Lock()

    def is_allowed(self) -> bool:
        with self.lock:
            now = time.time()

            while self.requests and self.requests[0] < now - self.window_seconds:
                self.requests.popleft()

            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True

            return False

rate_limiter = RateLimiter(REQUEST_LIMIT, WINDOW_SIZE)

# ---------------- ENV LOAD ----------------
def load_local_dotenv():
    env_path = Path(__file__).resolve().parents[1] / ".env"

    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)

                    os.environ.setdefault(
                        key.strip(),
                        value.strip().strip('"').strip("'")
                    )

load_local_dotenv()

# ---------------- GEMINI ----------------
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

if not API_KEY:
    raise ValueError("GEMINI_API_KEY topilmadi")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
Sen AvtoSugurta Pro AI yordamchisisan.

QOIDALAR:
- Faqat avtomobil sug'urtasi haqida gapir.
- O'zbek tilida javob ber.
- Javoblaring aniq, to'liq va ijodiy bo'lsin.
- Hech qachon o'rta chog'da to'xtama.
- Paketlardan tashqariga chiqma.

MAVJUD PAKETLAR:
1. Basic - faqat majburiy OSAGO.
2. Comfort - Basic + evakuator + 24/7 yordam.
3. Max - to'liq KASKO+.

TAVSIYA QOIDALARI:
- Yangi mashina → Basic yoki Comfort.
- O'rtacha holat → Comfort.
- Qimmat / xavfli mashina → Max.
- To'liq himoya so'ralsa yoki KASKO+ kerak bo'lsa → Max.

Javob formatini shu tarzda bering:
1. Qisqacha xulosa
2. Har bir paket ta'rifi va foydasi
3. Yakuniy tavsiya

Agar ma'lumot yetarli bo'lmasa, avvalo model, yil va avtomobil holati haqida qo'shimcha savol so'rang.
"""

# ---------------- ROUTE ----------------
@chat_bp.route("/chat", methods=["POST"])
def chat():

    if not rate_limiter.is_allowed():
        return jsonify({"reply": "Limit oshdi, keyinroq urinib ko'ring"}), 429

    data = request.get_json()

    if not data:
        return jsonify({"reply": "JSON yo'q"}), 400

    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Xabar bo'sh"}), 400

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                {"role": "MODEL", "parts": [{"text": SYSTEM_INSTRUCTION}]},
                {"role": "USER", "parts": [{"text": user_message}]},
            ],
            config={
                "temperature": 0.45,
                "top_p": 0.95,
                "max_output_tokens": 900,
            }
        )

        return jsonify({
            "reply": response.text or "Javob topilmadi"
        })

    except Exception as e:

        error_msg = str(e)
        print("Gemini error:", error_msg)

        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return jsonify({"reply": "API limit tugagan"}), 429

        if "API_KEY" in error_msg:
            return jsonify({"reply": "API key xato"}), 401

        return jsonify({"reply": "Server xatolik"}), 500