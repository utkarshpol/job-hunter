from playwright.sync_api import sync_playwright
import ollama # type: ignore
import json
import re


PROMPT = """
Extract:

- title
- experience
- skills
- location
- description

Return STRICT JSON only.
"""


def extract_job_details(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(4000)
            text = page.locator("body").inner_text()
            browser.close()

        response = ollama.chat(
            model="gemma3:4b",
            messages=[
                {
                    "role": "user",
                    "content":
                    PROMPT + "\n\n" + text[:15000]
                }
            ]
        )

        content = response["message"]["content"]
        parsed = parse_llm_json(content)

        if parsed:
            return parsed

        return {
            "error": "Could not parse",
            "raw_output": content,
            "job_url": url
        }
    except Exception as e:
        print(f"Job details extraction failed for {url}: {e}")
        return {
            "error": "extraction_failed",
            "message": str(e),
            "job_url": url
        }

def parse_llm_json(content):
    try:
        # Remove markdown fences
        content = re.sub(
            r"```json|```",
            "",
            content
        ).strip()
        # Extract JSON object or array
        match = re.search(
            r"(\{.*\}|\[.*\])",
            content,
            re.DOTALL
        )
        if not match:
            return None
        cleaned = match.group()
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            if len(parsed) > 0 and isinstance(parsed[0], dict):
                return parsed[0]
            return None
        if isinstance(parsed, dict):
            return parsed
        return None
    except Exception as e:
        print("JSON Parse Error:", e)
        return None