import requests.compat
from bs4 import BeautifulSoup
import logging
from typing import List
from ..core.ports.gateways import HtmlParser

class BeautifulSoupHtmlParser(HtmlParser):
    def find_links(self, html_content: str, base_url: str, selector: str, keywords: List[str], suffix: str) -> List[str]:
        # Start parsing HTML content with BeautifulSoup
        logging.debug("Parsing HTML content using BeautifulSoup.")
        soup = BeautifulSoup(html_content, 'html.parser')  # Create BeautifulSoup object
        pdf_links = []  # List to store matching links
        found_links = soup.select(selector)  # Find all elements matching CSS selector

        # Return empty list if no elements found
        if not found_links:
            logging.warning(f"BeautifulSoup found no elements with selector '{selector}'.")
            return []

        # Check each found link for matching criteria
        for link in found_links:
            href = link.get('href', '')  # Get href attribute
            link_text = link.text.strip()  # Get link text and remove whitespace

            # Check if link text contains any of the keywords
            has_keyword = any(keyword in link_text for keyword in keywords)
            # Check if href ends with required suffix and has keyword
            if href.endswith(suffix) and has_keyword:
                # Convert relative URLs to absolute URLs
                absolute_href = href if href.startswith('http') else requests.compat.urljoin(base_url, href)
                pdf_links.append(absolute_href)  # Add matching link to results
                logging.debug(f"Found matching link via BeautifulSoup: {absolute_href}")

        # Log results of search
        if not pdf_links:
            logging.warning(f"BeautifulSoup found no links matching criteria.")
        else:
            logging.info(f"BeautifulSoup extracted {len(pdf_links)} PDF links.")
        return pdf_links  # Return list of matching PDF links