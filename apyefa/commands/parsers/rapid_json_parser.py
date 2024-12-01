import json

from apyefa.commands.parsers.parser import Parser


class RapidJsonParser(Parser):
    def parse(self, data: str) -> dict:
        if not data:
            return {}

        return json.loads(data)
