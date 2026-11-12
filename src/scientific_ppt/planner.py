"""Lossless content pagination. Semantic narrative planning belongs to the Agent."""
from copy import deepcopy
from pathlib import Path
from .models import Page,Element,Box,validate_deck,LayoutError
from .typography import text_height,split_text
from .tables import TABLE_CAPTION_HEIGHT, paginate_table
from .images import prepare_image
from .layout import content_box,gallery_boxes


def plan(deck,tokens,base_dir,cache,safety=None):
    validate_deck(deck)
    safety=safety or tokens['quality']['measurement_safety']
    pages=[];base_dir=Path(base_dir)
    for source_index,slide in enumerate(deck['slides']):
        blocks=deepcopy(slide['blocks'])
        for i,b in enumerate(blocks):
            b.setdefault('id',f's{source_index+1}-b{i+1}')
            if b['type']=='image':
                path=Path(b['path']);path=path if path.is_absolute() else base_dir/path
                path,size=prepare_image(path,cache)
                b['_path']=str(path);b['_size']=list(size)
        box,_=content_box(slide['title'],tokens)
        gap=tokens['spacing']['gap'];size=tokens['type']['body']
        start=len(pages)
        if slide.get('layout') in ('composed','cover','end'):
            from .equations import render_equation
            p=Page(slide['title'],notes=slide.get('notes',''),source_slide=source_index,layout=slide['layout'])
            for b in blocks:
                if 'box' not in b:
                    raise LayoutError('Composed pages require a box for every block')
                slot=Box(*b['box'])
                if b['type']=='equation':
                    b['_equation']=render_equation(b['latex'],cache)
                if b['type']=='table':
                    caption_h=TABLE_CAPTION_HEIGHT if b.get('caption') else 0
                    parts=paginate_table(b,slot.w,slot.h,tokens,safety,caption_height=caption_h)
                    if len(parts)!=1:
                        raise LayoutError('Composed table exceeds its region. Use a dedicated table page for automatic pagination.')
                    b.update(parts[0])
                p.elements.append(Element(b,slot))
            pages.append(p)
            continue
        def new_page(layout='stack'):
            p=Page(slide['title'],notes=slide.get('notes',''),source_slide=source_index,layout=layout)
            pages.append(p);return p
        def text_pages(text_blocks):
            p=None;y=box.y
            for b in text_blocks:
                for chunk in split_text(b['text'],box.w,box.h,size,tokens,safety):
                    h=text_height(chunk,box.w,size,tokens,safety)
                    if p is None or y+h>box.y+box.h+.1:p=new_page();y=box.y
                    child={**b,'text':chunk}
                    p.elements.append(Element(child,Box(box.x,y,box.w,h)))
                    y+=h+gap
        images=[b for b in blocks if b['type']=='image']
        texts=[b for b in blocks if b['type']=='text']
        if images and len(images)+len(texts)==len(blocks):
            if len(images)==1 and texts and .45<=images[0]['_size'][0]/images[0]['_size'][1]<=2.3 and slide.get('layout','auto') in ('auto','split'):
                tw=(box.w-gap)*.48
                needed=sum(text_height(b['text'],tw,size,tokens,safety)+gap for b in texts)
                if needed-gap<=box.h:
                    p=new_page('split');y=box.y
                    for b in texts:
                        bh=text_height(b['text'],tw,size,tokens,safety)
                        p.elements.append(Element(b,Box(box.x,y,tw,bh)));y+=bh+gap
                    p.elements.append(Element(images[0],Box(box.x+tw+gap,box.y,box.w-tw-gap,box.h)))
                    continue
            intro_h=sum(text_height(b['text'],box.w,size,tokens,safety)+gap for b in texts)
            if intro_h>box.h*.3:
                text_pages(texts);texts=[];intro_h=0
            for group_start in range(0,len(images),4):
                p=new_page('gallery');y=box.y
                if group_start==0:
                    for b in texts:
                        bh=text_height(b['text'],box.w,size,tokens,safety)
                        p.elements.append(Element(b,Box(box.x,y,box.w,bh)));y+=bh+gap
                group=images[group_start:group_start+4]
                slots=gallery_boxes(group,Box(box.x,y,box.w,box.y+box.h-y),gap)
                p.elements.extend(Element(b,s) for b,s in zip(group,slots))
        elif all(b['type']=='text' for b in blocks):text_pages(blocks)
        else:
            pending=[]
            for b in blocks:
                if b['type']=='text':pending.append(b);continue
                if pending:text_pages(pending);pending=[]
                if b['type']=='table':
                    caption_h=TABLE_CAPTION_HEIGHT if b.get('caption') else 0
                    for part_index,part in enumerate(paginate_table(b,box.w,box.h,tokens,safety,caption_height=caption_h)):
                        p=new_page('table')
                        child={**b,**part}
                        if part_index:child.pop('caption',None)
                        p.elements.append(Element(child,Box(box.x,box.y,box.w,sum(part['row_heights'])+(caption_h if not part_index else 0))))
                elif b['type']=='equation':
                    # Multiple formulae on the same source slide share a page when possible.
                    from .equations import render_equation
                    eq=render_equation(b['latex'],cache)
                    ew,eh=eq['size_pt']; scale=min(1.0,box.w/ew)
                    if scale<.7 or eh*scale+60>box.h:
                        raise LayoutError('Formula is too large. Split the derivation into separate equations.')
                    bh=max(80,eh*scale+60)
                    p=pages[-1] if len(pages)>start and pages[-1].layout=='equations' else None
                    y=(p.elements[-1].box.y+p.elements[-1].box.h+gap) if p else box.y
                    if p is None or y+bh>box.y+box.h:p=new_page('equations');y=box.y
                    p.elements.append(Element({**b,'_equation':eq},Box(box.x,y,box.w,bh)))
                else:
                    p=new_page('figure');p.elements.append(Element(b,box))
            if pending:text_pages(pending)
        for i,p in enumerate(pages[start:],1):p.continuation=i
    if not pages:raise LayoutError('No content pages')
    return pages
