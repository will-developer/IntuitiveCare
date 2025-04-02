import logging
from typing import List
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.application.ports.html_parser import HtmlParser

logger = logging.getLogger(__name__)

class Bs4HtmlParser(HtmlParser):
    """BeautifulSoup implementation for HTML parsing operations."""

    def find_links_ending_with(self, base_url: str, content: str, extension: str) -> List[str]:
        """Finds all hyperlinks ending with specified extension. """
        links = []
        try:
            soup = BeautifulSoup(content, 'html.parser')  # Parse HTML with bs4
            normalized_extension = extension.lower().strip('.')  # Normalize extension format

            # Find all anchor tags with href attributes
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith(f'.{normalized_extension}'):
                    full_url = urljoin(base_url, href)  # Convert to absolute URL
                    links.append(full_url)
                    logger.debug(f"Matched link: {full_url}")

            # Log appropriate result summary
            if not links:
                logger.warning(f"No {extension} links found at {base_url}")
            else:
                logger.info(f"Found {len(links)} {extension} links at {base_url}")

        except Exception as e:
            logger.error(f"HTML parsing failed for {base_url}: {e}", exc_info=True)
            raise  # Re-raise to allow caller handling

        return links