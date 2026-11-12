import copy
from pathlib import Path
import pytest
from PIL import Image
from pptx import Presentation
from scientific_ppt.models import load_tokens,validate_deck,Box,LayoutError
from scientific_ppt.images import fit_image
from scientific_ppt.planner import plan
from scientific_ppt.pptx_writer import write_pptx
from scientific_ppt.tables import paginate_table
from scientific_ppt.typography import wrap
from scientific_ppt.typography import split_text

def deck(blocks):return {'version':'1.0','title':'测试','slides':[{'title':'研究设计','blocks':blocks}]}

def test_lossless_wrapping():
    t=load_tokens();text='变量 x_123  与  English words\n第二行：很长的词abcdefghijklmnop'
    assert ''.join(wrap(text,65,24,t['fonts']['body']))==text

def test_no_orphan_continuation():
    t=load_tokens();text='研究观测数据。'*180
    chunks=split_text(text,672,430,24,t,1.32)
    counts=[len(wrap(c,664,24,t['fonts']['body'])) for c in chunks]
    assert max(counts)-min(counts)<=3
    assert ''.join(chunks)==text

def test_text_overflow_splits(tmp_path):
    t=load_tokens();text='保留所有实验记录，避免遗漏数据。'*180
    d=deck([{'type':'text','text':text}]);before=copy.deepcopy(d)
    pages=plan(d,t,tmp_path,tmp_path/'cache')
    assert len(pages)>3
    assert ''.join(e.block['text'] for p in pages for e in p.elements)==text
    assert d==before
    write_pptx(d,pages,t,tmp_path/'text.pptx')
    assert len(Presentation(tmp_path/'text.pptx').slides)==len(pages)

def test_mixed_images(tmp_path):
    blocks=[{'type':'text','text':'同一研究的不同观测视角。'}]
    for i,size in enumerate([(900,450),(250,800),(600,500)]):
        path=tmp_path/f'{i}.png';Image.new('RGB',size,'navy').save(path)
        blocks.append({'type':'image','path':str(path),'caption':f'视角{i}'})
    d=deck(blocks);t=load_tokens();pages=plan(d,t,tmp_path,tmp_path/'cache')
    manifest,_=write_pptx(d,pages,t,tmp_path/'mixed.pptx')
    assert sum(len(p.elements) for p in pages)==4
    for p in manifest:
        for e in p['elements']:
            if e['type']=='image':
                assert e['actual_box'][2]/e['actual_box'][3]==pytest.approx(e['source_size'][0]/e['source_size'][1])

@pytest.mark.parametrize('size',[(10000,20),(20,10000),(800,600)])
def test_image_no_distortion(size):
    box,mode,warning=fit_image(size,Box(0,0,500,300),'cover',False)
    assert mode=='contain' and warning
    assert box.w/box.h==pytest.approx(size[0]/size[1])

def test_table_data_and_groups():
    t=load_tokens();b={'type':'table','columns':['ID','Value'],'rows':[{'id':str(i),'cells':[str(i),'值'+str(i)],'group':str(i//3)} for i in range(75)]}
    parts=paginate_table(b,672,420,t,1.12)
    assert len(parts)>5
    assert [r for p in parts for r in p['rows']]==b['rows']
    assert all(len(p['rows'])%3==0 for p in parts)

def test_oversized_row_fails():
    with pytest.raises(LayoutError,match='taller'):
        paginate_table({'columns':['X'],'rows':[{'id':'bad','cells':['超长'*1000]}]},500,400,load_tokens())

def test_schema_rejects_data_mismatch():
    with pytest.raises(ValueError,match='exactly'):
        validate_deck(deck([{'type':'table','columns':['A','B'],'rows':[{'id':'1','cells':['x']}]}]))
