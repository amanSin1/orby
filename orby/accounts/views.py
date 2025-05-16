from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout  
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import CustomUser, Meeting
from .forms import MeetingForm

import openai
import json

# ---------------------- HOME ----------------------

def home(request):
    return render(request, 'accounts/home.html')


# ---------------------- AUTH ----------------------

def register_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        full_name = request.POST['full_name']
        mood = request.POST.get('mood', '')  # Optional mood
        profile_picture = request.FILES.get('profile_picture')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        
        user = CustomUser.objects.create_user(
            email=email,
            full_name=full_name,
            password=password,
            mood=mood,
            profile_picture=profile_picture
        )
        user.save()
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')
        
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# ---------------------- DASHBOARD ----------------------
from briefing.utils.briefing import generate_daily_brief
@login_required
def dashboard_view(request):
    now = timezone.now()
    ongoing_meetings = Meeting.objects.filter(
        user=request.user,
        start_time__lte=now,
        end_time__gte=now
    )
    context = {
        'user': request.user,
        
        'briefing': generate_daily_brief(request.user, request),
    }
    return render(request, 'accounts/dashboard.html', context)


# ---------------------- MEETINGS ----------------------

@login_required
def add_meeting(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.user = request.user
            meeting.save()
            return redirect('dashboard')
    else:
        form = MeetingForm()
    return render(request, 'accounts/add_meeting.html', {'form': form})


# ---------------------- CHATBOT (Page & API) ----------------------

@login_required
def chatbot_page(request):
    return render(request, 'accounts/chatbot.html')


import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from .models import Meeting
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now
from django.conf import settings
from .models import Meeting

import openai
import json

# Basic intent detection
def detect_intent(message):
    message = message.lower()
    if any(kw in message for kw in [" meetings schedule", "meetings", "schedule",  "show calendar"]):
        return "meeting_info"
    
    else:
        return "general"

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        try:
            # Parse message from request
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"response": "Please enter a message."})

            user = request.user
            current_time = now()

            # Detect intent
            intent = detect_intent(user_message)

            # Get user's upcoming meetings
            upcoming_meetings = Meeting.objects.filter(
                user=user,
                start_time__gte=current_time
            ).order_by('start_time')

            # Create a meeting summary if applicable
            meeting_summary = ""
            if upcoming_meetings.exists():
                meeting_summary = "Here are your upcoming meetings:\n"
                for m in upcoming_meetings:
                    meeting_summary += f"- {m.title} on {m.start_time.strftime('%A, %d %B %Y at %I:%M %p')}\n"
            else:
                meeting_summary = "You have no upcoming meetings scheduled."

            # Build system context based on intent
            system_prompt = "You are a helpful and emotionally supportive personal assistant chatbot."

            if intent == "meeting_info":
                system_prompt += (
                    "\nWhen the user asks about meetings, provide accurate information from this summary:\n"
                    + meeting_summary
                )
            # elif intent == "mental_health":
            #     system_prompt += (
            #         "\nThe user may be feeling emotional or stressed. Be gentle, kind, and supportive. "
            #         "Only mention meetings if they bring it up."
            #     )
            else:
                system_prompt += (
                    "\nKeep your responses helpful and polite. Only bring up meetings if the user explicitly asks."
                )

            # Initialize Mistral client
            openai.api_key = settings.MISTRAL_API_KEY
            client = openai.OpenAI(api_key=settings.MISTRAL_API_KEY, base_url="https://api.mistral.ai/v1")

            # Build messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # Get AI response from Mistral
            response = client.chat.completions.create(
                model="mistral-small",
                messages=messages
            )

            ai_reply = response.choices[0].message.content

        except Exception as e:
            print("Chatbot error:", str(e))
            ai_reply = "Something went wrong. Please try again later."

        return JsonResponse({"response": ai_reply})

    return JsonResponse({"error": "Only POST requests allowed."}, status=405)