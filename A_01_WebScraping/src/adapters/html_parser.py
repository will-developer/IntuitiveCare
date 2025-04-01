import requests.compat
from bs4 import BeautifulSoup
import logging
from typing import List
from ..core.ports.gateways import HtmlParser

class BeautifulSoupHtmlParser(HtmlParser):
    def find_links(self, html_content: str, base_url: str, selector: str, keywords: List[str], suffix: str) -> List[str]:
        logging.debug("Parsing HTML content using BeautifulSoup.")
        soup = BeautifulSoup(html_content, 'html.parser')
        pdf_links = []
        found_links = soup.select(selector)

        if not found_links:
            logging.warning(f"BeautifulSoup found no elements with selector '{selector}'.")
            return []

        for link in found_links:
            href = link.get('href', '')
            link_text = link.text.strip()

            has_keyword = any(keyword in link_text for keyword in keywords)
            if href.endswith(suffix) and has_keyword:
                absolute_href = href if href.startswith('http') else requests.compat.urljoin(base_url, href)
                pdf_links.append(absolute_href)
                logging.debug(f"Found matching link via BeautifulSoup: {absolute_href}")

        if not pdf_links:
            logging.warning(f"BeautifulSoup found no links matching criteria.")
        else:
            logging.info(f"BeautifulSoup extracted {len(pdf_links)} PDF links.")
        return pdf_links