import pytest
from src.adapters.html_parser import BeautifulSoupHtmlParser

@pytest.fixture
def html_parser():
    return BeautifulSoupHtmlParser()

BASE_URL = "http://example.com"
SELECTOR = "a.content-link"
KEYWORDS = ["Anexo I", "Anexo II"]
SUFFIX = ".pdf"

def test_find_links_success(html_parser):
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
    expected_links = [
        "http://example.com/files/anexo1.pdf",
        "http://example.com/files/relative_anexo2.pdf",
        "http://another.com/files/anexo_external.pdf",
    ]

    import requests.compat
    expected_links[1] = requests.compat.urljoin(BASE_URL, "/files/relative_anexo2.pdf")


    found_links = html_parser.find_links(html_content, BASE_URL, SELECTOR, KEYWORDS, SUFFIX)

    assert sorted(found_links) == sorted(expected_links)

def test_find_links_no_matches(html_parser):
    html_content = """
    <html><body>
        <a class="content-link" href="file.doc">Anexo I Doc</a>
        <a class="other-link" href="anexo2.pdf">Anexo II PDF Wrong Class</a>
        <a class="content-link" href="report.pdf">Report PDF No Keyword</a>
    </body></html>
    """
    found_links = html_parser.find_links(html_content, BASE_URL, SELECTOR, KEYWORDS, SUFFIX)
    assert found_links == []

def test_find_links_empty_html(html_parser):
    found_links = html_parser.find_links("", BASE_URL, SELECTOR, KEYWORDS, SUFFIX)
    assert found_links == []
    found_links = html_parser.find_links("<html></html>", BASE_URL, SELECTOR, KEYWORDS, SUFFIX)
    assert found_links == []