"""Create the composed Transformer example using the scientific-ppt schema."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/my-transformer-v3'
OUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache' / 'matplotlib'))
sys.path.insert(0, str(ROOT / 'src'))

from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
from scientific_ppt.typography import resolve_font

SOURCE = 'Vaswani et al., Attention Is All You Need, NeurIPS 30, 2017. https://arxiv.org/abs/1706.03762'


def draw_causal_mask(path):
    """Draw the four-token causal visibility matrix used in the example."""
    figure = Figure(figsize=(5.4, 5.4), dpi=190, facecolor='#F7F7F7')
    axis = figure.add_axes([.205, .11, .72, .72])
    font = FontProperties(fname=resolve_font('SimSun')[0], size=17)
    positions = range(4)
    for query in positions:
        for key in positions:
            visible = key <= query
            axis.add_patch(Rectangle((key, query), 1, 1,
                                     facecolor='#CCFFFF' if visible else '#E5E5E5',
                                     edgecolor='white', linewidth=2))
            axis.text(key + .5, query + .5, '可见' if visible else '屏蔽',
                      color='#161616' if visible else '#606060', fontproperties=font,
                      ha='center', va='center')
    axis.set(xlim=(0, 4), ylim=(4, 0), aspect='equal')
    for ticks in (axis.set_xticks, axis.set_yticks):
        ticks([index + .5 for index in positions], [str(index + 1) for index in positions])
    axis.xaxis.tick_top()
    axis.xaxis.set_label_position('top')
    axis.set_xlabel('键位置', fontproperties=font, labelpad=8)
    axis.set_ylabel('查询位置', fontproperties=font, labelpad=8)
    axis.tick_params(length=0, labelsize=15, pad=5)
    for spine in axis.spines.values():
        spine.set_visible(False)
    figure.savefig(path)


def text(value, box, size=22, heading=False, panel=None, align='left'):
    item = dict(type='text', text=value, box=box, font_size=size, heading=heading, align=align)
    if panel:
        item['panel'] = panel
    return item


def equation(value, box, number):
    return dict(type='equation', latex=value, box=box, caption=f'（{number}）', source=SOURCE)


def page(title, blocks, layout='composed', notes=''):
    return dict(title=title, layout=layout, blocks=blocks, notes=SOURCE+'\n'+notes)


def table(columns, widths, rows, box, caption):
    return dict(type='table', columns=columns, widths=widths,
                rows=[dict(id=f'row-{i}', cells=row) for i, row in enumerate(rows)],
                box=box, caption=caption, fill_height=False, source=SOURCE)


def node(name, label, x, y, w=140, h=38, color='cyan'):
    return dict(id=name, label=label, box=[x, y, w, h], color=color)


def edge(a, b, points):
    return {'from': a, 'to': b, 'route': points}


nodes = []
edges = []
enc = ['嵌入 + 位置编码', '多头自注意力', 'Add & Norm', '逐位置 FFN', 'Add & Norm']
dec = ['右移嵌入 + 位置', '掩码多头注意力', 'Add & Norm', '交叉注意力', 'Add & Norm', '逐位置 FFN', 'Add & Norm']
for prefix, labels, x, color in [('e', enc, 12, 'cyan'), ('d', dec, 228, 'green')]:
    for i, label in enumerate(labels):
        nodes.append(node(f'{prefix}{i}', label, x, i*46, color=color))
        if i:
            edges.append(edge(f'{prefix}{i-1}', f'{prefix}{i}', [[x+70, (i-1)*46+38], [x+70, i*46]]))
# Residual routes stay outside node boundaries.
for prefix, x, pairs in [('e',12,[(0,2),(2,4)]),('d',228,[(0,2),(2,4),(4,6)])]:
    for a, b in pairs:
        lane = x-10
        edges.append(edge(f'{prefix}{a}', f'{prefix}{b}',
                          [[x,a*46+19],[lane,a*46+19],[lane,b*46+19],[x,b*46+19]]))
edges.append(edge('e4','d3', [[152,203],[190,203],[190,157],[228,157]]))
architecture = dict(type='diagram', box=[24,110,412,398], nodes=nodes, edges=edges,
                    direction='TB', caption='图 1  编码器与解码器子层', source=SOURCE)

slides = [
page('Transformer', [
    text('Transformer', [32,85,656,85],54,True,align='center'),
    text('从注意力计算到编码器—解码器', [32,176,656,50],28,True,align='center'),
    text('架构原理与计算过程', [72,247,576,53],26,True,'gradient','center'),
    text('• 读懂 Q、K、V 与多头注意力\n• 理解掩码、位置编码和残差连接\n• 串联训练过程与逐词生成', [92,327,550,135],24),
    text('基于 Attention Is All You Need（2017）', [72,471,576,32],18,align='center')
], 'cover'),
page('目录', [
    text('01  整体架构', [24,86,326,74],26,True,'gradient'),
    text('编码器、解码器及跨序列的信息流。',[24,168,326,78]),
    text('02  注意力计算', [370,86,326,74],26,True,'gradient'),
    text('Q / K / V、多头机制与因果掩码。',[370,168,326,78]),
    text('03  子层与参数', [24,268,326,74],26,True,'gradient'),
    text('位置编码、前馈网络、残差连接与模型维度。',[24,350,326,110]),
    text('04  训练与生成', [370,268,326,74],26,True,'gradient'),
    text('右移输入、并行训练与自回归预测。',[370,350,326,110])
]),
page('整体架构与残差路径', [
    text('编码器', [35,73,150,36],18,True,align='center'),
    text('解码器', [251,73,150,36],18,True,align='center'),
    architecture,
    text('两侧分别堆叠 6 层', [450,89,246,44],22,True,'gradient'),
    text('• **编码器**建立源序列的上下文表示。\n\n• **交叉注意力**读取编码器最终输出。\n\n• 外侧折线是**残差路径**，连接子层输入与输出。', [450,145,246,237],20),
    text('Add & Norm\n残差相加后做层归一化。解码器顶部输出再经线性层与 softmax。',[450,394,246,110],18,False,'outline')
], notes='图按信息流自上而下排列，展示一层的子层与输入。跨列连线代表编码器完整堆栈最终输出。'),
page('Q、K、V 如何产生注意力', [
    text('1. 线性投影', [24,82,672,42],24,True,'gradient'),
    equation(r'Q=XW^Q,\quad K=XW^K,\quad V=XW^V',[24,125,672,86],1),
    text('• **Q（查询）**表示当前位置要检索的信息。\n• **K（键）**参与匹配分数计算，**V（值）**提供聚合内容。',[24,218,672,76],22),
    text('2. 匹配、归一化与加权', [24,307,672,42],24,True,'gradient'),
    equation(r'A=\operatorname{softmax}\left(QK^{\mathsf T}/\sqrt{d_k}\right),\quad Z=AV',[24,352,672,88],2),
    text('每行对应一个查询。dₖ 为单头键维度，缩放可缓和点积幅度增大。',[24,450,672,56],20)
]),
page('用一个查询理解加权聚合', [
    dict(type='chart', kind='bar', categories=['我','读','书'], series=[dict(name='注意力权重',values=[.090030573,.244728471,.665240956])], box=[24,90,348,300],caption='图 2  三个词元的注意力权重'),
    text('教学算例', [390,87,306,42],24,True,'gradient'),
    text('• 假设查询“读”的缩放分数为 **0、1、2**。\n\n• softmax 后的权重约为 **0.09、0.24、0.67**。\n\n• 输出对各值向量加权求和。',[390,143,306,241],22),
    equation(r'z=0.09v_1+0.24v_2+0.67v_3',[24,400,672,92],3)
], notes='教学数值由 softmax([0,1,2]) 计算。式（3）使用两位小数近似。'),
page('多头注意力与张量维度', [
    text('多组投影并行计算，再拼接输出', [24,84,672,42],24,True,'gradient'),
    equation(r'\operatorname{head}_i=\operatorname{Attention}(XW_i^Q,XW_i^K,XW_i^V)',[24,136,672,88],4),
    equation(r'\operatorname{MultiHead}(X)=\operatorname{Concat}(h_1,\ldots,h_8)W^O',[24,232,672,84],5),
    text('投影与分头\n• 输入 X 的宽度为 **512**。\n• 每个头的键和值宽度为 **64**。\n• 各头使用独立的投影参数。',[24,333,326,170],20,False,'outline'),
    text('拼接与融合\n• 8 个头拼接为 **512** 维。\n• 输出投影混合各头信息。\n• 各头可学习不同的匹配模式。',[370,333,326,170],20,False,'gradient')
], notes='式（5）中 h_i 表示 head_i。以自注意力和 Base 配置为例。'),
page('因果掩码与三种注意力', [
    dict(type='image',path='causal-mask.png',box=[24,81,320,325],caption='图 3  因果注意力可见区域'),
    text('逐行理解可见范围', [362,85,334,42],24,True,'gradient'),
    text('• **行**是查询，**列**是键。\n\n• 查询 3 读取键 1 至 3。\n\n• 未来位置先加负无穷，归一化后权重为零。',[362,142,334,216],22),
    text('目标输入已右移。因此，对角线位置对应的是当前已知输入，预测仍只依赖此前目标词元。',[24,420,672,84],22,False,'outline')
]),
page('三种注意力的作用对照', [
    table(['模块','Q 来源','K、V 来源','可见范围'],[.27,.22,.23,.28],
          [['编码器自注意力','源序列表示','源序列表示','全部有效源位置'],
           ['解码器自注意力','目标端表示','目标端表示','当前及此前位置'],
           ['交叉注意力','解码器表示','编码器输出','全部有效源位置']],
          [24,82,672,287],'表 1  注意力模块的输入与可见范围'),
    text('• **自注意力**在同一序列内部建立上下文联系。\n• **交叉注意力**让目标端查询源序列的信息。\n• 三种模块都需要屏蔽填充位置。',[24,389,672,116],22)
]),
page('位置编码与逐位置前馈网络', [
    text('位置信息进入输入表示', [24,82,672,40],24,True,'gradient'),
    equation(r'X=E+P,\quad P_{p,2i}=\sin\left(p/10000^{2i/d}\right)',[24,128,672,88],6),
    text('偶数维使用正弦，奇数维使用余弦。位置向量与词嵌入同维相加，保留序列次序信息。',[24,223,672,68],22),
    text('FFN 对每个位置做非线性变换', [24,303,672,40],24,True,'gradient'),
    equation(r'\operatorname{FFN}(x)=\max(0,xW_1+b_1)W_2+b_2',[24,348,672,88],7),
    text('各位置共享参数。Base 配置的 FFN 维度为 **512 → 2048 → 512**。',[24,440,672,66],22)
]),
page('残差连接与层归一化', [
    equation(r'y=\operatorname{LayerNorm}\left(x+\operatorname{Sublayer}(x)\right)',[24,84,672,93],8),
    text('残差连接', [24,190,326,42],24,True,'gradient'),
    text('• 保留子层输入，叠加新变换。\n\n• 相加要求输入与输出具有相同宽度。\n\n• 原架构各子层保持 **512** 维残差流。',[24,246,326,253],22,False,'outline'),
    text('层归一化', [370,190,326,42],24,True,'gradient'),
    text('• 按每个词元的特征维度计算归一化。\n\n• 原论文采用 **Post-LN** 顺序。\n\n• 每个注意力和 FFN 子层均使用这一结构。',[370,246,326,253],22,False,'outline')
]),
page('Base 配置与计算规模', [
    table(['参数','数值','含义'],[.30,.18,.52],
          [['编码层 / 解码层','6 / 6','两侧各自的堆叠深度'],
           ['模型宽度','512','嵌入与残差流维度'],
           ['注意力头数','8','每个注意力子层的头数'],
           ['单头键 / 值宽度','64 / 64','每个头的投影维度'],
           ['FFN 隐层宽度','2048','前馈网络中间层维度']],
          [24,82,672,331],'表 2  原论文 Transformer Base 的主要配置'),
    text('**计算规模**　序列长度翻倍，全注意力分数矩阵的元素数增至四倍。',[24,427,672,78],22,False,'gradient')
]),
page('训练与推理的输入差异', [
    text('训练阶段', [24,82,326,43],24,True,'gradient'),
    text('• 使用**右移的真实目标序列**作为输入。\n\n• 所有位置可并行预测。\n\n• 因果掩码阻止读取未来目标信息。',[24,141,326,234],22,False,'outline'),
    text('推理阶段', [370,82,326,43],24,True,'gradient'),
    text('• 使用**已生成的词元前缀**作为输入。\n\n• 每步追加一个预测词元。\n\n• 输出结束符或达到长度上限时停止。',[370,141,326,234],22,False,'outline'),
    text('例子\n输入〈开始〉预测“我”，输入〈开始〉我预测“读”，随后继续生成“书”。',[24,393,672,110],22,False,'gradient')
]),
page('小结与参考文献', [
    text('三个要点', [24,84,672,43],24,True,'gradient'),
    text('1. **注意力**通过查询与键匹配，对值向量加权聚合。\n\n2. **多头、FFN 与残差**共同构成可堆叠的表示变换。\n\n3. **掩码与右移输入**连接并行训练和逐词生成。',[24,144,672,209],23),
    text('参考文献（IEEE 格式）',[24,373,672,39],22,True),
    text('[1] A. Vaswani et al., “Attention Is All You Need,” in Advances in Neural Information Processing Systems, vol. 30, 2017.',[24,423,672,82],20)
]),
page('The End', [
    text('THE END',[48,125,624,100],56,True,align='center'),
    text('谢谢聆听',[48,246,624,67],34,True,align='center'),
    text('讨论\n一个词元如何从其他位置获取信息？',[80,357,560,107],26,False,'gradient','center')
], 'end')
]

# Editorial revision: preserve topic boundaries and natural table row heights.
slides[0]['blocks']=[
    text('Transformer 架构',[38,143,644,78],44,True,align='center'),
    text('原理与计算过程',[38,229,644,50],28,True,align='center'),
    dict(type='table',columns=['项目','信息'],widths=[.38,.62],hide_header=True,style='bands',
         rows=[dict(id=f'cover-{i}',cells=[label,'xxx']) for i,label in enumerate(['汇报人','所属单位','汇报时间'])],
         box=[176,332,368,145])]
slides[-1]['blocks']=[text('THE END',[48,174,624,100],56,True,align='center'),
                     text('谢谢聆听',[48,292,624,67],34,True,align='center')]
for index in (7,10):
    slides[index]['blocks']=[slides[index]['blocks'][0]]
    slides[index]['blocks'][0]['box']=[24,88,672,408]
slides[12]['title']='小结'
reference=slides[12]['blocks'][-1]
reference['box']=[28,104,664,180]
slides[12]['blocks']=slides[12]['blocks'][:2]
slides.insert(-1,page('参考文献',[reference]))

def paragraph(value,box):
    return {**text(value,box,23),'first_line_indent':2,'paragraph_space':18}

slides.insert(2,page('为什么使用注意力',[
    text('从顺序递推到直接建立联系',[24,84,672,43],25,True),
    paragraph('循环网络沿序列逐步更新状态，较远位置之间的信息需要经过多个递推步骤。Transformer 通过==自注意力==直接计算词元之间的联系，使每个位置能够聚合其他位置的表示。',[24,145,672,147]),
    paragraph('在编码器中，各位置可以并行计算上下文表示。模型再加入位置编码，使表示同时包含内容与次序信息。解码器通过因果掩码限制可见范围，维持__从左到右生成__的条件。',[24,318,672,155])
]))
base_index=next(i for i,s in enumerate(slides) if s['title']=='Base 配置与计算规模')
slides.insert(base_index+1,page('模型宽度与序列长度',[
    text('宽度决定表示空间，长度影响注意力规模',[24,84,672,43],24,True),
    paragraph('Base 模型使用 512 维表示，8 个注意力头分别在 64 维子空间中计算，再拼接并投影。前馈网络将维度扩展到 2048 后映射回 512，使子层输出能够与输入进行残差相加。',[24,145,672,147]),
    paragraph('对长度为 n 的序列，每个头的全注意力分数矩阵包含 n² 个元素。__序列长度翻倍__，元素数量会变为四倍。因此，处理长序列时，需要同时考虑中间表示的存储和注意力计算开销。',[24,318,672,155])
]))

# Restrained variation: most headings are unboxed; colored panels group body copy.
gradients=[
    dict(colors=['FFFFFF','DDEDF9'],kind='linear',angle=0),
    dict(colors=['FFF5CF','FFFFFF'],kind='linear',angle=90),
    dict(colors=['FFFFFF','DDF0DE'],kind='radial',focus=[.25,.3]),
    dict(colors=['E1EEF9','FFFFFF'],kind='linear',angle=135),
    dict(colors=['FFFFFF','FFF0C8'],kind='radial',focus=[.7,.6])]
body_panel=0
for si,s in enumerate(slides):
    for bi,b in enumerate(s['blocks']):
        if b['type']=='text':
            if b.get('heading') and b.get('panel')=='gradient':b.pop('panel')
            if b.get('heading') and si%2==0 and s['layout'] not in ('cover','end'):b['emphasis']='blue'
            if b.get('panel')=='gradient':
                b['gradient']=gradients[body_panel%len(gradients)];body_panel+=1
            if '• ' in b['text'] and b['text'].startswith('• '):
                b['text']=b['text'].replace('• ','')
                b['bullet']=dict(symbol=['■','●','□','○'][si%4],color='A50021' if si%3==0 else '111111')
    if s['title']=='目录':
        for i,b in enumerate(s['blocks']):
            if not b.get('heading'):
                b['panel']='gradient';b['gradient']=gradients[(i//2)%len(gradients)]
    if s['title']=='用一个查询理解加权聚合':
        s['blocks'][0].update(palette=['237DB5','239B73','E8B52B'],vary_categories=True)
    if s['title']=='Q、K、V 如何产生注意力':
        s['blocks'][2]['text']=s['blocks'][2]['text'].replace('**Q（查询）**','==Q（查询）==')

draw_causal_mask(OUT/'causal-mask.png')
(OUT/'deck.json').write_text(json.dumps(dict(version='1.0',title='Transformer 架构原理与计算过程',english_title='TRANSFORMER  /  ATTENTION IS ALL YOU NEED',language='zh-CN',slides=slides),ensure_ascii=False,indent=2),encoding='utf-8')
tokens=json.loads((ROOT/'references/design_tokens.json').read_text(encoding='utf-8'))
tokens['type'].update(node=16,body=22,title=30)
tokens['spacing']['line_height']=1.12
(OUT/'tokens.json').write_text(json.dumps(tokens,ensure_ascii=False,indent=2),encoding='utf-8')

print(OUT/'deck.json')
