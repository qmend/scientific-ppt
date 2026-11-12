"""Verify the delivered PPTX itself against the source, PDF, and rendered images."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import zipfile
from PIL import Image
from pptx import Presentation
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]

def verify():
    out=ROOT/'artifacts/demo'
    source=json.loads((ROOT/'tests/fixtures/demo/demo.json').read_text(encoding='utf-8'))
    report=json.loads((out/'qa_report.json').read_text(encoding='utf-8'))
    layout=json.loads((out/'resolved_layout.json').read_text(encoding='utf-8'))
    prs=Presentation(out/'presentation.pptx')
    images=sorted((out/'previews').glob('slide-*.png'))
    assert len(prs.slides)==len(PdfReader(out/'presentation.pdf').pages)==len(images)==report['slide_count']
    assert report['rendered_count']==len(images) and not report['issues']
    assert hashlib.sha256((out/'presentation.pptx').read_bytes()).hexdigest()==report['pptx_sha256']
    assert report['source_sha256']==hashlib.sha256(json.dumps(source,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    for im in images:
        with Image.open(im) as image:
            assert image.getpixel((10,10))[:3]==(165,0,33)
            assert abs(image.width/image.height-4/3)<.01
    blocks=[b for s in source['slides'] for b in s['blocks']]
    tables=[b for b in blocks if b['type']=='table']
    expected=[r['cells'] for t in tables for r in t['rows']]
    actual=[];table_pages=0;notes=[];connectors=0;charts=0
    for slide in prs.slides:
        notes.append(slide.notes_slide.notes_text_frame.text)
        for shape in slide.shapes:
            if shape.has_table:
                table_pages+=1
                assert [c.text for c in shape.table.rows[0].cells]==tables[0]['columns']
                actual.extend([[c.text for c in row.cells] for row in list(shape.table.rows)[1:]])
            if shape.has_chart:charts+=1
            if shape._element.tag.endswith('}cxnSp'):connectors+=1
    assert actual==expected
    assert connectors>0 and charts>0
    texts=[e['block']['text'] for p in layout for e in p['elements'] if e['block']['type']=='text']
    assert ''.join(texts)==''.join(b['text'] for b in blocks if b['type']=='text')
    # Check body chunks are really present in the PPTX, not only its sidecar.
    actual_text=Counter(s.text for p in prs.slides for s in p.shapes if s.has_text_frame)
    for text,count in Counter(texts).items():assert actual_text[text]>=count
    for b in blocks:
        if b['type']=='equation':assert any('LaTeX: '+b['latex'] in note for note in notes)
    with zipfile.ZipFile(out/'presentation.pptx') as z:
        assert any(n.startswith('ppt/embeddings/') for n in z.namelist())
    result={'status':'passed','pptx_sha256':report['pptx_sha256'],'slides':len(prs.slides),
            'pdf_pages':len(images),'png_previews':len(images),'table_rows_exact':len(actual),
            'repeated_header_pages':table_pages,'native_connectors':connectors,'native_charts':charts,
            'text_preserved':True,'latex_preserved':True,'header_color_verified':True}
    (out/'integrity_report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':verify()
