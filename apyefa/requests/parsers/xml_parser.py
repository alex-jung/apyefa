from apyefa.requests.parsers.parser import Parser


class XmlParser(Parser):
    def parse(data: str) -> dict:
        raise NotImplementedError
