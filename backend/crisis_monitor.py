import re

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "hurt myself", "end it all",
    "no reason to live", "better off dead", "cutting myself", "overdose"
]

HELPLINE_MESSAGE = """
I am detecting that you might be in distress. Please know that you are not alone and there is help available.

**Immediate Help:**
- **National Suicide Prevention Lifeline (India):** 9152987821
- **Vandrevala Foundation:** 1860 266 2345
- **iCall:** 022-25521111

If you are in immediate danger, please call emergency services (112) or go to the nearest hospital.
"""

def detect_crisis(text: str) -> bool:
    text_lower = text.lower()
    for keyword in CRISIS_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text_lower):
            return True
    return False
