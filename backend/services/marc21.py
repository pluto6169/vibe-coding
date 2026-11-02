from models.schemas import ExtractedMetadata

def generate_marc21_json(metadata: ExtractedMetadata) -> dict:
    fields = {}
    
    fields["LDR"] = "00000nab a2200000 i 4500"
    fields["008"] = f"{metadata.date if metadata.date else '    '}                        eng d"
    
    if metadata.title:
        fields["245"] = {"ind1": "0", "ind2": "0", "subfields": {"a": metadata.title, "c": ", ".join(metadata.authors) if metadata.authors else ""}}
        
    if metadata.authors:
        fields["100"] = {"ind1": "1", "ind2": " ", "subfields": {"a": metadata.authors[0], "e": "author"}}
        if len(metadata.authors) > 1:
            fields["700"] = [{"ind1": "1", "ind2": " ", "subfields": {"a": author, "e": "author"}} for author in metadata.authors[1:]]
            
    fields["264"] = {"ind1": " ", "ind2": "1", "subfields": {"a": "[Place of publication not identified]", "b": metadata.publisher or "[Publisher not identified]", "c": metadata.date or "[date not identified]"}}
    
    fields["500"] = {"ind1": " ", "ind2": " ", "subfields": {"a": "DRAFT RECORD - Requires professional cataloger review for complete cataloging including classification, subject headings (LCSH), and authority control."}}
    
    if metadata.abstract:
        fields["520"] = {"ind1": "3", "ind2": " ", "subfields": {"a": metadata.abstract}}
        
    fields["546"] = {"ind1": " ", "ind2": " ", "subfields": {"a": "Text in English."}}
    
    if metadata.keywords:
        fields["653"] = [{"ind1": " ", "ind2": " ", "subfields": {"a": kw}} for kw in metadata.keywords]
        
    return fields

def generate_marc21_mrk(metadata: ExtractedMetadata) -> str:
    json_data = generate_marc21_json(metadata)
    lines = []
    
    for tag, value in json_data.items():
        if tag in ["LDR", "008", "001", "003", "005"]:
            lines.append(f"={tag}  {value}")
        elif isinstance(value, dict):
            i1 = value.get('ind1', ' ').replace(' ', '\\')
            i2 = value.get('ind2', ' ').replace(' ', '\\')
            subf = "".join([f"${k}{v}" for k, v in value.get('subfields', {}).items() if v])
            lines.append(f"={tag}  {i1}{i2}{subf}")
        elif isinstance(value, list):
            for item in value:
                i1 = item.get('ind1', ' ').replace(' ', '\\')
                i2 = item.get('ind2', ' ').replace(' ', '\\')
                subf = "".join([f"${k}{v}" for k, v in item.get('subfields', {}).items() if v])
                lines.append(f"={tag}  {i1}{i2}{subf}")
                
    return "\n".join(lines)
