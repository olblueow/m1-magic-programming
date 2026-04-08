import xml.etree.ElementTree as ET

class ProgramLoader:
    def __init__(self, cod_path):
        tree = ET.parse(cod_path)
        self.program_name = tree.findtext("deckname")
        self.instructions = [
            {
                "card": card.get("name"), 
                "annotation": card.get("annotation", "")
            }
            for card in tree.findall(".//zone[@name='main']/card")
        ]