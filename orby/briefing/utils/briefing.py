import os
import requests
from datetime import datetime, time
from django.conf import settings
from django.utils import timezone
from accounts.models import Meeting


def get_city_from_ip(ip):
    try:
        response = requests.get(f"https://ipapi.co/{ip}/json/")
        data = response.json()
        print(f"IP: {ip}, City: {data.get('city')}")  # Debug line
        return data.get("city", "New Delhi")
    except Exception:
        return "New Delhi"

    
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

# ---------------------- WEATHER ----------------------

def get_weather(city):
    """
    Fetches the current weather for the specified city.
    """
    api_key = settings.WEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("weather") and data.get("main"):
            description = data["weather"][0]["description"].capitalize()
            temperature = data["main"]["temp"]
            return f"🌤️ {description}, {temperature}°C in {city}"
        else:
            return "🌤️ Weather info unavailable."
    except Exception:
        return "🌤️ Failed to fetch weather."

# ---------------------- QUOTE ----------------------
def get_quote():
    """
    Fetches a random motivational quote.
    """
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            return f"🧠 {data[0]['q']} — {data[0]['a']}"
        else:
            return "🧠 Failed to fetch quote."
    except Exception:
        return "🧠 Error fetching quote."

# ---------------------- NEWS ----------------------
def get_news():
    """
    Fetches top news headlines for specified categories.
    """
    base_url = "https://newsapi.org/v2/top-headlines"
    categories = {
        "Technology 🖥️": "technology",
        "Health 🧬": "health"
    }
    news_sections = []

    for label, category in categories.items():
        headlines = []
        for region in ["in", None]:  # Try India first, then global
            params = {
                "apiKey": os.getenv("NEWS_API_KEY"),
                "category": category,
                "pageSize": 3,
                "language": "en"
            }
            if region:
                params["country"] = region
            try:
                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                articles = data.get("articles", [])
                if articles:
                    headlines = [f"• {a['title']}" for a in articles if a.get("title")]
                    break
            except Exception:
                continue
        if headlines:
            news_sections.append(f"{label}:\n" + "\n".join(headlines))
        else:
            news_sections.append(f"{label}:\n• No news available.")

    return news_sections

# ---------------------- DAILY BRIEFING ----------------------
def generate_daily_brief(user, request):
    """
    Generates a daily briefing for the user, including weather, quote, meetings, and news.
    """
    now = timezone.now()
    end_of_day = timezone.make_aware(datetime.combine(now.date(), time.max))

    # Fetch today's upcoming meetings
    today_meetings = Meeting.objects.filter(
        user=user,
        start_time__range=(now, end_of_day)
    )

    if today_meetings.exists():
        meeting_lines = [
            f"📅 {m.title} at {m.start_time.strftime('%I:%M %p')}" for m in today_meetings
        ]
    else:
        meeting_lines = ["📅 No upcoming meetings today."]

    # Fetch news and other components
    news_lines = get_news()
    ip = get_client_ip(request)  # get the user's IP
    
    city = get_city_from_ip(ip) 

    # Combine all components into the briefing
    briefing = "\n".join([

        get_weather(city),
        "",
        get_quote(),
        "",
        "📅 Upcoming Meetings Today:",
        *meeting_lines,
        "",
        "🗞️ Top News:",
        *news_lines
    ])

    return briefing