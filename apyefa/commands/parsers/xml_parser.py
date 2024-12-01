from apyefa.commands.parsers.parser import Parser


class XmlParser(Parser):
    def parse(data: str) -> dict:
        raise NotImplementedError
