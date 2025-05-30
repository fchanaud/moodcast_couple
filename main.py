from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import requests
from datetime import datetime, timedelta
from supabase import create_client, Client
import uvicorn

app = FastAPI(title="Moodcast API", description="API for sharing daily moods")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MoodCreate(BaseModel):
    user: str
    weather: str

class MoodResponse(BaseModel):
    success: bool
    mood: dict = None
    notificationSent: bool = False

class MoodsResponse(BaseModel):
    success: bool
    moods: list

# Supabase client
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")
    return create_client(url, key)

# Weather mappings
WEATHER_EMOJIS = {
    'sunny': '☀️', 'partly_sunny': '🌤️', 'cloudy': '☁️', 'overcast': '🌫️',
    'rainy': '🌧️', 'stormy': '⛈️', 'snowy': '❄️', 'windy': '💨', 'foggy': '🌁'
}

WEATHER_NAMES = {
    'sunny': 'ensoleillée', 'partly_sunny': 'avec éclaircies', 'cloudy': 'nuageuse',
    'overcast': 'couverte', 'rainy': 'pluvieuse', 'stormy': 'orageuse',
    'snowy': 'neigeuse', 'windy': 'venteuse', 'foggy': 'brumeuse'
}

def send_pushover_notification(user: str, weather: str) -> bool:
    """Send Pushover notification"""
    try:
        api_token = os.getenv("PUSHOVER_API_TOKEN")
        user_key = os.getenv("PUSHOVER_USER_KEY")
        
        if not api_token or not user_key:
            return False
            
        user_name = "Clémence" if user == "clemence" else "Franklin"
        device = "iphoneF" if user == "clemence" else "iphone"
        
        message = f"{user_name} a une météo {WEATHER_EMOJIS[weather]} {WEATHER_NAMES[weather]} aujourd'hui !"
        
        response = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": api_token,
            "user": user_key,
            "message": message,
            "title": "Moodcast - Nouvelle météo",
            "device": device
        })
        
        return response.status_code == 200
    except Exception as e:
        print(f"Pushover error: {e}")
        return False

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Page not found")

@app.post("/api/save-mood", response_model=MoodResponse)
async def save_mood(mood_data: MoodCreate, supabase: Client = Depends(get_supabase)):
    """Save a new mood and send notification"""
    try:
        # Validate input
        if mood_data.user not in ["clemence", "franklin"]:
            raise HTTPException(status_code=400, detail="Invalid user")
        
        if mood_data.weather not in WEATHER_EMOJIS:
            raise HTTPException(status_code=400, detail="Invalid weather")
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if user already posted today
        existing = supabase.table("moods").select("*").eq("user", mood_data.user).eq("date", today).execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Mood already shared today")
        
        # Insert new mood
        new_mood = {
            "user": mood_data.user,
            "weather": mood_data.weather,
            "date": today,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("moods").insert(new_mood).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save mood")
        
        # Send notification
        notification_sent = send_pushover_notification(mood_data.user, mood_data.weather)
        
        return MoodResponse(
            success=True,
            mood=result.data[0],
            notificationSent=notification_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/get-moods", response_model=MoodsResponse)
async def get_moods(supabase: Client = Depends(get_supabase)):
    """Get recent moods"""
    try:
        result = supabase.table("moods").select("*").order("created_at", desc=True).limit(10).execute()
        
        return MoodsResponse(
            success=True,
            moods=result.data or []
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/reminder")
async def send_reminder(request: Request, supabase: Client = Depends(get_supabase)):
    """Send reminder if no mood shared in 3+ days (cron endpoint)"""
    try:
        # Check authorization for cron job
        auth_header = request.headers.get("authorization")
        expected_auth = f"Bearer {os.getenv('CRON_SECRET')}"
        
        if auth_header != expected_auth:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Check for moods in last 3 days
        three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        
        recent_moods = supabase.table("moods").select("*").gte("date", three_days_ago).execute()
        
        if recent_moods.data:
            return {
                "message": "No reminder needed",
                "reason": "Recent moods found",
                "count": len(recent_moods.data)
            }
        
        # Send reminders
        api_token = os.getenv("PUSHOVER_API_TOKEN")
        user_key = os.getenv("PUSHOVER_USER_KEY")
        
        if not api_token or not user_key:
            raise HTTPException(status_code=500, detail="Pushover configuration missing")
        
        message = "🌤️ Cela fait plus de 3 jours sans nouvelles de vos météos intérieures !\n\nN'oubliez pas de partager comment vous vous sentez aujourd'hui. 💙"
        
        notifications = [
            {"device": "iphone", "user": "Clémence"},
            {"device": "iphoneF", "user": "Franklin"}
        ]
        
        results = []
        for notif in notifications:
            try:
                response = requests.post("https://api.pushover.net/1/messages.json", data={
                    "token": api_token,
                    "user": user_key,
                    "message": message,
                    "title": "Moodcast - Rappel de météo (3+ jours)",
                    "device": notif["device"],
                    "priority": 1,
                    "sound": "pushover"
                })
                
                results.append({
                    "device": notif["device"],
                    "user": notif["user"],
                    "success": response.status_code == 200
                })
            except Exception as e:
                results.append({
                    "device": notif["device"],
                    "user": notif["user"],
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "message": f"Reminders sent (3+ days without mood)",
            "sent": success_count,
            "total": len(notifications),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/test-reminder")
async def test_reminder():
    """Test reminder notifications"""
    try:
        api_token = os.getenv("PUSHOVER_API_TOKEN")
        user_key = os.getenv("PUSHOVER_USER_KEY")
        
        if not api_token or not user_key:
            raise HTTPException(status_code=500, detail="Pushover configuration missing")
        
        message = "🧪 TEST - N'oubliez pas de partager votre météo intérieure aujourd'hui !\n\nRendez-vous sur votre Moodcast pour dire comment vous vous sentez. 💙"
        
        notifications = [
            {"device": "iphone", "user": "Clémence"},
            {"device": "iphoneF", "user": "Franklin"}
        ]
        
        results = []
        for notif in notifications:
            try:
                response = requests.post("https://api.pushover.net/1/messages.json", data={
                    "token": api_token,
                    "user": user_key,
                    "message": message,
                    "title": f"TEST - Moodcast Rappel pour {notif['user']}",
                    "device": notif["device"],
                    "priority": 0,
                    "sound": "pushover"
                })
                
                results.append({
                    "device": notif["device"],
                    "user": notif["user"],
                    "success": response.status_code == 200
                })
            except Exception as e:
                results.append({
                    "device": notif["device"],
                    "user": notif["user"],
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        
        return {
            "message": "Test reminder sent",
            "sent": success_count,
            "total": len(notifications),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 