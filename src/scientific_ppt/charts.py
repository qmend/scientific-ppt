from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE,XL_LEGEND_POSITION,XL_TICK_MARK
from pptx.util import Pt
from .models import Box


def draw_chart(slide,block,box,tokens):
    from .pptx_writer import color,text_box
    data=CategoryChartData();data.categories=block['categories']
    for s in block['series']:data.add_series(s['name'],s['values'])
    chart=slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED if block['kind']=='bar' else XL_CHART_TYPE.LINE,
        Pt(box.x),Pt(box.y),Pt(box.w),Pt(box.h-50),data).chart
    chart.has_title=False
    chart.has_legend=len(block['series'])>1
    if chart.has_legend:
        chart.legend.position=XL_LEGEND_POSITION.BOTTOM;chart.legend.font.size=Pt(14);chart.legend.include_in_layout=True
    for axis in (chart.category_axis,chart.value_axis):
        axis.tick_labels.font.size=Pt(14);axis.tick_labels.font.name=tokens['fonts']['body'];axis.major_tick_mark=XL_TICK_MARK.NONE
    chart.value_axis.has_major_gridlines=True
    chart.value_axis.major_gridlines.format.line.color.rgb=color('DADADA')
    chart.value_axis.major_gridlines.format.line.width=Pt(.5)
    if block.get('y_title'):
        chart.value_axis.has_title=True;chart.value_axis.axis_title.text_frame.text=block['y_title']
        for p in chart.value_axis.axis_title.text_frame.paragraphs:p.font.size=Pt(14)
    palette=block.get('palette') or tokens.get('charts',{}).get('palette') or ['7289AB','8DC1A9','E69D87','EEDD78','DD6B66','73B9BC']
    for i,series in enumerate(chart.series):
        c=color(palette[i%len(palette)])
        series.format.fill.solid();series.format.fill.fore_color.rgb=c
        series.format.line.color.rgb=c;series.format.line.width=Pt(2)
        if block.get('vary_categories') and block['kind']=='bar':
            for j,point in enumerate(series.points):
                point.format.fill.solid();point.format.fill.fore_color.rgb=color(palette[j%len(palette)])
                point.format.line.color.rgb=color(palette[j%len(palette)])
    if block.get('caption'):
        from pptx.enum.text import PP_ALIGN
        text_box(slide,block['caption'],Box(box.x,box.y+box.h-36,box.w,36),tokens['type']['caption'],tokens,fill=tokens['colors']['text'],padding=0,align=PP_ALIGN.CENTER)
