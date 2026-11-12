from itertools import groupby
from .typography import text_height
from .models import LayoutError

TABLE_CAPTION_HEIGHT = 32

def paginate_table(block,width,height,tokens,safety=1.0,*,caption_height=0):
    n=len(block['columns']); size=tokens['type']['table']
    widths=[width*x for x in block.get('widths',[1/n]*n)]
    if min(widths)<size*2.5:
        raise LayoutError('Table columns too narrow. Split columns into linked tables or use a wider canvas.')
    def row_height(cells):
        return max(32,max(text_height(c,w-8,size,tokens,safety) for c,w in zip(cells,widths))+10)
    head=0 if block.get('hide_header') else row_height(block['columns'])
    full_capacity=height-head
    capacity=full_capacity-caption_height
    if capacity<32: raise LayoutError('Table header leaves no space for rows')
    groups=[]
    for _,rows in groupby(enumerate(block['rows']),lambda p: ('group',p[1]['group']) if p[1].get('group') else ('row',p[0])):
        groups.append([(i,r,row_height(r['cells'])) for i,r in rows])
    pages=[];current=[];used=0
    for group in groups:
        total=sum(r[2] for r in group)
        if total<=full_capacity and current and used+total>capacity:
            pages.append(current);current=[];used=0
            capacity=full_capacity
        for row in group:
            if current and used+row[2]>capacity:
                pages.append(current);current=[];used=0
                capacity=full_capacity
            if row[2]>capacity:
                raise LayoutError(f'Table row {row[1]["id"]} is taller than a page. Restructure this row explicitly; no data was dropped.')
            current.append(row);used+=row[2]
    if current: pages.append(current)
    flattened=[r[1] for p in pages for r in p]
    assert flattened==block['rows'], 'Table data conservation failed'
    result=[]
    for index,page in enumerate(pages):
        heights=([head] if head else [])+[r[2] for r in page]
        available=height-caption_height if index==0 else height
        if index<len(pages)-1 or block.get('fill_height',False):
            extra=max(0,available-sum(heights))/len(page)
            heights=([head] if head else [])+[r[2]+extra for r in page]
        result.append({'rows':[r[1] for r in page],'row_indices':[r[0] for r in page], 'row_heights':heights, 'column_widths':widths})
    return result
