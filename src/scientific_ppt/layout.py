"""Content-dependent layout candidates in points, independent of PowerPoint."""
import math
from .models import Box, LayoutError
from .images import fit_image
from .typography import text_height


def content_box(title,tokens):
    w,h=tokens['canvas']['width'],tokens['canvas']['height'];s=tokens['spacing']
    title_h=text_height(title,w-2*s['margin'],tokens['type']['title'],tokens,1.04)
    header=max(s['header'],title_h+12)
    if header>h*.28: raise LayoutError('Title is too long; use a concise title and move detail into body text')
    top=max(s['content_top'],header+16)
    return Box(s['margin'],top,w-2*s['margin'],h-s['footer']-top),header


def gallery_boxes(images,box,gap=16):
    """Select by contained area, with an asymmetric option for mixed portrait/landscape."""
    count=len(images)
    if not count:return []
    candidates=[]
    for cols in range(1,min(3,count)+1):
        rows=math.ceil(count/cols)
        cw=(box.w-(cols-1)*gap)/cols;ch=(box.h-(rows-1)*gap)/rows
        candidates.append([Box(box.x+(i%cols)*(cw+gap),box.y+(i//cols)*(ch+gap),cw,ch) for i in range(count)])
    if count==3:
        for large in range(3):
            slots=[None]*3
            slots[large]=Box(box.x,box.y,(box.w-gap)*.48,box.h)
            for j,i in enumerate(k for k in range(3) if k!=large):
                slots[i]=Box(box.x+(box.w-gap)*.48+gap,box.y+j*(box.h+gap)/2,(box.w-gap)*.52,(box.h-gap)/2)
            candidates.append(slots)
    def score(slots):
        area=0
        for b,img in zip(slots,images):
            cap=38 if img.get('caption') else 0
            if b.h<=cap+18:return -1
            fit,_,_=fit_image(img['_size'],Box(b.x,b.y,b.w,b.h-cap))
            area+=fit.w*fit.h
        return area
    return max(candidates,key=score)
