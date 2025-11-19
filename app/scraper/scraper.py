from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import re
import base64

class WebScraper:
    async def scrape_quiz_data(self, url: str):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")

            content = await page.content()
            await browser.close()

            soup = BeautifulSoup(content, 'html.parser')

            # 1. Extract visible text and questions
            questions = self._extract_questions(soup)

            # 2. Find submission URL
            submission_url = self._find_submission_url(soup)

            # 3. Find and decode hidden content from script tags
            hidden_data = self._find_and_decode_atob(soup)

            return {
                "raw_html": content,
                "questions": questions,
                "submission_url": submission_url,
                "hidden_data": hidden_data
            }

    def _extract_questions(self, soup: BeautifulSoup):
        # A simple heuristic: find text that looks like a question.
        # This can be significantly improved with more sophisticated rules.
        questions = []
        for tag in soup.find_all(['p', 'div', 'label']):
            text = tag.get_text(strip=True)
            if '?' in text and len(text) > 15:
                questions.append(text)
        return questions

    def _find_submission_url(self, soup: BeautifulSoup):
        # Look for a form's action attribute
        form = soup.find('form')
        if form and form.has_attr('action'):
            return form['action']

        # Look for a link that might be a submission button
        for a in soup.find_all('a'):
            if 'submit' in a.get_text(strip=True).lower():
                return a.get('href')
        return None

    def _find_and_decode_atob(self, soup: BeautifulSoup):
        decoded_strings = []
        # Regex to find atob("...") patterns in script tags
        atob_pattern = re.compile(r'atob\("([^"]+)"\)')

        for script in soup.find_all('script'):
            if script.string:
                matches = atob_pattern.findall(script.string)
                for match in matches:
                    try:
                        decoded = base64.b64decode(match).decode('utf-8')
                        decoded_strings.append(decoded)
                    except Exception as e:
                        # Ignore strings that are not valid base64
                        pass
        return decoded_strings

async def main():
    scraper = WebScraper()
    # Replace with a real URL for testing if needed
    test_url = "http://example.com"
    data = await scraper.scrape_quiz_data(test_url)
    print("Scraping complete.")
    print(data)

if __name__ == "__main__":
    asyncio.run(main())
