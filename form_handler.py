import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import google.generativeai as genai
from dotenv import load_dotenv

class FormHandler:
    def __init__(self):
        load_dotenv()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not self.gemini_api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")

        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def get_internal_links(self, base_url, soup):
        domain = urlparse(base_url).netloc
        links = set()

        for a in soup.find_all("a", href=True):
            href = a['href'].strip()
            if href.startswith("#") or href.startswith("javascript:"):
                continue
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == domain:
                links.add(full_url)

        return list(links)

    def filter_relevant_links(self, urls):
        include_keywords = [
            "about", "contact", "service", "solution", "product", 
            "career", "job", "team", "opening", "technology", "support"
        ]
        exclude_keywords = [
            "privacy", "terms", "conditions", "policy", "disclaimer", 
            "login", "signup", "partners", "executive", "newsletter", 
            "media", "press", "blog", "faq", "cookie", "events"
        ]

        filtered = []
        for url in urls:
            url_lower = url.lower()
            if any(ex_kw in url_lower for ex_kw in exclude_keywords):
                continue
            if any(in_kw in url_lower for in_kw in include_keywords):
                filtered.append(url)

        return list(set(filtered))

    def scrape_html(self, url):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"⚠️ Error scraping {url}: {e}")
            return ""

    def extract_contact_details(self, soup):
        emails = set()
        phones = set()
        addresses = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "mailto:" in href:
                emails.add(href.replace("mailto:", "").strip())
            if "tel:" in href:
                phones.add(href.replace("tel:", "").strip())

        text = soup.get_text(separator=' ', strip=True)
        for line in text.split("\n"):
            if any(loc in line.lower() for loc in ["address", "houston", "india", "texas", "usa"]):
                addresses.append(line.strip())

        return {
            "emails": list(emails),
            "phones": list(phones),
            "addresses": list(set(addresses))
        }

    def clean_json_string(self, response_text):
        # Remove triple backtick blocks if present
        cleaned = re.sub(r"```json|```", "", response_text.strip())
        return cleaned

    def ask_gemini_for_data(self, text, contact_data):
        prompt = (
            "From the following content and detected contact data, extract only this information in pure JSON "
            "(without markdown, without text, without ```json blocks):\n\n"
            "{\n"
            "  \"company_name\": string,\n"
            "  \"contact_numbers\": [string],\n"
            "  \"email_addresses\": [string],\n"
            "  \"locations\": [string],\n"
            "  \"available_jobs\": [string],\n"
            "  \"technologies_used\": [string]\n"
            "}\n\n"
            f"Detected emails: {contact_data['emails']}\n"
            f"Detected phones: {contact_data['phones']}\n"
            f"Detected addresses: {contact_data['addresses']}\n\n"
            f"Website Content:\n{text[:16000]}"
        )

        print("Fetching details...")
        try:
            result = self.model.generate_content(prompt)
            response_text = result.text.strip() if result and result.text else ""
            cleaned_text = self.clean_json_string(response_text)
            try:
                return json.loads(cleaned_text)
            except Exception as e:
                print("❌ Failed to parse Gemini response as JSON:", e)
                print("Raw response:\n", response_text)
                return None
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            return None

    def process_website(self, base_url):
        print(f"\n🌐 Processing: {base_url}")
        homepage_html = self.scrape_html(base_url)

        if not homepage_html:
            print("❌ Homepage content is empty.")
            return

        homepage_soup = BeautifulSoup(homepage_html, "html.parser")
        homepage_text = homepage_soup.get_text(separator=' ', strip=True)
        base_contact_data = self.extract_contact_details(homepage_soup)

        all_text = homepage_text
        all_contact_data = base_contact_data.copy()

        links = self.get_internal_links(base_url, homepage_soup)
        filtered_links = self.filter_relevant_links(links)

        # print(f"🔍 Found {len(filtered_links)} potentially useful pages")

        for link in filtered_links:
            # print(f"🔗 Scraping: {link}")
            page_html = self.scrape_html(link)
            if not page_html:
                continue

            soup = BeautifulSoup(page_html, "html.parser")
            all_text += "\n\n" + soup.get_text(separator=' ', strip=True)
            data = self.extract_contact_details(soup)
            all_contact_data['emails'].extend(data['emails'])
            all_contact_data['phones'].extend(data['phones'])
            all_contact_data['addresses'].extend(data['addresses'])

        # Deduplicate contact data
        all_contact_data['emails'] = list(set(all_contact_data['emails']))
        all_contact_data['phones'] = list(set(all_contact_data['phones']))
        all_contact_data['addresses'] = list(set(all_contact_data['addresses']))

        extracted_info = self.ask_gemini_for_data(all_text, all_contact_data)

        if extracted_info:
            return extracted_info
        else:
            print("❌ No data extracted from Gemini.")
