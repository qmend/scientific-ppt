"""Editable graph layout. Automatic DAG ranks, explicit nodes and feedback routes."""
from collections import defaultdict,deque
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR
from pptx.util import Pt
from pptx.oxml.xmlchemy import OxmlElement
from .models import Box,LayoutError
from .typography import text_height


def node_boxes(block,box,tokens):
    nodes=block['nodes'];size=tokens['type']['node'];gap=30
    if all('box' in n for n in nodes):
        boxes={n['id']:Box(box.x+n['box'][0],box.y+n['box'][1],n['box'][2],n['box'][3]) for n in nodes}
    elif all('position' in n for n in nodes):
        nw=min(140,box.w*.22);nh=68
        boxes={n['id']:Box(box.x+n['position'][0]*(box.w-nw),box.y+n['position'][1]*(box.h-nh),nw,nh) for n in nodes}
    else:
        indegree={n['id']:0 for n in nodes};adj=defaultdict(list);ranks={key:0 for key in indegree}
        for e in block['edges']:
            if not e.get('feedback'):
                indegree[e['to']]+=1;adj[e['from']].append(e['to'])
        q=deque(k for k,v in indegree.items() if v==0);visited=0
        while q:
            node=q.popleft();visited+=1
            for nxt in adj[node]:
                ranks[nxt]=max(ranks[nxt],ranks[node]+1);indegree[nxt]-=1
                if indegree[nxt]==0:q.append(nxt)
        if visited!=len(nodes):raise LayoutError('Diagram has a cycle. Mark feedback edges or provide positions for every node.')
        levels=defaultdict(list)
        for n in nodes:levels[ranks[n['id']]].append(n)
        horizontal=block.get('direction','LR')=='LR';count=len(levels)
        nw=(box.w-gap*(count-1))/count if horizontal else min(220,box.w/(max(map(len,levels.values()))+.4))
        nh=min(76,(box.h-gap*(count-1))/count) if not horizontal else 76
        if nw<80 or nh<42:raise LayoutError('Diagram too dense. Split into overview and detailed stages.')
        boxes={}
        for rank,group in levels.items():
            if horizontal:
                slot=box.h/len(group)
                if slot<nh+8:raise LayoutError('Too many parallel diagram nodes; split the diagram')
                for j,n in enumerate(group):boxes[n['id']]=Box(box.x+rank*(nw+gap),box.y+(j+.5)*slot-nh/2,nw,nh)
            else:
                slot=box.w/len(group)
                for j,n in enumerate(group):boxes[n['id']]=Box(box.x+(j+.5)*slot-nw/2,box.y+rank*(nh+gap),nw,nh)
    for n in nodes:
        b=boxes[n['id']]
        pad=20 if n.get('kind')=='decision' else 8
        needed=text_height(n['label'],b.w-pad,size,tokens,1.12)
        if needed>b.h-pad:raise LayoutError(f'Diagram label {n["id"]} is too long. Shorten the label or use a detail page.')
    return boxes


def draw_diagram(slide,block,box,tokens):
    from .pptx_writer import rectangle,set_text,text_box,color
    cap=38 if block.get('caption') else 0
    graphbox=Box(box.x+8,box.y+20,box.w-16,box.h-cap-50)
    boxes=node_boxes(block,graphbox,tokens)
    def line(x1,y1,x2,y2,arrow=True):
        connector=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Pt(x1),Pt(y1),Pt(x2),Pt(y2))
        connector.line.color.rgb=color(tokens['colors']['text']);connector.line.width=Pt(1.3)
        connector._element.spPr.append(OxmlElement('a:effectLst'))
        if arrow:
            ln=connector._element.spPr.get_or_add_ln();end=OxmlElement('a:tailEnd');end.set('type','triangle');ln.append(end)
        return connector
    # Edges behind nodes. Arrows remain editable native DrawingML connectors.
    for idx,e in enumerate(block['edges']):
        a,b=boxes[e['from']],boxes[e['to']]
        if e.get('route'):
            points=[(graphbox.x+p[0],graphbox.y+p[1]) for p in e['route']]
            for i,(start,end) in enumerate(zip(points,points[1:])):
                line(*start,*end,arrow=i==len(points)-2)
            mx,my=points[len(points)//2]
        elif e.get('feedback'):
            y=box.y+5+(idx%2)*8
            line(a.x+a.w/2,a.y,a.x+a.w/2,y,False);line(a.x+a.w/2,y,b.x+b.w/2,y,False);line(b.x+b.w/2,y,b.x+b.w/2,b.y)
            mx,my=(a.x+b.x)/2,y
        elif block.get('direction','LR')=='LR':
            line(a.x+a.w,a.y+a.h/2,b.x,b.y+b.h/2)
            mx,my=(a.x+a.w+b.x)/2,(a.y+a.h/2+b.y+b.h/2)/2
        else:
            line(a.x+a.w/2,a.y+a.h,b.x+b.w/2,b.y)
            mx,my=(a.x+a.w/2+b.x+b.w/2)/2,(a.y+a.h+b.y)/2
        if e.get('label'):
            text_box(slide,e['label'],Box(mx-32,my-22,64,22),12,tokens,align=PP_ALIGN.CENTER,padding=0)
    kinds={'process':MSO_SHAPE.RECTANGLE,'decision':MSO_SHAPE.DIAMOND,'terminal':MSO_SHAPE.ROUNDED_RECTANGLE,'data':MSO_SHAPE.PARALLELOGRAM,'neuron':MSO_SHAPE.OVAL}
    for n in block['nodes']:
        b=boxes[n['id']]
        shape=rectangle(slide,b,tokens['colors'][n.get('color','white')],tokens['colors']['text'],kinds[n.get('kind','process')])
        shape.name='node:'+n['id']
        set_text(shape,n['label'],tokens['type']['node'],tokens,align=PP_ALIGN.CENTER,padding=8)
        shape.text_frame.vertical_anchor=MSO_ANCHOR.MIDDLE
    if cap:text_box(slide,block['caption'],Box(box.x,box.y+box.h-cap,box.w,cap),tokens['type']['caption'],tokens,align=PP_ALIGN.CENTER,fill=tokens['colors']['text'],padding=0)
    return {'nodes':[{'id':n['id'],'box':boxes[n['id']].as_list(),'label':n['label']} for n in block['nodes']], 'edges':block['edges']}
