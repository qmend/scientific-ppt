"""Editable PowerPoint primitives; all coordinates are points."""
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR,PP_ALIGN,MSO_AUTO_SIZE
from pptx.oxml.xmlchemy import OxmlElement
from .models import Box
from .tables import TABLE_CAPTION_HEIGHT
from .layout import content_box
from .typography import resolve_font
from .images import fit_image


def color(hex_color):return RGBColor.from_string(hex_color)


def rectangle(slide,box,fill,line=None,kind=MSO_SHAPE.RECTANGLE):
    s=slide.shapes.add_shape(kind,*[Pt(v) for v in box.as_list()])
    s.fill.solid();s.fill.fore_color.rgb=color(fill)
    # Suppress theme-inherited shadows (Office default shape style has an effect ref).
    s._element.spPr.append(OxmlElement('a:effectLst'))
    if line:s.line.color.rgb=color(line);s.line.width=Pt(.8)
    else:s.line.fill.background()
    return s


def set_text(shape,text,size,tokens,fill=None,bold=False,align=PP_ALIGN.LEFT,padding=None,family=None,first_line_indent=0,paragraph_space=0,bullet=None):
    tf=shape.text_frame;tf.clear();tf.word_wrap=True;tf.auto_size=MSO_AUTO_SIZE.NONE
    pad=tokens['spacing']['text_padding'] if padding is None else padding
    tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=Pt(pad)
    tf.vertical_anchor=MSO_ANCHOR.TOP
    family=resolve_font(family or tokens['fonts']['body'])[1]
    latin=resolve_font(tokens['fonts']['latin'])[1]
    for i,line in enumerate(text.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        paragraph_props=p._p.get_or_add_pPr()
        paragraph_props.set('eaLnBrk','1');paragraph_props.set('latinLnBrk','0');paragraph_props.set('hangingPunct','0')
        p.alignment=align;p.line_spacing=tokens['spacing']['line_height'];p.space_before=Pt(0);p.space_after=Pt(paragraph_space)
        if first_line_indent:paragraph_props.set('indent',str(int(Pt(size*first_line_indent))))
        if bullet and line.strip():
            line=line.lstrip('•●○■□ ').strip()
            paragraph_props.set('marL',str(int(Pt(size*1.2))))
            paragraph_props.set('indent',str(-int(Pt(size*.95))))
            bc=OxmlElement('a:buClr');rgb=OxmlElement('a:srgbClr');rgb.set('val',bullet.get('color',tokens['colors']['text']));bc.append(rgb);paragraph_props.append(bc)
            bf=OxmlElement('a:buFont');bf.set('typeface','Arial');paragraph_props.append(bf)
            char=OxmlElement('a:buChar');char.set('char',bullet['symbol']);paragraph_props.append(char)
        import re
        for part in re.split(r'(\*\*.*?\*\*|==.*?==|__.*?__)', line):
            strong = part.startswith('**') and part.endswith('**')
            blue=part.startswith('==') and part.endswith('==')
            underline=part.startswith('__') and part.endswith('__')
            r=p.add_run();r.text=part[2:-2] if strong or blue or underline else part
            r.font.size=Pt(size);r.font.name=latin;r.font.bold=bold or strong
            r.font.underline=underline
            r.font.color.rgb=color(tokens['colors']['blue'] if blue else (fill or tokens['colors']['text']))
            props=r._r.get_or_add_rPr()
            props.set('lang','zh-CN' if any('\u3400'<=c<='\u9fff' for c in part) else 'en-US')
            ea=OxmlElement('a:ea');ea.set('typeface',family);props.append(ea)
    return shape


def text_box(slide,text,box,size,tokens,**kwargs):
    shape=slide.shapes.add_textbox(*[Pt(v) for v in box.as_list()])
    return set_text(shape,text,size,tokens,**kwargs)


def write_pptx(deck,pages,tokens,output):
    prs=Presentation();prs.slide_width=Pt(tokens['canvas']['width']);prs.slide_height=Pt(tokens['canvas']['height'])
    prs.core_properties.title=deck['title'];prs.core_properties.author=deck.get('author','')
    warnings=[];manifest=[]
    w,h=tokens['canvas']['width'],tokens['canvas']['height'];colors=tokens['colors']
    for index,page in enumerate(pages,1):
        slide=prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid();slide.background.fill.fore_color.rgb=color(colors['background'])
        _,header=content_box(page.title,tokens)
        if page.layout not in ('cover','end'):
            rectangle(slide,Box(0,0,w,header),colors['primary'])
            text_box(slide,page.title,Box(24,8,w-48,header-12),tokens['type']['title'],tokens,fill=colors['white'],padding=0,family=tokens['fonts']['heading'])
        else:
            text_box(slide,deck.get('english_title','SCIENTIFIC PRESENTATION'),Box(36,25,w-72,24),16,tokens,fill=colors['primary'],padding=0,align=PP_ALIGN.CENTER)
            rectangle(slide,Box(36,47,w-72,1.5),colors['primary']).name='English header rule'
        if 1<index<len(pages) and page.layout not in ('cover','end'):
            text_box(slide,str(index),Box(w-64,h-30,40,28),tokens['type']['footer'],tokens,fill=colors['primary'],align=PP_ALIGN.RIGHT,padding=0)
        if page.continuation>1 and page.layout!='table':
            text_box(slide,f'续 / {page.continuation}',Box(24,h-30,100,28),tokens['type']['footer'],tokens,fill=colors['muted'],padding=0)
        notes=[page.notes];items=[]
        for el in page.elements:
            b,box=el.block,el.box;kind=b['type']
            item={'id':b['id'],'type':kind,'box':box.as_list()}
            if b.get('source'):notes.append('Source: '+b['source'])
            if kind=='text':
                size=b.get('font_size',tokens['type']['body'])
                shape=slide.shapes.add_textbox(*[Pt(v) for v in box.as_list()])
                if b.get('panel'):
                    shape.fill.solid();shape.fill.fore_color.rgb=color(colors['white'])
                    shape.line.color.rgb=color(colors['text']);shape.line.width=Pt(1)
                    if b['panel']=='gradient':
                        spec=b.get('gradient',{})
                        shades=spec.get('colors',[colors['white'],colors['cyan']])
                        shape.fill.gradient()
                        shape.fill.gradient_stops[0].color.rgb=color(shades[0])
                        shape.fill.gradient_stops[1].color.rgb=color(shades[1])
                        shape.fill.gradient_angle=spec.get('angle',0)
                        if spec.get('kind')=='radial':
                            grad=shape._element.spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}gradFill')
                            for old in list(grad):
                                if old.tag.endswith('}lin') or old.tag.endswith('}path'):grad.remove(old)
                            path=OxmlElement('a:path');path.set('path','circle')
                            x,y=spec.get('focus',[.5,.5]);rect=OxmlElement('a:fillToRect')
                            for key,value in [('l',x),('t',y),('r',1-x),('b',1-y)]:rect.set(key,str(round(value*100000)))
                            path.append(rect);grad.append(path)
                set_text(shape,b['text'],size,tokens,fill=colors.get(b.get('emphasis'),colors['text']),bold=b.get('heading',False),family=tokens['fonts']['heading'] if b.get('heading') else None,align=PP_ALIGN.CENTER if b.get('align')=='center' else PP_ALIGN.LEFT,first_line_indent=b.get('first_line_indent',0),paragraph_space=b.get('paragraph_space',0),bullet=b.get('bullet'))
                item['text']=b['text'].replace('**','').replace('==','').replace('__','');item['font_size']=size
            elif kind in ('image','equation'):
                if kind=='equation':
                    source=b['_equation']['png'];size=b['_equation']['size_px'];notes.append('LaTeX: '+b['latex'])
                    item['latex']=b['latex']
                else:source=b['_path'];size=b['_size']
                cap_h=38 if b.get('caption') else 0
                if kind=='equation':
                    cap_h=0
                frame=Box(box.x,box.y,box.w,box.h-cap_h)
                # Formulae are set at their natural point size and are never stretched to fill a slide.
                if kind=='equation':
                    if b.get('caption'):
                        frame.w-=56
                    nw,nh=b['_equation']['size_pt'];scale=min(1,frame.w/nw,frame.h/nh)
                    frame=Box(frame.x+(frame.w-nw*scale)/2,frame.y+(frame.h-nh*scale)/2,nw*scale,nh*scale)
                fitted,mode,warning=fit_image(size,frame,b.get('fit','contain'),b.get('allow_crop',False),tokens['quality']['max_image_crop'])
                if warning:warnings.append({'page':index,'id':b['id'],'message':warning})
                if mode=='cover':pic=slide.shapes.add_picture(source,Pt(fitted.x),Pt(fitted.y));pic.crop_left=0;pic.crop_right=0
                else:pic=slide.shapes.add_picture(source,*[Pt(v) for v in fitted.as_list()])
                if mode=='cover':
                    # Public add_picture cannot crop to box; compute symmetrical source crop explicitly.
                    pic.left=Pt(fitted.x);pic.top=Pt(fitted.y);pic.width=Pt(fitted.w);pic.height=Pt(fitted.h)
                    ratio=size[0]/size[1];target=fitted.w/fitted.h
                    if ratio>target:pic.crop_left=pic.crop_right=(1-target/ratio)/2
                    else:pic.crop_top=pic.crop_bottom=(1-ratio/target)/2
                pic._element.nvPicPr.cNvPr.set('descr',b.get('alt',b.get('latex',b.get('caption',''))))
                item.update(actual_box=fitted.as_list(),source_size=size,fit=mode)
                if kind=='equation' and b.get('caption'):
                    text_box(slide,b['caption'],Box(box.x+box.w-52,box.y+box.h/2-17,52,34),tokens['type']['caption'],tokens,align=PP_ALIGN.RIGHT,padding=0)
                if cap_h:text_box(slide,b['caption'],Box(box.x,min(box.y+box.h-cap_h+4,fitted.y+fitted.h+6),box.w,cap_h-4),tokens['type']['caption'],tokens,fill=colors['text'],align=PP_ALIGN.CENTER,padding=0)
            elif kind=='table':
                table_y=box.y+TABLE_CAPTION_HEIGHT if b.get('caption') else box.y
                style=b.get('style','grid')
                contents=([b['columns']] if not b.get('hide_header') else [])+[v['cells'] for v in b['rows']]
                table=slide.shapes.add_table(len(contents),len(b['columns']),Pt(box.x),Pt(table_y),Pt(box.w),Pt(sum(b['row_heights']))).table
                table.first_row=not b.get('hide_header',False);table.horz_banding=False
                for col,cw in zip(table.columns,b['column_widths']):col.width=Pt(cw)
                for row,rh in zip(table.rows,b['row_heights']):row.height=Pt(rh)
                for r,cells in enumerate(contents):
                    for c,value in enumerate(cells):
                        cell=table.cell(r,c);cell.fill.solid();cell.fill.fore_color.rgb=color(colors['cyan'] if r==0 else colors['white'])
                        if style in ('bands','underline','borderless'):cell.fill.background()
                        align=PP_ALIGN.CENTER
                        if style in ('underline','borderless'):align=PP_ALIGN.RIGHT if c==0 else PP_ALIGN.LEFT
                        set_text(cell,value,tokens['type']['table'],tokens,bold=r==0 and not b.get('hide_header'),padding=4,align=align)
                        cell.vertical_anchor=MSO_ANCHOR.MIDDLE
                        props=cell._tc.get_or_add_tcPr()
                        for edge_index,edge in enumerate(('lnL','lnR','lnT','lnB')):
                            for old in list(props):
                                if old.tag.endswith('}'+edge):props.remove(old)
                            ln=OxmlElement('a:'+edge);ln.set('w','6350')
                            hidden=style=='borderless' or (style=='underline' and edge!='lnB') or (
                                style=='bands' and ((edge=='lnL' and c>0) or (edge=='lnR' and c<len(cells)-1))
                            )
                            if hidden:ln.append(OxmlElement('a:noFill'))
                            else:
                                fill=OxmlElement('a:solidFill');rgb=OxmlElement('a:srgbClr');rgb.set('val',colors['line'] if style=='grid' else colors['text']);fill.append(rgb);ln.append(fill)
                            props.insert(edge_index,ln)
                item['row_ids']=[r['id'] for r in b['rows']];item['rows']=b['rows'];item['columns']=b['columns']
                notes.append('Table row IDs: '+json.dumps(item['row_ids'],ensure_ascii=False))
                if b.get('caption'):text_box(slide,b['caption'],Box(box.x,box.y,box.w,30),tokens['type']['caption'],tokens,fill=colors['text'],padding=0,align=PP_ALIGN.CENTER)
            elif kind=='diagram':
                from .diagrams import draw_diagram
                item.update(draw_diagram(slide,b,box,tokens))
            elif kind=='chart':
                from .charts import draw_chart
                draw_chart(slide,b,box,tokens)
            items.append(item)
        slide.notes_slide.notes_text_frame.text='\n'.join(notes)
        manifest.append({'page':index,'source_slide':page.source_slide,'title':page.title,'layout':page.layout,'elements':items})
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);prs.save(output)
    return manifest,warnings
