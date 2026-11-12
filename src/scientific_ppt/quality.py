"""Geometry and rendered-output checks. These do not replace human visual review."""
from PIL import Image,ImageStat
from .typography import text_height


def inspect(manifest,tokens,render=None):
    issues=[];w,h=tokens['canvas']['width'],tokens['canvas']['height']
    def add(page,code,message,severity='error',**kw):issues.append({'page':page,'code':code,'severity':severity,'message':message,**kw})
    for page in manifest:
        number=page['page'];elements=page['elements'];area=0
        for e in elements:
            x,y,ew,eh=e['box'];area+=ew*eh
            if x<-.1 or y<-.1 or x+ew>w+.1 or y+eh>h-tokens['spacing']['footer']+.2:
                add(number,'bounds','Content exceeds safe slide bounds',id=e['id'])
            if e['type']=='text' and text_height(e['text'],ew,e['font_size'],tokens)>eh+.5:
                add(number,'text_overflow','Measured text exceeds its box',id=e['id'])
            if e['type']=='image' and e['fit']=='contain':
                ratio=e['actual_box'][2]/e['actual_box'][3];source=e['source_size'][0]/e['source_size'][1]
                if abs(ratio/source-1)>.005:add(number,'image_distortion','Image aspect ratio changed',id=e['id'])
            if e['type']=='diagram':
                for a,first in enumerate(e['nodes']):
                    for second in e['nodes'][a+1:]:
                        if intersection(first['box'],second['box'])>1:add(number,'node_overlap',f'Diagram nodes overlap: {first["id"]}, {second["id"]}')
        for i,a in enumerate(elements):
            for b in elements[i+1:]:
                if intersection(a['box'],b['box'])>1:add(number,'overlap',f'Content blocks overlap: {a["id"]}, {b["id"]}')
        occupancy=area/(w*h)
        if occupancy<tokens['quality']['min_occupancy']:add(number,'sparse','Low content occupancy; review composition','warning')
        if occupancy>tokens['quality']['max_occupancy']:add(number,'dense','High content occupancy; review readability','warning')
    if render:
        if render['status']!='rendered':add(None,'render_unavailable','Actual PPT rendering was unavailable; visual verification incomplete','warning')
        else:
            if len(render['images'])!=len(manifest):add(None,'page_count','Rendered page count differs from generated PPTX')
            for metric in render.get('metrics',[]):
                if metric['bound_height']>metric['available_height']+2 or metric['bound_width']>metric['available_width']+2:
                    add(metric['page'],'rendered_text_overflow',f'PowerPoint reports text overflow in {metric["name"]}',shape=metric['shape'],metrics=metric)
            for i,path in enumerate(render['images'],1):
                with Image.open(path) as im:
                    if max(ImageStat.Stat(im.convert('RGB')).stddev)<2:add(i,'blank_render','Slide rendered nearly blank')
    return issues


def intersection(a,b):
    return max(0,min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0]))*max(0,min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1]))
