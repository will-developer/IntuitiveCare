import abc

class HtmlParser(abc.ABC):
    @abc.abstractmethod
    def find_links_ending_with(self, base_url: str, content: str, extension: str) -> list[str]:
        pass