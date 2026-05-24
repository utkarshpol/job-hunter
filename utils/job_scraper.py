from playwright.sync_api import sync_playwright
from urllib.parse import urljoin


def scrape_careers_page(url):
    jobs = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(
                url,
                wait_until="domcontentloaded"
            )
            page.wait_for_timeout(5000)

            # Scroll
            for _ in range(20):
                old_height = page.evaluate("() => document.body.scrollHeight")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                new_height = page.evaluate("() => document.body.scrollHeight")
                if old_height == new_height:
                    break

            links = page.locator("a").all()
            for link in links:
                try:
                    text = link.inner_text().strip()
                    href = link.get_attribute("href")
                    if not href or not text:
                        continue
                    full_url = urljoin(url, href)
                    jobs.append({
                        "title": text,
                        "url": full_url
                    })
                except Exception:
                    pass
    except Exception as e:
        print(f"Career page scraping failed for {url}: {e}")
    return jobs