import logging
from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.application.ports.html_parser import HtmlParser

logger = logging.getLogger(__name__)

class Bs4HtmlParser(HtmlParser):
    def find_links_ending_with(self, base_url: str, content: str, extension: str) -> List[str]:
        links = []
        try:
            soup = BeautifulSoup(content, 'html.parser')
            normalized_extension = extension.lower().strip('.')

            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith(f'.{normalized_extension}'):
                    full_url = urljoin(base_url, href)
                    links.append(full_url)
                    logger.debug(f"Found link ending with '.{normalized_extension}': {full_url}")

            if not links:
                logger.warning(f"No links ending with '.{normalized_extension}' found at base URL {base_url}")
            else:
                logger.info(f"Found {len(links)} links ending with '.{normalized_extension}' at base URL {base_url}")

        except Exception as e:
            logger.error(f"Error parsing HTML content from base URL {base_url}: {e}")

        return links