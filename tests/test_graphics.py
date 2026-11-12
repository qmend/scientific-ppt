import zipfile
from pathlib import Path
import pytest
from PIL import Image
from scientific_ppt.equations import render_equation
from scientific_ppt.models import load_tokens,Box,LayoutError
from scientific_ppt.diagrams import node_boxes
from scientific_ppt.planner import plan
from scientific_ppt.pptx_writer import write_pptx

@pytest.mark.parametrize('latex',[r'\sum_{i=1}^{n}x_i^2',r'\int_0^1 x^2\,dx',r'A=\begin{bmatrix}1&2\\3&4\end{bmatrix}',r'f(x)=\begin{cases}x^2&x\ge0\\-x&x<0\end{cases}',r'x_{i}^{t+1}=\frac{a+b}{c}'])
def test_formulas(latex,tmp_path):
    result=render_equation(latex,tmp_path)
    assert Path(result['tex']).read_text()==latex
    assert '<path' in Path(result['svg']).read_text()
    with Image.open(result['png']) as im:
        assert im.width>40 and im.height>30 and im.getbbox()

def test_invalid_latex(tmp_path):
    with pytest.raises(ValueError):render_equation(r'\unknowncommand{x}',tmp_path)

def graph():
    return {'type':'diagram','nodes':[{'id':str(i),'label':'模块 '+str(i)} for i in range(6)],'edges':[{'from':str(i),'to':str(i+1)} for i in range(5)],'direction':'TB'}

def test_cycles():
    b=graph();b['edges'].append({'from':'5','to':'0'})
    with pytest.raises(LayoutError,match='cycle'):node_boxes(b,Box(0,0,600,500),load_tokens())
    b['edges'][-1]['feedback']=True
    assert len(node_boxes(b,Box(0,0,600,500),load_tokens()))==6

def test_editable_diagram_chart_formula(tmp_path):
    b=graph();b['direction']='LR';b['nodes']=b['nodes'][:4];b['edges']=b['edges'][:3]
    d={'version':'1.0','title':'Engineering','slides':[{'title':'Pipeline','blocks':[b]},{'title':'Results','blocks':[{'type':'chart','kind':'bar','categories':['A','B'],'series':[{'name':'Observed','values':[1,2]}]}]},{'title':'Model','blocks':[{'type':'equation','latex':r'\sum x_i'}]}]}
    t=load_tokens();pages=plan(d,t,tmp_path,tmp_path/'cache');out=tmp_path/'test.pptx';write_pptx(d,pages,t,out)
    with zipfile.ZipFile(out) as z:
        xml=z.read('ppt/slides/slide1.xml').decode()
        assert xml.count('<p:cxnSp>')==3
        assert 'node:0' in xml and 'tailEnd' in xml
        assert 'ppt/charts/chart1.xml' in z.namelist()
        assert any(n.endswith('.xlsx') for n in z.namelist())
        assert 'LaTeX:' in z.read('ppt/notesSlides/notesSlide3.xml').decode()
