"""Deterministic text intake, never substitutes for an Agent reading source evidence."""
import json
import re
import zipfile
from pathlib import Path
from lxml import etree


def extract(path):
    path=Path(path);suffix=path.suffix.lower()
    if suffix in ('.md','.txt'):return path.read_text(encoding='utf-8-sig')
    if suffix=='.pdf':
        from pypdf import PdfReader
        chunks=[f'\n[Source page {i}]\n'+(p.extract_text() or '') for i,p in enumerate(PdfReader(path).pages,1)]
        if not any(len(c.split(']\n',1)[-1].strip())>20 for c in chunks):
            raise ValueError('PDF has no usable text layer; OCR/visual reading is required')
        return '\n'.join(chunks)
    if suffix=='.docx':
        with zipfile.ZipFile(path) as z:root=etree.fromstring(z.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        return '\n'.join(''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in root.xpath('//w:p',namespaces=ns))
    raise ValueError('Supported source text formats: .md, .txt, .pdf, .docx. Agent supplies structured deck JSON for other inputs.')


def markdown_plan(path):
    """Headings become sections, paragraphs stay intact. No invented topic expansion."""
    path=Path(path);text=extract(path);title=path.stem;slides=[];current=None
    for para in re.split(r'\n\s*\n',text):
        if not para.strip():continue
        lines=para.splitlines()
        for line in lines:
            if re.match(r'^#{1,3}\s+',line):
                heading=re.sub(r'^#{1,3}\s+','',line).strip()
                if line.startswith('# '):title=heading
                current={'title':heading,'blocks':[],'notes':f'Source: {path.name}'};slides.append(current)
            else:
                if current is None:
                    current={'title':title,'blocks':[],'notes':f'Source: {path.name}'};slides.append(current)
                value=re.sub(r'^[-*]\s+','',line)
                if value.strip():current['blocks'].append({'type':'text','text':value,'source':path.name})
    slides=[s for s in slides if s['blocks']]
    if not slides:raise ValueError('Source has no non-heading content')
    return {'version':'1.0','title':title,'slides':slides}
