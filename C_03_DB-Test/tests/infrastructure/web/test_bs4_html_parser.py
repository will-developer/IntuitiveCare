import pytest
from src.infrastructure.web import Bs4HtmlParser

@pytest.fixture
def parser():
    """Provides an instance of Bs4HtmlParser."""
    return Bs4HtmlParser()

@pytest.mark.parametrize("html_content, base_url, extension, expected_links", [
    # Simple case
    ('<html><body><a href="file1.zip">Link 1</a></body></html>',
     'http://example.com', '.zip', ['http://example.com/file1.zip']),
    # Multiple links, different extensions
    ('<html><a href="doc.pdf">PDF</a> <a href="/data/archive.zip">ZIP</a> <a href="image.JPG">JPG</a></html>',
     'http://test.com/page/', '.zip', ['http://test.com/data/archive.zip']),
    # Absolute link in HTML
    ('<html><a href="http://othersite.com/file.zip">Absolute</a> <a href="relative.zip">Relative</a></html>',
     'http://example.com', '.zip', ['http://othersite.com/file.zip', 'http://example.com/relative.zip']),
    # Case-insensitive extension matching (provide extension without dot)
    ('<html><a href="data.ZIP">Upper</a> <a href="data.Zip">Mixed</a></html>',
     'http://example.com', 'zip', ['http://example.com/data.ZIP', 'http://example.com/data.Zip']),
    # No matching links
    ('<html><a href="file.txt">Text</a> <a href="image.png">PNG</a></html>',
     'http://example.com', '.zip', []),
    # Empty HTML
    ('', 'http://example.com', '.zip', []),
     # Extension check should be precise
    ('<html><a href="archive.zip.bak">Backup</a> <a href="real.zip">Real</a></html>',
     'http://example.com', '.zip', ['http://example.com/real.zip']),
     # Base URL with trailing slash vs without
     ('<html><a href="file.zip">Link</a></html>', 'http://example.com/data/', '.zip', ['http://example.com/data/file.zip']),
     ('<html><a href="file.zip">Link</a></html>', 'http://example.com/data', '.zip', ['http://example.com/file.zip']), # urljoin behavior
     # Links starting with slash
     ('<html><a href="/files/doc.zip">Link</a></html>', 'http://example.com/data/', '.zip', ['http://example.com/files/doc.zip']),
])
def test_find_links_ending_with(parser, html_content, base_url, extension, expected_links):
    """Tests finding links with various scenarios."""
    # Ensure extension format consistency if needed (e.g., always start with '.')
    if not extension.startswith('.'):
        normalized_extension = '.' + extension
    else:
        normalized_extension = extension

    result = parser.find_links_ending_with(base_url, html_content, normalized_extension)
    # Use sets for comparison as order doesn't matter
    assert set(result) == set(expected_links)

def test_find_links_invalid_html(parser):
    """Tests behavior with potentially invalid HTML (should be robust)."""
    # Arrange
    invalid_html = '<html><body><a href="good.zip">Good</a href="bad.zip"></a><<>>'
    base_url = 'http://example.com'
    extension = '.zip'
    expected = ['http://example.com/good.zip'] # bs4 is often lenient

    # Act
    result = parser.find_links_ending_with(base_url, invalid_html, extension)

    # Assert
    assert set(result) == set(expected)