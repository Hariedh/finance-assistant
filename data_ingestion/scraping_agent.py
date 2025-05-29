import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingAgent:
    def scrape_filings(self, url: str) -> str:
        """Scrape text content from a financial news URL."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            return " ".join(p.get_text().strip() for p in paragraphs)
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return ""