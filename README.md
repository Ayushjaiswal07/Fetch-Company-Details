# 🕵️‍♂️ Company Data Extractor with Gemini AI

This project is a web-based tool built with **Streamlit** that allows users to submit a company's website URL and their email address. The tool:

1. Scrapes the website content and important subpages (like About, Contact, Services, Careers, etc.).
2. Extracts emails, phone numbers, addresses, and visible textual content.
3. Sends the scraped content to **Gemini AI** for structured analysis.
4. Emails the structured details to the user.

---

## 🚀 Features

- 🔗 Smart internal link discovery and filtering
- 🧠 Uses Google Gemini AI for content summarization
- ✉️ Sends structured data directly to the user via email
- 💻 Built with Python, Streamlit, and Google Generative AI
- 🌐 Streamlit form replaces traditional Google Forms

---

## 🧰 Tech Stack

- Python 3.10+
- Streamlit
- BeautifulSoup (bs4)
- Requests
- Google Generative AI (`google-generativeai`)
- Gmail SMTP (via `smtplib`)
- `.env` for secret management

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/company-data-extractor.git
cd company-data-extractor

# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
