import json
from PIL import Image
import pytest
from scientific_ppt.pipeline import build
from scientific_ppt.rendering import render_pptx
from scientific_ppt.quality import inspect
from scientific_ppt.models import load_tokens
from scientific_ppt.ingest import markdown_plan

def deck():return {'version':'1.0','title':'test','slides':[{'title':'Test','blocks':[{'type':'text','text':'Measurable scientific evidence.'}]}]}

def test_missing_renderer(monkeypatch,tmp_path):
    monkeypatch.setattr('scientific_ppt.rendering.detect_backends',lambda:{'powerpoint':False,'libreoffice':None})
    r=build(deck(),tmp_path)
    assert r['status']=='unverified' and r['rendered_count']==0
    assert (tmp_path/'presentation.pptx').is_file()
    assert 'render_unavailable' in [i['code'] for i in r['issues']]

def test_repair_is_bounded(tmp_path):
    def renderer(source,out,backend):
        out.mkdir(parents=True);path=out/'1.png';im=Image.new('RGB',(100,75),'white');im.putpixel((1,1),(0,0,0));im.save(path)
        return {'status':'rendered','backend':'test-double','images':[str(path)],'metrics':[{'page':1,'shape':1,'name':'bad','bound_height':100,'available_height':1,'bound_width':20,'available_width':40}],'errors':[]}
    report=build(deck(),tmp_path,max_repairs=2,renderer=renderer)
    assert report['attempts']==3 and report['status']=='needs_review'
    assert [h['measurement_safety'] for h in report['history']]==sorted(h['measurement_safety'] for h in report['history'])

def test_overlap_detection():
    elems=[{'id':str(i),'type':'text','box':[20,100,500,40],'text':'same','font_size':20} for i in range(2)]
    issues=inspect([{'page':1,'elements':elems}],load_tokens())
    assert 'overlap' in [i['code'] for i in issues]

def test_markdown_intake(tmp_path):
    p=tmp_path/'input.md';p.write_text('# Materials\n\n## Design\n\nKeep provenance.\n\n## Results\n\nDo not invent data.',encoding='utf8')
    d=markdown_plan(p)
    assert d['title']=='Materials' and len(d['slides'])==2
    assert d['slides'][1]['blocks'][0]['text']=='Do not invent data.'

def test_rebuild_cleans_owned_previews_only(tmp_path):
    previews=tmp_path/'previews';previews.mkdir()
    old=previews/'slide-002.png';old.write_bytes(b'old generated preview')
    user=previews/'my-note.png';user.write_bytes(b'keep')
    outside=tmp_path/'slide-999.png';outside.write_bytes(b'keep')
    (previews/'index.json').write_text(json.dumps([str(old),str(outside)]))
    (tmp_path/'qa_report.json').write_text('{}')
    (tmp_path/'presentation.pdf').write_bytes(b'old PDF')
    (tmp_path/'contact-sheet.jpg').write_bytes(b'old contact sheet')
    report=build(deck(),tmp_path,do_render=False)
    assert report['status']=='unverified'
    assert not old.exists() and user.exists() and outside.exists()
    assert not (tmp_path/'presentation.pdf').exists()
    assert not (tmp_path/'contact-sheet.jpg').exists()
    assert json.loads((previews/'index.json').read_text())==[]
