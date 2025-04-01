import requests
import logging
from typing import Optional
from ..core.ports.gateways import HttpGateway

class RequestsHttpGateway(HttpGateway):
    def get_content(self, url: str, timeout: int) -> Optional[str]:
        logging.debug(f"Requesting content from: {url} using Requests")
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            logging.info(f"Successfully fetched content from: {url}")
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Requests failed to fetch page {url}: {e}")
            return None