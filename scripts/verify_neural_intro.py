"""Verify the rendered lecture and data conservation in the exported PPTX."""
import json
from pathlib import Path
import numpy as np
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt
import pypdfium2 as pdfium

out=Path(__file__).resolve().parents[1]/'artifacts/neural-network-intro'
deck=json.loads((out/'deck.json').read_text(encoding='utf-8'))
qa=json.loads((out/'qa_report.json').read_text(encoding='utf-8'))
prs=Presentation(out/'presentation.pptx')
assert 20<=len(prs.slides)<=30
assert qa['rendered_count']==len(prs.slides)==26
assert qa['issues']==[],qa['issues']
assert len(list((out/'previews').glob('slide-*.png')))==26
with pdfium.PdfDocument(out/'presentation.pdf') as pdf:assert len(pdf)==26
for page_index in (0,25):
    header=next(s for s in prs.slides[page_index].shapes if s.has_text_frame and s.text==deck['english_title'])
    assert header.text_frame.paragraphs[0].alignment==PP_ALIGN.CENTER
    rule=next(s for s in prs.slides[page_index].shapes if s.name=='English header rule')
    assert rule.top==Pt(47)
for index,slide in enumerate(prs.slides,1):
    numbers=[s for s in slide.shapes if s.has_text_frame and s.text==str(index)]
    if index in (1,len(prs.slides)):
        assert not numbers
    else:
        assert len(numbers)==1
        assert numbers[0].text_frame.paragraphs[0].runs[0].font.size==Pt(18)
        assert numbers[0].text_frame.paragraphs[0].alignment==PP_ALIGN.RIGHT
cover=next(s for s in prs.slides[0].shapes if s.has_table)
assert 2*cover.left+cover.width==prs.slide_width and cover.width==Pt(228)
for row in cover.table.rows:
    assert row.cells[1].text_frame.paragraphs[0].alignment==PP_ALIGN.LEFT
    for cell in row.cells:
        props=cell._tc.get_or_add_tcPr()
        assert props.xpath('./a:noFill')
        assert all(props.xpath(f'./a:{edge}/a:noFill') for edge in ('lnL','lnR','lnT','lnB'))
agenda=[s for s in prs.slides[1].shapes if s.has_text_frame and s.text[:2].isdigit() and len(s.text)>2]
assert len(agenda)==5 and len({s.left for s in agenda})==1
assert all(a.top+a.height<b.top for a,b in zip(agenda,agenda[1:]))
long_tables=[]
for source_index,source in enumerate(deck['slides']):
    tables=[b for b in source['blocks'] if b['type']=='table' and len(b['rows'])>10]
    if not tables:continue
    original=tables[0]
    pages=[m for m in qa['manifest'] if m['source_slide']==source_index]
    assert len(pages)==2
    actual=[]
    for part,m in enumerate(pages):
        slide=prs.slides[m['page']-1]
        table_shape=next(s for s in slide.shapes if s.has_table)
        table=table_shape.table
        bottom=table_shape.top+table_shape.height
        if part==len(pages)-1:
            assert bottom<prs.slide_height-Pt(30)
        else:
            assert abs(bottom-(prs.slide_height-Pt(30)))<Pt(.01)
        assert [c.text for c in table.rows[0].cells]==original['columns']
        actual.extend([[c.text for c in r.cells] for r in list(table.rows)[1:]])
        assert len(m['elements'])==1 # dedicated table page, no body text below
        strings=[s.text for s in slide.shapes if s.has_text_frame]
        assert not any('续 /' in value for value in strings)
        if part:assert original['caption'] not in strings
    assert actual==[r['cells'] for r in original['rows']]
    long_tables.append(dict(title=source['title'],pages=[m['page'] for m in pages],rows=len(actual)))
assert len(long_tables)==2
result=json.loads((out/'xor_results.json').read_text(encoding='utf-8'))
weights=np.load(out/'xor_weights.npz')
X=np.array(result['inputs']);y=np.array(result['targets'])
h=np.tanh(X@weights['W1']+weights['b1'])
logits=(h@weights['W2']+weights['b2'])[:,0]
probs=1/(1+np.exp(-logits))
assert np.allclose(probs,result['probabilities'],rtol=0,atol=1e-14)
assert np.array_equal(probs>=.5,y.astype(bool))
assert sum(weights[k].size for k in weights)==33
loss=float(np.mean(np.logaddexp(0,logits)-y*logits))
assert abs(loss-result['history'][-1]['loss'])<1e-14
charts=sum(s.has_chart for p in prs.slides for s in p.shapes)
nodes=sum(s.name.startswith('node:') for p in prs.slides for s in p.shapes)
assert charts==3 and nodes==47
flowchart_boxes=[
    s for page in prs.slides for s in page.shapes
    if s.name.startswith('node:') and s.auto_shape_type==MSO_SHAPE.RECTANGLE
]
assert len(flowchart_boxes)==31
assert all(str(box.fill.fore_color.rgb)=='FFFFFF' for box in flowchart_boxes)
summary=dict(pages=len(prs.slides),rendered=qa['rendered_count'],issues=qa['issues'],
             long_tables=long_tables,native_charts=charts,native_diagram_nodes=nodes,
             xor_loss=loss,pptx_sha256=qa['pptx_sha256'])
(out/'verification.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True,indent=2))
