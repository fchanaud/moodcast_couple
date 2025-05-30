from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Optional
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

# Storage - use JSON file as fallback
MOODS_FILE = "/tmp/moods.json"

def clear_temp_storage():
    """Clear temporary JSON storage to force Supabase usage"""
    try:
        if os.path.exists(MOODS_FILE):
            os.remove(MOODS_FILE)
            print("Cleared temporary JSON storage")
    except:
        pass

def load_moods():
    """Load moods from JSON file"""
    try:
        if os.path.exists(MOODS_FILE):
            with open(MOODS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_moods(moods):
    """Save moods to JSON file"""
    try:
        with open(MOODS_FILE, 'w') as f:
            json.dump(moods, f)
        return True
    except:
        return False

# Supabase client (with better error handling)
def get_supabase():
    """Get Supabase client if configured"""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        print(f"Supabase URL configured: {bool(url)}")
        print(f"Supabase Key configured: {bool(key)}")
        
        if url and key:
            from supabase import create_client
            client = create_client(url, key)
            
            # Test the connection by making a simple query
            try:
                test_result = client.table("moods").select("id").limit(1).execute()
                print("Supabase connection test successful")
                return client
            except Exception as e:
                print(f"Supabase connection test failed: {e}")
                return None
                
    except Exception as e:
        print(f"Supabase setup error: {e}")
    
    return None

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
            print("Pushover not configured")
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
        
        print(f"Pushover notification sent: {response.status_code == 200}")
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
async def save_mood(mood_data: MoodCreate):
    """Save a new mood and send notification"""
    try:
        # Validate input
        if mood_data.user not in ["clemence", "franklin"]:
            raise HTTPException(status_code=400, detail="Invalid user")
        
        if mood_data.weather not in WEATHER_EMOJIS:
            raise HTTPException(status_code=400, detail="Invalid weather")
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Try Supabase first
        supabase = get_supabase()
        
        if supabase:
            print("Using Supabase for save-mood")
            try:
                # Check if user already posted today in Supabase
                existing = supabase.table("moods").select("*").eq("user", mood_data.user).eq("date", today).execute()
                
                if existing.data:
                    print(f"User {mood_data.user} already posted today in Supabase")
                    raise HTTPException(status_code=400, detail="Mood already shared today")
                
                # Insert new mood into Supabase
                new_mood = {
                    "user": mood_data.user,
                    "weather": mood_data.weather,
                    "date": today,
                    "created_at": datetime.now().isoformat()
                }
                
                result = supabase.table("moods").insert(new_mood).execute()
                
                if not result.data:
                    raise Exception("Failed to save to Supabase")
                
                saved_mood = result.data[0]
                print(f"Mood saved to Supabase successfully")
                
            except HTTPException:
                raise
            except Exception as e:
                print(f"Supabase save error: {e}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        else:
            print("Using JSON fallback for save-mood")
            # Use JSON file storage as fallback
            moods = load_moods()
            
            # Check if user already posted today in JSON
            existing = [m for m in moods if m.get("user") == mood_data.user and m.get("date") == today]
            if existing:
                print(f"User {mood_data.user} already posted today in JSON")
                raise HTTPException(status_code=400, detail="Mood already shared today")
            
            # Create new mood
            saved_mood = {
                "id": len(moods) + 1,
                "user": mood_data.user,
                "weather": mood_data.weather,
                "date": today,
                "created_at": datetime.now().isoformat()
            }
            
            moods.append(saved_mood)
            save_moods(moods)
            print(f"Mood saved to JSON successfully")
        
        # Send notification
        notification_sent = send_pushover_notification(mood_data.user, mood_data.weather)
        
        return MoodResponse(
            success=True,
            mood=saved_mood,
            notificationSent=notification_sent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Save mood error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/get-moods", response_model=MoodsResponse)
async def get_moods():
    """Get recent moods"""
    try:
        # Try Supabase first
        supabase = get_supabase()
        
        if supabase:
            print("Using Supabase for get-moods")
            try:
                result = supabase.table("moods").select("*").order("created_at", desc=True).limit(10).execute()
                moods = result.data or []
                print(f"Retrieved {len(moods)} moods from Supabase")
            except Exception as e:
                print(f"Supabase get error: {e}")
                supabase = None
        
        if not supabase:
            print("Using JSON fallback for get-moods")
            # Use JSON file storage
            moods = load_moods()
            # Sort by created_at descending and limit to 10
            moods.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            moods = moods[:10]
            print(f"Retrieved {len(moods)} moods from JSON")
        
        return MoodsResponse(
            success=True,
            moods=moods
        )
        
    except Exception as e:
        print(f"Get moods error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/reminder")
async def send_reminder(request: Request):
    """Send reminder if no mood shared in 3+ days (cron endpoint)"""
    try:
        # Check authorization for cron job
        auth_header = request.headers.get("authorization")
        expected_auth = f"Bearer {os.getenv('CRON_SECRET')}"
        
        if auth_header != expected_auth:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Check for moods in last 3 days
        three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        
        # Try Supabase first
        supabase = get_supabase()
        recent_moods = []
        
        if supabase:
            try:
                result = supabase.table("moods").select("*").gte("date", three_days_ago).execute()
                recent_moods = result.data or []
            except Exception as e:
                print(f"Supabase error in reminder: {e}")
                supabase = None
        
        if not supabase:
            # Use JSON file storage
            moods = load_moods()
            recent_moods = [m for m in moods if m.get("date", "") >= three_days_ago]
        
        if recent_moods:
            return {
                "message": "No reminder needed",
                "reason": "Recent moods found",
                "count": len(recent_moods)
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

@app.get("/api/debug")
async def debug_info():
    """Debug endpoint to check configuration"""
    return {
        "supabase_url_configured": bool(os.getenv("SUPABASE_URL")),
        "supabase_key_configured": bool(os.getenv("SUPABASE_ANON_KEY")),
        "pushover_token_configured": bool(os.getenv("PUSHOVER_API_TOKEN")),
        "pushover_user_configured": bool(os.getenv("PUSHOVER_USER_KEY")),
        "cron_secret_configured": bool(os.getenv("CRON_SECRET")),
        "supabase_connection": bool(get_supabase())
    }

# Clear temporary storage on startup
clear_temp_storage()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 