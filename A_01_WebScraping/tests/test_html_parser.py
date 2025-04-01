import pytest
from src.adapters.html_parser import BeautifulSoupHtmlParser

# Fixture that provides a BeautifulSoupHtmlParser instance for tests
@pytest.fixture
def html_parser():
    return BeautifulSoupHtmlParser()

# Constants used in tests
BASE_URL = "http://example.com"  # Base URL for relative links
SELECTOR = "a.content-link"  # CSS selector to find links
KEYWORDS = ["Anexo I", "Anexo II"]  # Keywords to search in link text
SUFFIX = ".pdf"  # Required file extension

# Test finding matching links in HTML content
def test_find_links_success(html_parser):
    # HTML content with various test links
    html_content = f"""
    <html><body>
        <h1>Title</h1>
        <p>Some text</p>
        <a class="content-link" href="http://example.com/files/anexo1.pdf">Link Text Anexo I</a>
        <a class="other-link" href="http://example.com/files/ignored.pdf">Ignored Link Anexo II</a>
        <a class="content-link" href="/files/relative_anexo2.pdf">Relative Link Anexo II PDF</a>
        <a class="content-link" href="http://example.com/files/anexo_word.doc">Link Text Anexo I DOC</a>
        <a class="content-link" href="http://another.com/files/anexo_external.pdf">External Anexo II</a>
        <p>More text</p>
        <a class="content-link" href="http://example.com/files/anexo_no_keyword.pdf">No Keyword PDF</a>
    </body></html>
    """
    
    # Expected links that should match all criteria
    expected_links = [
        "http://example.com/files/anexo1.pdf",
        "http://example.com/files/relative_anexo2.pdf",
        "http://another.com/files/anexo_external.pdf",
    ]

    # Convert relative URL to absolute URL for comparison
    import requests.compat
    expected_links[1] = requests.compat.urljoin(BASE_URL, "/files/relative_anexo2.pdf")

    # Find links using the parser
    found_links = html_parser.find_links(html_content, BASE_URL, SELECTOR, KEYWORDS, SUFFIX)

    # Verify correct links were found
    assert sorted(found_links) == sorted(expected_links)

# Test case where no links match all criteria
def test_find_links_no_matches(html_parser):
    html_content = """
    <html><body>
        <a class="content-link" href="file.doc">Anexo I Doc</a>  # Wrong extension
        <a class="other-link" href="anexo2.pdf">Anexo II PDF Wrong Class</a>  # Wrong class
        <a class="content-link" href="report.pdf">Report PDF No Keyword</a>  # No keyword
    </body></html>
    """
    found_links = html_parser.find_links(html_content, BASE_URL, SELECTOR, KEYWORDS, SUFFIX)
    assert found_links == []  # Should return empty list

# Test empty HTML content cases
def test_find_links_empty_html(html_parser):
    # Test with empty string
    found_links = html_parser.find_links("", BASE_URL, SELECTOR, KEYWORDS, SUFFIX)
    assert found_links == []
    
    # Test with empty HTML document
    found_links = html_parser.find_links("<html></html>", BASE_URL, SELECTOR, KEYWORDS, SUFFIX)
    assert found_links == []