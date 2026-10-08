import anthropic
import json
from app.config import settings

def analyze_email(subject: str, content: str) -> dict:
    if not settings.anthropic_api_key:
        return _mock_response(subject, content)

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        
        prompt = f"""Analyze the following email.
Subject: {subject}
Content: {content}

1. Categorize it into exactly one of: Work, Personal, Important, Spam.
2. Provide a confidence score between 0.0 and 1.0.
3. Write a 1-sentence summary.
4. Provide a brief reason for the category.
5. Generate a professional contextual reply based on the category and content.

Return ONLY a valid JSON object with the following keys:
- category (string)
- confidence (float)
- reason (string)
- summary (string)
- generated_reply (string)
"""
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            temperature=0.0,
            system="You are an AI Email Assistant. You must output strictly valid JSON with no markdown formatting, no preamble.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        data = json.loads(response_text.strip())
        
        if data.get("category") not in ["Work", "Personal", "Important", "Spam"]:
            data["category"] = "Work"
            
        return data

    except Exception as e:
        print(f"Error calling Claude: {e}")
        raise Exception("Failed to analyze email using Claude AI.")

def _mock_response(subject: str, content: str) -> dict:
    lower_content = (subject + " " + content).lower()
    category = "Work"
    if "offer" in lower_content or "lottery" in lower_content or "prince" in lower_content:
        category = "Spam"
    elif "family" in lower_content or "friend" in lower_content or "weekend" in lower_content:
        category = "Personal"
    elif "urgent" in lower_content or "asap" in lower_content or "important" in lower_content:
        category = "Important"
        
    reply = f"Thank you for your email regarding '{subject}'. I have received your message and will review the details shortly."
    if category == "Work":
        reply = "Thank you for the update. I will review the information and get back to you with my feedback."
    elif category == "Personal":
        reply = "Thanks for reaching out! It's great to hear from you. Let's catch up soon."
    elif category == "Spam":
        reply = "[No reply generated for spam]"
        
    return {
        "category": category,
        "confidence": 0.95,
        "reason": "This is a demo response based on simple keyword matching.",
        "summary": f"Demo summary of an email about {subject}.",
        "generated_reply": reply,
        "is_demo": True
    }
