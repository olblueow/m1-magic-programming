import xml.etree.ElementTree as ET
from xml.dom import minidom

class XMLGenerator:
    """Generates a valid Cockatrice .cod XML file from a translated decklist."""
    
    @staticmethod
    def build_cod_file(decklist: list, output_path: str, deckname: str = "Compiled Program"):
        root = ET.Element("cockatrice_deck", version="1")
        name = ET.SubElement(root, "deckname")
        name.text = deckname
        
        zone = ET.SubElement(root, "zone", name="main")
        
        # Add all cards to the XML tree
        for inst in decklist:
            ET.SubElement(zone, "card", name=inst["card"], annotation=inst["annotation"])
        
        # Convert to a formatted (pretty) string
        raw_xml = ET.tostring(root, 'utf-8')
        reparsed = minidom.parseString(raw_xml)
        pretty_xml = reparsed.toprettyxml(indent="    ")
        
        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
            
        print(f"✅ Compilation successful! Saved to: {output_path}")