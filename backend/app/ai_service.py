"""AI service: categorization, urgency detection, and reply generation via OpenAI-compatible API.

Includes a robust rule-based fallback that activates when:
- No API key is configured
- The API call fails (network, auth, rate limit)
- The response doesn't parse correctly

This ensures the app is always functional for demonstration.
"""

import json
import logging
import re
from typing import Optional

from openai import OpenAI
from openai import APIError, APIConnectionError, RateLimitError, APITimeoutError

from .config import settings

logger = logging.getLogger(__name__)

CATEGORIES = [
    "Work", "Personal", "Customer Support", "Sales", "Finance",
    "Meeting", "Application/Recruitment", "Newsletter", "Notification", "Spam", "Other"
]

URGENCIES = ["critical", "high", "medium", "low"]

# Some provider models only accept temperature=1 (thinking models). We normalize.
_FORCE_TEMP_1_MODELS = {"drytis/kimi", "drytis/kimi-k2.5", "drytis/kimi-k3",
                        "drytis/minimax-m2.7", "drytis/MiniMax-M3", "z-ai/glm-5"}


class ClassificationResult:
    def __init__(self, category: str, urgency: str, confidence: float,
                 explanation: str = "", needs_response: bool = False,
                 suggested_followup: bool = False):
        self.category = category
        self.urgency = urgency
        self.confidence = confidence
        self.explanation = explanation
        self.needs_response = needs_response
        self.suggested_followup = suggested_followup

    def to_dict(self):
        return {
            "category": self.category,
            "urgency": self.urgency,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "needs_response": self.needs_response,
            "suggested_followup": self.suggested_followup,
        }


def _get_client() -> Optional[OpenAI]:
    """Get an OpenAI client, or None if no key is available."""
    if not settings.openai_api_key:
        return None
    try:
        return OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=45.0,
        )
    except Exception as e:
        logger.warning(f"Could not initialize OpenAI client: {e}")
        return None


def _safe_temperature(desired: float) -> float:
    """Some models only accept temperature=1."""
    if settings.openai_model in _FORCE_TEMP_1_MODELS:
        return 1.0
    return desired


def _extract_json(text: str) -> dict:
    """Extract a JSON object from text that may contain markdown fences or extra text."""
    text = text.strip()
    # Remove markdown code fences
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the first { ... } block
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Last resort: find first { to last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not extract JSON from: {text[:200]}")


# ---- CATEGORIZATION ----

CATEGORIZE_PROMPT = """You are an expert email assistant. Analyze the email below and classify it.

Categories (choose exactly one): Work, Personal, Customer Support, Sales, Finance, Meeting, Application/Recruitment, Newsletter, Notification, Spam, Other

Urgency levels (choose exactly one): critical, high, medium, low
- critical: requires immediate action, legal/security threats, deadlines today
- high: important, needs action within 1-2 days, from boss/client
- medium: normal priority, needs a response this week
- low: FYI, newsletters, automated notifications, no response needed

Return ONLY valid JSON (no markdown, no explanation outside JSON):
{
  "category": "<one of the categories>",
  "urgency": "<critical|high|medium|low>",
  "confidence": <0.0-1.0>,
  "explanation": "<one short sentence explaining the classification>",
  "needs_response": <true if a reply is expected/needed>,
  "suggested_followup": <true if a follow-up reminder would be helpful>
}"""


def categorize_email(subject: str, body: str, sender: str = "") -> ClassificationResult:
    """Categorize an email using AI, with rule-based fallback."""
    text_for_ai = f"Subject: {subject}\nFrom: {sender}\n\nBody:\n{body[:2000]}"

    # Try AI first
    client = _get_client()
    if client:
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": CATEGORIZE_PROMPT},
                    {"role": "user", "content": text_for_ai},
                ],
                temperature=_safe_temperature(0.1),
                max_tokens=400,
            )
            raw = response.choices[0].message.content
            if not raw or not raw.strip():
                raise ValueError("Empty response from AI")

            data = _extract_json(raw)

            category = _normalize_category(data.get("category", "Other"))
            urgency = str(data.get("urgency", "medium")).lower()
            if urgency not in URGENCIES:
                urgency = "medium"
            confidence = float(data.get("confidence", 0.8))
            confidence = max(0.0, min(1.0, confidence))

            return ClassificationResult(
                category=category,
                urgency=urgency,
                confidence=confidence,
                explanation=data.get("explanation", ""),
                needs_response=bool(data.get("needs_response", False)),
                suggested_followup=bool(data.get("suggested_followup", False)),
            )
        except (APIError, APIConnectionError, RateLimitError, APITimeoutError) as e:
            logger.warning(f"AI categorization API error: {e}. Falling back to rules.")
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            logger.warning(f"AI categorization parse error: {e}. Falling back to rules.")
        except Exception as e:
            logger.warning(f"AI categorization unexpected error: {e}. Falling back to rules.")

    # Rule-based fallback
    return _rule_based_categorize(subject, body, sender)


