import google.generativeai as genai  # type: ignore
import os
import random
import re
import json
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)  # type: ignore

SYSTEM_PROMPT = """
You are a compassionate, non-judgmental mental health support chatbot.
Your goal is to provide emotional support using principles of Cognitive Behavioral Therapy (CBT).
- Validate the user's feelings first.
- Ask gentle, open-ended questions to help them explore their thoughts.
- Keep responses concise (under 3 sentences) unless explaining a concept.
- DO NOT diagnose or prescribe medication.
- If the user seems overwhelmed, suggest ground techniques (e.g., 5-4-3-2-1 technique).
"""

model = genai.GenerativeModel('gemini-2.5-flash') if API_KEY else None  # type: ignore

def _is_affirmative_short(text: str) -> bool:
    t = text.strip().lower()
    affirm = ["yes", "yeah", "yep", "ok", "okay", "sure", "please", "ya", "y"]
    return any(re.fullmatch(rf"{a}", t) for a in affirm)


def generate_local_response(text: str, history: Optional[List] = None) -> str:
    t = text.lower()
    if history:
        try:
            for item in reversed(history):
                if item.get("role") == "assistant":
                    parts = item.get("parts") or item.get("content") or []
                    last_assistant = " ".join(parts) if isinstance(parts, list) else str(parts)
                    la = last_assistant.lower()
                    if ("detailed steps" in la or "more detailed" in la) and _is_affirmative_short(text):
                        return (
                            "Here are some step-by-step actions you can try:\n"
                            "1) Breathing: Sit comfortably. Inhale for 4 seconds, hold 4, exhale for 6. Repeat 4 times.\n"
                            "2) Grounding: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste — move slowly through each.\n"
                            "3) Micro-action: If possible, step outside for 2–5 minutes and notice one small sensory detail.\n"
                            "4) Reflection: Write one thing you're grateful for and one small next-step.\n"
                            "Would you like to try one of these together now?"
                        )
                    break
        except Exception:
            pass

    if ("detailed" in t and "step" in t) or "give the detailed steps" in t:
        return (
            "Here are some step-by-step actions you can try:\n"
            "1) Breathing: Sit comfortably. Inhale for 4 seconds, hold 4, exhale for 6. Repeat 4 times.\n"
            "2) Grounding: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.\n"
            "3) Micro-action: Step outside for 2–5 minutes and notice one sensory detail.\n"
            "4) Reflection: Write one thing you're grateful for and one small next-step.\n"
            "Would you like to try one of these together now?"
        )

    if any(w in t for w in ["suicide", "kill myself", "hurt myself", "want to die"]):
        return "I'm really sorry you're feeling this way. If you are in immediate danger please contact local emergency services or a crisis hotline right now. Can you tell me if you're safe at this moment?"
    if any(w in t for w in ["sad", "depressed", "down"]):
        options = [
            "I'm sorry you're feeling sad. What do you think is making you feel this way?",
            "That sounds really heavy. Would you like to talk about what happened today?",
            "I hear you — feeling down is hard. What's been on your mind most recently?"
        ]
        return random.choice(options)
    if any(w in t for w in ["stress", "stressed", "anxious", "anxiety"]):
        tips = [
            "Try a simple breathing exercise: inhale 4s, hold 4s, exhale 6s — repeat a few times.",
            "Grounding can help: name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
            "Sometimes a short walk or stretching helps reset stress — would you like a few more ideas?"
        ]
        return random.choice(tips)
    if any(w in t for w in ["suggest", "how", "what can i do", "help me"]):
        return "Here are a few small steps you could try: take three slow breaths, step outside for a minute, and write one thing you're grateful for. Would you like more detailed steps?"
    generics = [
        "Thanks for sharing. I'm here to listen — can you tell me more about that?",
        "That sounds important. How long have you been feeling like this?",
        "I appreciate you telling me. What happened just before you felt this way?"
    ]
    return random.choice(generics)

async def get_ai_response(user_input: str, chat_history: Optional[List] = None) -> str:
    if chat_history is None:
        chat_history = []
    if not API_KEY or model is None:
        return generate_local_response(user_input, chat_history)

    try:
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        try:
            return generate_local_response(user_input, chat_history)
        except Exception:
            return "Thanks for sharing. I'm here to listen — can you tell me more about that?"

async def get_recommendations(history_texts: list) -> list:
    if not history_texts or not model or not API_KEY:
        return [
            "I'm feeling anxious about...",
            "How do I manage stress?",
            "I'm having trouble sleeping."
        ]
    
    prompt = f"""
    Analyze these anonymous mental health check-in topics:
    {history_texts[:10]}
    
    Based on these, suggest 3 short, empathetic conversation starters for a new user.
    Return ONLY a JSON list of strings. Example: ["I feel overwhelmed.", "Help me relax."]
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return [
            "I feel overwhelmed lately.",
            "Can you help me relax?",
            "I'm feeling down today."
        ]
