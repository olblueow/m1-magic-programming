import xml.etree.ElementTree as ET

class DeckLoader:
    """Its sole purpose is to read the XML file and extract the instructions."""
    
    def __init__(self, cod_path: str):
        tree = ET.parse(cod_path)
        self.program_name = tree.findtext("deckname") or "Unknown"
        
        self.instructions = [
            {
                "card": card.get("name"), 
                "annotation": card.get("annotation", "")
            }
            for card in tree.findall(".//zone[@name='main']/card")
        ]