def _normalize_category(raw: str) -> str:
    """Map AI output to our exact category names."""
    raw_lower = raw.lower().strip()
    mapping = {
        "work": "Work",
        "personal": "Personal",
        "customer support": "Customer Support",
        "support": "Customer Support",
        "sales": "Sales",
        "finance": "Finance",
        "billing": "Finance",
        "meeting": "Meeting",
        "application": "Application/Recruitment",
        "application/recruitment": "Application/Recruitment",
        "recruitment": "Application/Recruitment",
        "job": "Application/Recruitment",
        "newsletter": "Newsletter",
        "notification": "Notification",
        "spam": "Spam",
    }
    return mapping.get(raw_lower, raw if raw in CATEGORIES else "Other")


def _rule_based_categorize(subject: str, body: str, sender: str) -> ClassificationResult:
    """Fallback categorization using keyword rules."""
    text = f"{subject} {body}".lower()

    # Spam indicators
    spam_words = ["viagra", "cialis", "lottery", "winner", "congratulations you won",
                  "bitcoin investment", "crypto giveaway", "free money", "click here now",
                  "limited time offer", "act now", "double your", "guaranteed"]
    if any(w in text for w in spam_words):
        return ClassificationResult("Spam", "low", 0.85, "Detected spam keywords.")

    # Newsletter / notification patterns
    newsletter_words = ["unsubscribe", "manage preferences", "view in browser",
                        "this newsletter", "you're receiving this"]
    if any(w in text for w in newsletter_words):
        return ClassificationResult("Newsletter", "low", 0.75,
                                    "Contains newsletter markers (unsubscribe link).")

    notification_words = ["noreply", "no-reply", "notification", "automated message",
                          "do not reply", "security alert", "2fa", "verification code"]
    sender_lower = sender.lower()
    if any(w in text for w in notification_words) or any(w in sender_lower for w in ["noreply", "no-reply"]):
        if any(w in text for w in ["security", "login", "password", "verification", "otp"]):
            return ClassificationResult("Notification", "high", 0.7,
                                        "Automated security notification requiring attention.")
        return ClassificationResult("Notification", "low", 0.65, "Automated notification.")

    # Finance
    finance_words = ["invoice", "payment", "receipt", "billing", "statement",
                     "transaction", "refund", "charge", "bank", "salary", "payroll"]
    if any(w in text for w in finance_words):
        urgency = "high" if any(w in text for w in ["overdue", "failed", "urgent payment"]) else "medium"
        return ClassificationResult("Finance", urgency, 0.75, "Financial/billing content detected.")

    # Meeting
    meeting_words = ["meeting", "calendar invite", "schedule", "agenda",
                     "reschedule", "standup", "sync at", "catch up",
                     "appointment", "conference"]
    if any(w in text for w in meeting_words):
        urgency = "high" if any(w in text for w in ["today", "tomorrow", "reschedule", "urgent"]) else "medium"
        return ClassificationResult("Meeting", urgency, 0.75, "Meeting-related content.")

    # Application/Recruitment
    job_words = ["interview", "job application", "position", "candidate", "hiring",
                 "resume", "cv", "job offer", "recruitment", "applied for"]
    if any(w in text for w in job_words):
        urgency = "high" if "interview" in text or "offer" in text else "medium"
        return ClassificationResult("Application/Recruitment", urgency, 0.75,
                                    "Recruitment/application content.")

    # Customer Support
    support_words = ["ticket", "support request", "issue", "bug", "complaint",
                     "can't access", "problem with", "error", "help me",
                     "not working", "broken"]
    if any(w in text for w in support_words):
        urgency = "high" if any(w in text for w in ["urgent", "critical", "immediately", "asap"]) else "medium"
        return ClassificationResult("Customer Support", urgency, 0.7,
                                    "Support request or issue report.")

    # Sales
    sales_words = ["demo", "proposal", "pricing", "quote", "contract",
                   "deal", "discount", "buy now", "purchase", "subscribe",
                   "upgrade", "plan"]
    if any(w in text for w in sales_words):
        return ClassificationResult("Sales", "medium", 0.65, "Sales-related content.")

    # Personal
    personal_words = ["family", "dinner", "weekend", "vacation", "birthday",
                      "party", "congratulations", "how are you", "catch up",
                      "let's grab", "miss you"]
    if any(w in text for w in personal_words):
        return ClassificationResult("Personal", "low", 0.6, "Personal correspondence.")

    # Work (default for professional context)
    work_words = ["project", "report", "deadline", "team", "please review",
                  "attached", "re:", "fw:", "meeting notes", "action item"]
    if any(w in text for w in work_words):
        urgency = "high" if any(w in text for w in ["asap", "urgent", "deadline today",
                                                      "immediately", "critical"]) else "medium"
        return ClassificationResult("Work", urgency, 0.6, "Work-related content.")

    # Default
    return ClassificationResult("Other", "medium", 0.4,
                                "No strong category signal detected.")


