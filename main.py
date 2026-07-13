from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import urllib.parse
import os

app = FastAPI()

# ── الـ Domain بتاع Railway ──
DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost:8000")
BASE_URL = f"https://{DOMAIN}"

# CORS عشان المتصفح مايحظرش الطلبات
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── بيانات Google OAuth ──
CLIENT_ID = "241164673641-mo4maeohonm88gimi77obvjqoa01m98p.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = f"{BASE_URL}/auth/callback"

# ── مسار الصفحة الرئيسية ──
@app.get("/", response_class=HTMLResponse)
@app.get("/game", response_class=HTMLResponse)
def game_page():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# ── توجيه المستخدم لجوجل ──
@app.get("/auth/login")
def login():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&prompt=select_account"
    )
    return RedirectResponse(url=google_auth_url)

# ── استقبال رد جوجل ──
@app.get("/auth/callback")
def callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    token_response = requests.post(token_url, data=data).json()
    access_token = token_response.get("access_token")

    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info = requests.get(user_info_url, headers=headers).json()

    name = urllib.parse.quote(user_info.get("name", ""))
    email = urllib.parse.quote(user_info.get("email", ""))
    picture = urllib.parse.quote(user_info.get("picture", ""))
    return RedirectResponse(url=f"{BASE_URL}/game?login=true&username={name}&email={email}&picture={picture}")

# ── تسجيل خروج ──
@app.get("/auth/logout")
def logout():
    return RedirectResponse(url=f"{BASE_URL}/game")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
