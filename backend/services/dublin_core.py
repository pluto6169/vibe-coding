from lxml import etree
from models.schemas import ExtractedMetadata, DublinCoreRecord

def generate_dublin_core_json(metadata: ExtractedMetadata, file_info: dict) -> dict:
    return {
        "title": metadata.title,
        "creator": metadata.authors,
        "subject": metadata.keywords,
        "description": metadata.abstract,
        "publisher": metadata.publisher or metadata.journal,
        "contributor": [],
        "date": metadata.date,
        "type": metadata.document_type or 'Text',
        "format": file_info.get("format", ""),
        "identifier": metadata.doi,
        "source": metadata.journal,
        "language": metadata.language or 'en',
        "relation": [],
        "coverage": None,
        "rights": "All rights reserved"
    }

def generate_dublin_core_xml(metadata: ExtractedMetadata, file_info: dict) -> str:
    dc_data = generate_dublin_core_json(metadata, file_info)
    
    NSMAP = {
        "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
    }
    
    root = etree.Element("{http://www.openarchives.org/OAI/2.0/oai_dc/}dc", nsmap=NSMAP)
    root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", 
             "http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd")
             
    def add_element(name, value):
        if value:
            if isinstance(value, list):
                for v in value:
                    elem = etree.SubElement(root, f"{{http://purl.org/dc/elements/1.1/}}{name}")
                    elem.text = str(v)
            else:
                elem = etree.SubElement(root, f"{{http://purl.org/dc/elements/1.1/}}{name}")
                elem.text = str(value)

    for key, value in dc_data.items():
        add_element(key, value)
        
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")
