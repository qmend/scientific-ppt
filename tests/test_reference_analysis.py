import json
from scientific_ppt.reference_analysis import analyze_reference
from scientific_ppt.models import load_tokens
from scientific_ppt.planner import plan
from scientific_ppt.pptx_writer import write_pptx


def test_new_reference_structure_without_fake_preview(tmp_path):
    d={'version':'1.0','title':'Reference','slides':[{'title':'Study','blocks':[{'type':'text','text':'Editable evidence'}]}]}
    t=load_tokens();pages=plan(d,t,tmp_path,tmp_path/'cache');path=tmp_path/'ref.pptx'
    write_pptx(d,pages,t,path)
    results=analyze_reference(path,tmp_path/'analysis',do_render=False)
    assert results[0]['slides']==1 and results[0]['size_pt']==[720,540]
    assert results[0]['render_status']=='unavailable' and results[0]['rendered_count']==0
    assert ('A50021',1) in results[0]['xml_colors'] or any(c=='A50021' for c,n in results[0]['xml_colors'])
    tokens=json.loads((tmp_path/'analysis/token_candidates.json').read_text())
    assert tokens['provenance'].startswith('PROVISIONAL')
