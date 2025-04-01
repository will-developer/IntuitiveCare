import requests
import logging
from typing import Optional
from ..core.ports.gateways import HttpGateway

class RequestsHttpGateway(HttpGateway):
    def get_content(self, url: str, timeout: int) -> Optional[str]:
        # Log the HTTP request attempt
        logging.debug(f"Requesting content from: {url} using Requests")
        
        try:
            # Make HTTP GET request with specified timeout
            response = requests.get(url, timeout=timeout)
            
            # Raise exception if HTTP request failed (status code >= 400)
            response.raise_for_status()
            
            # Log successful content fetch
            logging.info(f"Successfully fetched content from: {url}")
            
            # Return the response content as text
            return response.text
            
        except requests.exceptions.RequestException as e:
            # Log any request-related errors (connection, timeout, HTTP errors)
            logging.error(f"Requests failed to fetch page {url}: {e}")
            
            # Return None if request fails
            return None