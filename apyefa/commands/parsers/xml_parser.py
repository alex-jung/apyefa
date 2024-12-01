from apyefa.commands.parsers.parser import Parser


class XmlParser(Parser):
    def parse(self, data: str) -> dict:
        raise NotImplementedError
