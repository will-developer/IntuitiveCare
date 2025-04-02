import abc  # For creating abstract base classes

class HtmlParser(abc.ABC):
    """Abstract interface for HTML parsing operations"""

    @abc.abstractmethod
    def find_links_ending_with(self, 
                             base_url: str,    # Base URL to resolve relative links
                             content: str,     # HTML content to parse
                             extension: str    # Target file extension (e.g. '.pdf')
                            ) -> list[str]:    # Returns list of absolute URLs
        """
        Finds all hyperlinks in HTML content that end with specific extension
        """
        pass