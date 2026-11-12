from pptx import Presentation
from pytest import approx
from scientific_ppt.models import load_tokens
from scientific_ppt.planner import plan
from scientific_ppt.pptx_writer import write_pptx
from scientific_ppt.tables import paginate_table


def test_continued_table_fills_nonfinal_pages_and_preserves_topic_boundary():
    rows = [{'id': str(i), 'cells': [str(i), 'value']} for i in range(23)]
    pages = paginate_table({'columns': ['ID', 'Value'], 'rows': rows}, 672, 400, load_tokens())
    assert len(pages) >= 3
    assert [row for page in pages for row in page['rows']] == rows
    assert [sum(page['row_heights']) for page in pages[:-1]] == approx([400]*(len(pages)-1))
    natural_row_height = paginate_table(
        {'columns':['ID','Value'],'rows':rows[-1:]},672,400,load_tokens()
    )[0]['row_heights'][1]
    assert pages[-1]['row_heights'][1:] == approx([natural_row_height]*len(pages[-1]['rows']))
    assert sum(pages[-1]['row_heights']) < 400
    deck = {'version': '1.0', 'title': 'Table', 'slides': [
        {'title': 'Table', 'blocks': [{'type': 'table', 'caption':'Table 1', 'columns': ['ID', 'Value'], 'rows': rows}]},
        {'title': 'Next topic', 'blocks': [{'type':'text','text':'A separate topic.'}]}]}
    from tempfile import TemporaryDirectory
    from pathlib import Path
    with TemporaryDirectory() as temp:
        planned = plan(deck, load_tokens(), temp, Path(temp)/'assets')
        assert len(planned) > 1
        assert [r for page in planned for element in page.elements if element.block['type']=='table' for r in element.block['rows']] == rows
        assert planned[-1].title=='Next topic' and len(planned[-1].elements)==1
        assert all('caption' not in p.elements[0].block for p in planned[1:-1])
        output=Path(temp)/'table.pptx'
        tokens = load_tokens()
        write_pptx(deck,planned,tokens,output)
        slides = Presentation(output).slides
        assert all('续 /' not in s.text for p in slides for s in p.shapes if s.has_text_frame)
        tables = [next(s for s in p.shapes if s.has_table) for p in list(slides)[:-1]]
        bottom = tokens['canvas']['height']-tokens['spacing']['footer']
        assert [(table.top+table.height)/12700 for table in tables[:-1]] == approx([bottom]*(len(tables)-1),abs=.01)
        assert (tables[-1].top+tables[-1].height)/12700 < bottom


def test_editorial_styles_remain_editable(tmp_path):
    deck={'version':'1.0','title':'Styles','english_title':'TRANSFORMER','slides':[
        {'title':'Cover','layout':'cover','blocks':[
            {'type':'text','text':'==Blue== and __underlined__\nSecond paragraph','first_line_indent':2,'paragraph_space':12,
             'panel':'gradient','gradient':{'colors':['FFFFFF','DDF0DE'],'kind':'radial','focus':[.2,.3]},'box':[24,90,672,120]},
            {'type':'table','columns':['Field','Value'],'rows':[{'id':'name','cells':['Presenter','xxx']}],
             'hide_header':True,'style':'bands','box':[180,300,360,90]},
            {'type':'text','text':'First\nSecond','bullet':{'symbol':'□','color':'A50021'},'box':[24,430,400,70]}]}]}
    tokens=load_tokens();pages=plan(deck,tokens,tmp_path,tmp_path/'assets')
    output=tmp_path/'styles.pptx';write_pptx(deck,pages,tokens,output)
    slide=Presentation(output).slides[0]
    panel=next(s for s in slide.shapes if s.has_text_frame and 'Blue' in s.text)
    assert 'path="circle"' in panel._element.xml and 'indent="609600"' in panel._element.xml
    runs=list(panel.text_frame.paragraphs[0].runs)
    assert str(runs[1].font.color.rgb)==tokens['colors']['blue']
    assert any(r.text=='underlined' and r.font.underline for r in runs)
    tab=next(s.table for s in slide.shapes if s.has_table)
    assert len(tab.rows)==1
    ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
    assert tab.cell(0,0)._tc.find('a:tcPr/a:noFill',ns) is not None
    assert tab.cell(0,0)._tc.find('a:tcPr/a:lnR/a:noFill',ns) is not None
    assert any('buChar char="□"' in s._element.xml for s in slide.shapes)


def test_composed_text_formula_and_panel(tmp_path):
    deck = {'version': '1.0', 'title': 'Composition', 'slides': [{
        'title': 'Composition', 'layout': 'composed', 'blocks': [
            {'type': 'text', 'text': 'An **important** result', 'panel': 'gradient', 'box': [24, 80, 672, 90]},
            {'type': 'equation', 'latex': 'x^2', 'box': [24, 200, 672, 120], 'caption': '(1)'}
        ]}]}
    tokens = load_tokens()
    pages = plan(deck, tokens, tmp_path, tmp_path/'assets')
    assert len(pages) == 1 and len(pages[0].elements) == 2
    output = tmp_path/'composition.pptx'
    write_pptx(deck, pages, tokens, output)
    slide = Presentation(output).slides[0]
    panel = next(s for s in slide.shapes if s.has_text_frame and 'important' in s.text)
    assert '**' not in panel.text
    assert any(r.text == 'important' and r.font.bold for p in panel.text_frame.paragraphs for r in p.runs)
    assert 'gradFill' in panel._element.xml
    assert 'LaTeX: x^2' in slide.notes_slide.notes_text_frame.text
