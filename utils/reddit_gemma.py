import ollama 
import json
import re

def default_output():
    return {
        "estimated_ctc": "Unknown",
        "legitimacy": "Unknown",
        "interview_difficulty": "Unknown",
        "work_culture": "Unknown",
        "important_notes": [],
        "sources": []
    }

def analyze_with_gemma(company, title, snippets):
    if not snippets:
        return default_output()
    context = "\n---\n".join([item["text"] for item in snippets[:15]])
    prompt = f"""
You are an expert career intelligence analyst.
Analyze these Reddit discussions.
Company: {company}
Role: {title}
Return STRICT JSON ONLY:
{{
  "estimated_ctc": "",
  "legitimacy": "",
  "interview_difficulty": "",
  "work_culture": "",
  "important_notes": [],
  "sources": []
}}
If information is missing,
return "Unknown".
REDDIT DATA:
{context}
"""
    try:
        response = ollama.chat(
            model="gemma3:4b",
            messages=[{
                    "role": "user",
                    "content": prompt
                }],
            options={"temperature": 0.1})
        content = response["message"]["content"].strip()
        return parse_gemma_output(content, snippets)
    except Exception as e:
        print("Gemma error:", e)
        return default_output()

def parse_gemma_output(raw_output,snippets):
    try:
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if not match:
            return default_output()
        parsed = json.loads(match.group())
        parsed["sources"] = list(set([item["source"] for item in snippets if item["source"]]))
        return parsed
    except Exception:
        return default_output()