# ---- REPLY GENERATION ----

REPLY_PROMPT = """You are an expert email assistant. Write a reply to the email below.

Tone: {tone}
- professional: formal, polite, business-appropriate
- friendly: warm, casual, conversational
- concise: brief, direct, to-the-point

Guidelines:
- Address the sender appropriately
- Reference the key points from the original email
- Be helpful and actionable
- Do NOT invent facts that are not in the original email
- Do NOT include a subject line — start directly with the greeting
- Write ONLY the reply body text, ready to send"""


def generate_reply(subject: str, body: str, sender_name: str = "",
                   tone: str = "professional") -> Optional[str]:
    """Generate an AI reply for an email, with template fallback."""
    tone_desc = {
        "professional": "formal, polite, business-appropriate",
        "friendly": "warm, casual, conversational",
        "concise": "brief, direct, to-the-point",
    }.get(tone, "formal, polite")

    client = _get_client()
    if client:
        try:
            greeting_name = sender_name.split()[0] if sender_name else "there"
            user_msg = (
                f"Subject: {subject}\n"
                f"From: {sender_name}\n\n"
                f"Original email:\n{body[:2000]}\n\n"
                f"Write the reply in a {tone_desc} tone."
            )
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": REPLY_PROMPT.format(tone=tone_desc)},
                    {"role": "user", "content": user_msg},
                ],
                temperature=_safe_temperature(0.7),
                max_tokens=600,
            )
            reply = response.choices[0].message.content
            if reply and reply.strip():
                return reply.strip()
        except (APIError, APIConnectionError, RateLimitError, APITimeoutError) as e:
            logger.warning(f"AI reply generation API error: {e}. Using template fallback.")
        except Exception as e:
            logger.warning(f"AI reply generation error: {e}. Using template fallback.")

    # Template fallback
    return _template_reply(subject, body, sender_name, tone)


def _template_reply(subject: str, body: str, sender_name: str, tone: str) -> str:
    """Generate a template-based reply as fallback."""
    greeting_name = sender_name.split()[0] if sender_name else "there"
    reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"

    templates = {
        "professional": (
            f"Hi {greeting_name},\n\n"
            f"Thank you for your email regarding \"{subject}\". "
            f"I have received your message and will review it shortly. "
            f"Rest assured, I will get back to you with a detailed response.\n\n"
            f"Best regards,\n[Your Name]"
        ),
        "friendly": (
            f"Hey {greeting_name}!\n\n"
            f"Thanks so much for reaching out about \"{subject}\". "
            f"I really appreciate you taking the time to write. "
            f"I'll take a look and circle back with you soon!\n\n"
            f"Cheers,\n[Your Name]"
        ),
        "concise": (
            f"Hi {greeting_name},\n\n"
            f"Received your email. I'll review and respond soon.\n\n"
            f"Best,\n[Your Name]"
        ),
    }
    return templates.get(tone, templates["professional"])
