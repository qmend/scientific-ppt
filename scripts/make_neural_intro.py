"""Reproducible introductory lecture, with a real NumPy XOR experiment."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/neural-network-intro'
OUT.mkdir(parents=True,exist_ok=True)
BOOK='[1] I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. MIT Press, 2016. https://www.deeplearningbook.org/'
RESNET='[2] K. He, X. Zhang, S. Ren, and J. Sun, Deep Residual Learning for Image Recognition, CVPR, 2016, pp. 770–778. https://arxiv.org/abs/1512.03385'
TORCH='[3] PyTorch Contributors, Optimizing Model Parameters, PyTorch Tutorials. https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html (accessed 2026-11-12).'
BLUE='237DB5'; GREEN='239B73'; YELLOW='E8B52B'

# Real four-sample experiment, no held-out/generalization performance is claimed.
rng=np.random.default_rng(17)
X=np.array([[0.,0.],[0.,1.],[1.,0.],[1.,1.]])
y=np.array([[0.],[1.],[1.],[0.]])
W1=rng.normal(0,.7,(2,8)); b1=np.zeros((1,8))
W2=rng.normal(0,.7,(8,1)); b2=np.zeros((1,1))
history=[]
for step in range(4001):
    h=np.tanh(X@W1+b1); logits=h@W2+b2
    p=1/(1+np.exp(-logits))
    loss=float(np.mean(np.logaddexp(0,logits)-y*logits))
    if step%400==0:history.append(dict(step=step,loss=loss))
    if step==4000:break
    dz=(p-y)/4; g2=h.T@dz; gb2=dz.sum(0,keepdims=True)
    dh=(dz@W2.T)*(1-h*h); g1=X.T@dh; gb1=dh.sum(0,keepdims=True)
    W1-=.1*g1; b1-=.1*gb1; W2-=.1*g2; b2-=.1*gb2
assert np.array_equal((p>=.5).astype(int),y.astype(int))
experiment=dict(seed=17,steps=4000,learning_rate=.1,architecture=[2,8,1],parameter_count=33,
                inputs=X.tolist(),targets=y[:,0].tolist(),probabilities=p[:,0].tolist(),history=history,
                scope='All four XOR samples used for training; no held-out evaluation.')
(OUT/'xor_results.json').write_text(json.dumps(experiment,indent=2),encoding='utf-8')
np.savez(OUT/'xor_weights.npz',W1=W1,b1=b1,W2=W2,b2=b2)

def t(value,box,size=22,heading=False,panel=None,blue=False,**kwargs):
    b=dict(type='text',text=value,box=box,font_size=size,heading=heading,**kwargs)
    if panel:b['panel']=panel
    if blue:b['emphasis']='blue'
    return b

def bullets(lines,box,symbol='■',red=False,size=22,panel=None):
    return t('\n\n'.join(lines),box,size,panel=panel,bullet=dict(symbol=symbol,color='A50021' if red else '161616'))

def para(value,box):return t(value,box,23,first_line_indent=2,paragraph_space=14)
def eq(latex,box,number):return dict(type='equation',latex=latex,box=box,caption=f'（{number}）')
def page(title,blocks,layout='composed',source=BOOK,notes=''):
    return dict(title=title,blocks=blocks,layout=layout,notes=source+'\n'+notes)
def node(key,label,x,y,w=150,h=62,color='white',kind='process'):
    return dict(id=key,label=label,box=[x,y,w,h],color=color,kind=kind)
def edge(a,b,route=None):
    e={'from':a,'to':b}
    if route:e['route']=route
    return e
def graph(nodes,edges,box,caption,direction='LR'):
    return dict(type='diagram',nodes=nodes,edges=edges,box=box,caption=caption,direction=direction)
def tab(columns,rows,widths,caption,box=None,group_size=None):
    data=[]
    for i,row in enumerate(rows):
        record=dict(id=f'R{i+1:02}',cells=row)
        if group_size:record['group']=f'G{i//group_size}'
        data.append(record)
    result=dict(type='table',columns=columns,rows=data,widths=widths,caption=caption)
    if box:result['box']=box
    return result

# Figure 1: three inputs with weighted fan-in, bias and nonlinear output.
neuron=graph([
    node('x1','x₁',0,0,68,48,'cyan','neuron'),node('x2','x₂',0,70,68,48,'cyan','neuron'),
    node('x3','x₃',0,140,68,48,'cyan','neuron'),node('sum','加权求和\n+ 偏置 b',178,62,154,72),
    node('act','激活函数\nφ(z)',402,62,140,72),node('out','输出 a',576,71,76,54)],
    [edge('x1','sum'),edge('x2','sum'),edge('x3','sum'),edge('sum','act'),edge('act','out')],
    [24,124,672,262],'图 1  人工神经元的计算过程')

# Figure 3: every connection is an editable PowerPoint line.
mlp_nodes=[];mlp_edges=[];layers=[]
for li,(count,x,color) in enumerate([(3,10,'white'),(4,196,'cyan'),(4,382,'green'),(2,568,'yellow')]):
    layer=[]
    for j in range(count):
        key=f'L{li}N{j}';layer.append(key)
        mlp_nodes.append(node(key,f'{j+1}',x,18+(4-count)*29+j*58,52,46,color,'neuron'))
    layers.append(layer)
for a,b in zip(layers,layers[1:]):mlp_edges += [edge(i,j) for i in a for j in b]
mlp=graph(mlp_nodes,mlp_edges,[24,125,672,310],'图 3  含两个隐藏层的全连接网络')

backprop=graph([
    node('x','输入 x',8,30,96,60),node('z','z = wx + b',162,30,142,60),
    node('a','a = σ(z)',364,30,132,60),node('L','损失 L',550,30,100,60),
    node('gw','参数梯度\n∂L/∂w',162,158,142,68),
    node('gz','局部梯度\n∂L/∂z',364,158,132,68)],
    [edge('x','z'),edge('z','a'),edge('a','L'),
     edge('L','gz',[[600,90],[600,192],[496,192]]),edge('gz','gw',[[364,192],[304,192]])],
    [24,120,672,290],'图 4  前向计算与反向梯度路径')

pipeline_nodes=[node('raw','原始数据\n与标签',0,0,172,65),
    node('split','先划分\n训练 / 验证 / 测试',240,0,180,65),
    node('prep','仅用训练集\n拟合预处理',480,0,172,65),
    node('batch','小批量输入',480,112,172,65),
    node('forward','前向计算\n预测与损失',240,112,180,65),
    node('update','反向传播\n更新参数',0,112,172,65),
    node('val','验证集选模型',0,224,172,65),
    node('freeze','冻结配置\n保存检查点',240,224,180,65),
    node('test','最终测试\n报告结果',480,224,172,65)]
pipeline_edges=[edge('raw','split'),edge('split','prep'),
    edge('prep','batch',[[566,65],[566,112]]),edge('batch','forward',[[480,144],[420,144]]),
    edge('forward','update',[[240,144],[172,144]]),edge('update','val',[[86,177],[86,224]]),
    edge('val','freeze'),edge('freeze','test'),
    edge('update','forward',[[86,112],[86,90],[330,90],[330,112]])]
pipeline=graph(pipeline_nodes,pipeline_edges,[24,90,672,348],'图 5  训练迭代与独立评估流程')

cnn_nodes=[node('input','输入图像\n28 × 28 × 1',0,0,176,65),
    node('c1','卷积 + ReLU\n28 × 28 × 8',238,0,176,65),
    node('p1','2 × 2 池化\n14 × 14 × 8',476,0,176,65),
    node('c2','卷积 + ReLU\n14 × 14 × 16',476,118,176,65),
    node('p2','2 × 2 池化\n7 × 7 × 16',238,118,176,65),
    node('flat','展平 / FC / ReLU\n784 → 64',0,118,176,65),
    node('out','类别分数\n64 → 10',0,224,176,65),
    node('prob','softmax\n10 类概率',238,224,176,65)]
cnn_edges=[edge('input','c1'),edge('c1','p1'),edge('p1','c2',[[564,65],[564,118]]),
    edge('c2','p2',[[476,150],[414,150]]),edge('p2','flat',[[238,150],[176,150]]),
    edge('flat','out',[[88,183],[88,224]]),edge('out','prob')]
cnn=graph(cnn_nodes,cnn_edges,[24,80,672,353],'图 7  用于尺寸推导的教学 CNN')

residual=graph([node('x','输入 x',0,40,105,68),node('w1','权重层\n+ ReLU',170,40,130,68),
    node('w2','权重层',365,40,120,68),node('add','相加',540,40,100,68),
    node('out','ReLU\n输出 y',540,162,100,68)],
    [edge('x','w1'),edge('w1','w2'),edge('w2','add'),
     edge('x','add',[[52,40],[52,8],[590,8],[590,40]]),
     edge('add','out',[[590,108],[590,162]])],
    [24,104,672,298],'图 8  带恒等捷径的残差块')

slides=[]
slides.append(page('神经网络入门',[
    t('神经网络入门',[32,145,656,75],46,True,align='center'),
    t('从神经元到深度学习',[32,230,656,55],30,True,align='center'),
    dict(type='table',columns=['信息','内容'],hide_header=True,style='borderless',widths=[.52,.48],
         rows=[dict(id=f'info{i}',cells=[label,'xxx']) for i,label in enumerate(['汇报人','所属单位','汇报时间'])],box=[246,332,228,145])],layout='cover'))
slides.append(page('目录',[
    t('01  神经元与非线性',[55,91,610,48],26,True),
    t('02  多层网络与前向计算',[55,164,610,48],26,True,blue=True),
    t('03  损失、梯度与训练',[55,237,610,48],26,True),
    t('04  卷积网络与残差结构',[55,310,610,48],26,True,blue=True),
    t('05  配置、实验与应用',[55,383,610,48],26,True)]))
slides.append(page('神经网络究竟在学习什么',[
    t('从输入到预测，学习一组可调整的映射',[24,78,672,43],25,True,blue=True),
    para('神经网络由多层可微计算组成。输入可以是像素、测量值或词元表示，输出可以是类别分数或连续数值。训练通过调整权重与偏置，使模型在给定数据上产生更合适的预测。\n'
         '以手写数字识别为例，模型根据像素算出十个类别的分数。训练时，真实数字标签用于计算损失，优化器据此调整参数。推理时，模型只需读取图像即可给出预测。\n'
         '“深度”指多个表示变换的组合。网络能够学习中间特征，但效果仍取决于任务、数据和训练方法。__训练样本上表现好__，并不能直接说明模型在新样本上同样可靠。',[24,129,672,375])]))
slides.append(page('一个神经元：加权、偏置与激活',[
    t('权重控制各输入的影响，偏置调整响应位置',[24,80,672,39],23,True),neuron,
    eq(r'z=\sum_{i=1}^{d}w_i x_i+b,\qquad a=\phi(z)',[24,390,672,64],1),
    t('xᵢ 为输入，wᵢ 与 b 是可学习参数；φ 决定非线性响应。',[24,464,672,43],21)]))

# Native line chart; samples are evaluations of mathematical functions.
xs=np.arange(-3,4,dtype=float)
slides.append(page('为什么需要非线性激活',[
    dict(type='chart',kind='line',categories=[str(int(x)) for x in xs],
         series=[dict(name='Sigmoid',values=(1/(1+np.exp(-xs))).tolist()),dict(name='Tanh',values=np.tanh(xs).tolist()),dict(name='ReLU',values=np.maximum(xs,0).tolist())],
         palette=[BLUE,GREEN,YELLOW],box=[24,98,380,325],caption='图 2  激活函数的采样曲线'),
    bullets(['连续叠加**线性变换**，仍等价于一个线性变换。','激活函数使网络可以表达更复杂的关系。','ReLU 在正区间保持线性，负区间输出零。'],[424,98,272,310],symbol='●',size=21),
    t('图中仅在整数位置采样并连线。Sigmoid 输出在 0 与 1 之间，Tanh 输出在 −1 与 1 之间。',[24,441,672,65],21,panel='gradient')]))
slides.append(page('多层感知机：从连接到表示',[
    t('输入层',[32,83,110,36],20,True),t('隐藏层 1',[205,83,135,36],20,True,blue=True),
    t('隐藏层 2',[390,83,135,36],20,True,blue=True),t('输出层',[579,83,110,36],20,True),mlp,
    t('相邻层之间全连接。每条边对应一个权重，每个隐藏单元都有偏置和激活；输出形式由任务决定。',[24,438,672,70],21)],notes='图含13个单元、36条层间连接；节点编号为层内索引，偏置未单独绘出。'))
slides.append(page('前向计算：沿层逐步变换',[
    t('批量输入使用矩阵运算',[24,84,672,42],24,True,blue=True),
    eq(r'H=\phi(XW_1+b_1),\qquad Z=HW_2+b_2',[24,137,672,85],2),
    bullets(['若 X 的形状为 B × d，则 B 是批量大小，d 是输入维度。','隐藏层宽度为 m 时，W₁ 的形状为 d × m，H 为 B × m。','偏置沿批量维广播；每个样本共享同一组参数。'],[24,239,672,181],symbol='□',size=22),
    t('例：输入 2 维、隐藏层 8 单元、输出 1 维，总参数数为 2×8 + 8 + 8×1 + 1 = **33**。',[24,434,672,72],22,panel='gradient')]))
slides.append(page('损失函数：把预测误差变成目标',[
    t('回归：均方误差',[24,83,672,40],24,True),
    eq(r'L_{\mathrm{MSE}}=\frac{1}{B}\sum_{i=1}^{B}(\hat y_i-y_i)^2',[24,130,672,82],3),
    t('适合连续值预测。较大的误差会被平方项放大，目标量纲和异常值都需要关注。',[24,221,672,67],22),
    t('二分类：交叉熵',[24,301,672,40],24,True,blue=True),
    eq(r'L=-\frac{1}{B}\sum_{i=1}^{B}\left[y_i\log p_i+(1-y_i)\log(1-p_i)\right]',[24,345,672,89],4),
    t('yᵢ ∈ {0,1}，pᵢ 为正类概率。实际计算通常直接从 logits 求损失，以提高数值稳定性。',[24,444,672,64],21)],source=BOOK+'\n'+TORCH))
slides.append(page('反向传播：沿计算图应用链式法则',[
    backprop,
    eq(r'\frac{\partial L}{\partial w}=\frac{\partial L}{\partial a}\frac{\partial a}{\partial z}\frac{\partial z}{\partial w}',[24,417,672,72],5),
    t('反向传播负责求梯度，优化器再使用梯度更新参数。',[24,79,672,40],22,True,blue=True)]))
slides.append(page('梯度下降：参数如何改变',[
    eq(r'\theta_{t+1}=\theta_t-\eta\nabla_{\theta}L(\theta_t)',[24,87,672,91],6),
    t('学习率 η 决定每一步的更新尺度',[24,184,672,43],25,True,blue=True),
    bullets(['梯度指出当前位置损失增长最快的方向，减去梯度是局部下降步骤。','学习率过大可能震荡，过小则更新缓慢；下降不保证每步都泛化得更好。','小批量梯度由一部分样本估计，带有随机性。'],[24,240,672,220],symbol='●',red=True,size=22),
    t('数值例：w = 0.5，梯度 = 0.2，η = 0.1，则新权重为 **0.48**。',[24,468,672,40],21)]))
slides.append(page('训练流程：迭代与评估各司其职',[
    pipeline,t('回路表示更新参数后继续前向计算，每步取一个批次。验证集用于选择配置，最终测试不参与调参。',[24,444,672,64],21)],source=TORCH+'\n'+BOOK))
slides.append(page('泛化：训练误差不是最终答案',[
    dict(type='chart',kind='line',categories=[str(i) for i in range(1,11)],
         series=[dict(name='训练损失',values=[.91,.70,.52,.40,.31,.24,.18,.14,.11,.08]),
                 dict(name='验证损失',values=[.95,.75,.60,.51,.47,.46,.49,.55,.64,.77])],
         palette=[BLUE,YELLOW],box=[24,91,388,327],caption='图 6  过拟合趋势示意'),
    bullets(['训练损失下降，验证损失却开始上升，可能出现**过拟合**。','验证曲线还受样本规模与噪声影响，需要结合任务指标判断。','保存验证表现较好的检查点，而不是默认保留最后一步。'],[430,92,266,320],symbol='○',size=21),
    t('本页数据为教学示意，非实测结果。横轴为训练轮次，纵轴为损失；第 6 轮附近仅用于说明选点。',[24,440,672,66],21,panel='outline')]))
slides.append(page('改善训练：数据、约束与优化',[
    t('降低过拟合风险',[24,85,326,43],24,True,blue=True),
    bullets(['**数据增强**应保留任务标签含义。','**权重衰减**约束参数规模。','**早停**根据验证表现选择训练长度。'],[24,143,326,282],symbol='■',size=22,panel='gradient'),
    t('让优化更稳定',[370,85,326,43],24,True),
    bullets(['输入尺度尽量一致，预处理统计量仅从训练集估计。','合理初始化，并监控损失、梯度和学习率。','一次改变少量配置，保留可复现实验记录。'],[370,143,326,282],symbol='□',size=22),
    t('不同措施解决的问题不同。先定位数据或训练流程错误，再增加模型复杂度。',[24,438,672,70],22)],notes='参考 Deep Learning 第7、8章。'))
slides.append(page('从浅层到深层：组合中间特征',[
    t('深度提供多级变换，不自动保证更好效果',[24,78,672,43],24,True,blue=True),
    para('在图像任务中，多个卷积层可以逐步扩大有效感受野，把局部响应组合成更高层的表示。中间特征由训练目标和数据共同塑造，并不要求人为给每个通道指定一个语义名称。\n'
         '以手写数字为例，浅层单元可能对短线段产生较强响应。后续层能结合更大范围的信息，利用闭环、交叉和笔画位置等线索区分外观相近的数字。\n'
         '增加层数也会改变优化难度、显存占用和推理成本。设计深层模型时，需要同时检查信息传递、梯度传播与任务需求。__更深__是一种结构选择，而不是性能承诺。',[24,129,672,375])]))
slides.append(page('卷积网络：保留空间结构',[
    cnn,t('卷积通过局部连接共享参数，池化降低空间分辨率。本例 3×3 卷积步长1、填充1，2×2 池化步长2。',[24,440,672,68],20)],notes='教学架构为本例设计，不代表已训练模型。尺寸和参数将在后续表格逐层核对。'))

cnn_rows=[['输入','28×28×1','0','单通道图像'],
 ['卷积 1','28×28×8','80','3×3，含偏置'],['ReLU 1','28×28×8','0','逐元素激活'],
 ['池化 1','14×14×8','0','2×2，步长2'],['卷积 2','14×14×16','1,168','3×3，含偏置'],
 ['ReLU 2','14×14×16','0','逐元素激活'],['池化 2','7×7×16','0','2×2，步长2'],
 ['展平','784','0','保留全部元素'],['全连接 1','64','50,240','784×64+64'],
 ['ReLU 3','64','0','逐元素激活'],['全连接 2','10','650','64×10+10'],
 ['softmax','10','0','将分数转为概率']]
slides.append(page('教学 CNN：逐层尺寸与参数',[
    tab(['层 / 操作','输出尺寸','参数量','设置 / 说明'],cnn_rows,[.23,.23,.18,.36],
        '表 1  教学 CNN 的结构与参数',group_size=3)],layout='auto',notes='共12行，自动分页，保留行顺序；总可学习参数80+1168+50240+650=52138。'))
slides.append(page('残差连接：为信息保留直接路径',[
    residual,eq(r'y=\operatorname{ReLU}\left(F(x)+x\right)',[24,411,672,60],7),
    t('相加要求形状一致；若通道或分辨率改变，捷径分支可用投影匹配维度。',[24,474,672,36],20)],source=RESNET))

config_rows=[['任务','二分类 / 回归','先确定标签与输出含义'],
 ['划分','训练 / 验证 / 测试','按人、时间或来源防泄漏'],
 ['预处理','缩放 / 标准化','只用训练集拟合统计量'],
 ['宽度与深度','隐藏单元 / 层数','兼顾容量与计算成本'],
 ['损失函数','交叉熵 / 均方误差','与任务及输出形式匹配'],
 ['优化器','SGD / Adam','记录算法和全部超参数'],
 ['学习率','η 与调度策略','监控震荡和收敛速度'],
 ['批量大小','每步样本数','影响显存与梯度估计'],
 ['训练长度','epoch / 更新步数','明确轮次与步数的区别'],
 ['正则化','衰减 / 增强 / 早停','根据验证表现选择'],
 ['评价指标','准确率 / F1 / MAE','与应用代价保持一致'],
 ['可复现记录','种子 / 版本 / 数据','保留配置、权重和日志']]
slides.append(page('训练配置：从任务到实验记录',[
    tab(['配置项','常见选择','检查要点'],config_rows,[.21,.32,.47],
        '表 2  神经网络实验配置清单',group_size=3)],layout='auto',source=BOOK+'\n'+TORCH))
slides.append(page('实际小实验：学习 XOR',[
    dict(type='chart',kind='line',categories=[str(v['step']) for v in history],
         series=[dict(name='训练交叉熵',values=[v['loss'] for v in history])],palette=[GREEN],
         box=[24,99,390,309],caption='图 9  XOR 实测训练损失'),
    bullets(['输入相同输出 0，输入不同输出 1。','网络为 **2 → 8 → 1**，隐藏层使用 Tanh。','全批量梯度下降，学习率 0.1，训练 4000 步。'],[426,100,270,308],symbol='●',size=21),
    t(f'共 **33** 个参数。固定随机种子17，损失从 {history[0]["loss"]:.4f} 降至 {loss:.4f}。全部4个样本用于训练，不据此宣称泛化能力。',[24,433,672,73],21,panel='gradient')],source='本项目 scripts/make_neural_intro.py；结果保存在 xor_results.json。',notes='NumPy实现链式法则与梯度下降，未依赖外部训练框架。'))
slides.append(page('XOR：逐样本检查预测',[
    tab(['输入 x₁, x₂','标签','正类概率','预测类别'],
        [[f'{int(a)}, {int(b)}',str(int(target)),f'{prob:.6f}',str(int(prob>=.5))] for (a,b),target,prob in zip(X,y[:,0],p[:,0])],
        [.26,.17,.30,.27],'表 3  XOR 实测预测，阈值为 0.5',[24,91,672,400])],source='本项目实际训练结果 xor_results.json。',notes='概率按6位小数展示，原始浮点结果保存JSON；4个样本均为训练样本。'))
slides.append(page('从实验到应用：检查三个环节',[
    t('01  数据是否与目标场景一致',[24,84,672,41],24,True,blue=True),
    t('检查缺失值、异常输入与类别比例。按实体或时间划分时，避免同一来源的信息跨越训练与测试边界。',[24,135,672,76],22),
    t('02  模型是否满足评价与资源要求',[24,228,672,41],24,True),
    t('除了平均指标，还要分析错误样本、类别差异、推理延迟和内存。阈值选择应反映应用中的错误代价。',[24,279,672,76],22,panel='gradient'),
    t('03  部署后是否持续监测',[24,372,672,41],24,True,blue=True),
    t('固定训练时使用的预处理和类别映射。记录模型版本，监测输入分布与错误模式，必要时重新收集数据。',[24,423,672,76],22)]))
slides.append(page('小结：把结构、学习与验证连起来',[
    bullets(['**神经元**组合加权求和、偏置与非线性激活。','**多层网络**学习中间表示，前向计算产生预测。','**损失与反向传播**提供优化方向，优化器执行更新。','**卷积与残差结构**分别利用空间关系与捷径路径。','**可靠评价**依赖独立数据与可复现实验，不能只看训练结果。'],[38,78,644,393],symbol='■',red=True,size=23)]))
slides.append(page('参考文献',[
    t('[1] I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. Cambridge, MA, USA: MIT Press, 2016.',[24,78,672,64],20),
    t('[2] K. He, X. Zhang, S. Ren, and J. Sun, “Deep Residual Learning for Image Recognition,” in Proc. IEEE Conf. Computer Vision and Pattern Recognition, 2016, pp. 770–778.',[24,154,672,92],20),
    t('[3] PyTorch Contributors, “Optimizing Model Parameters,” PyTorch Tutorials. Accessed: Nov. 12, 2026. [Online]. Available: https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html',[24,258,672,120],20)
],source=BOOK+'\n'+RESNET+'\n'+TORCH))
slides.append(page('The End',[
    t('THE END',[48,174,624,100],56,True,align='center'),t('谢谢聆听',[48,292,624,67],34,True,align='center')],layout='end'))

gradients=[dict(colors=['FFFFFF','DEECF8'],kind='linear',angle=20),
           dict(colors=['FFF1CA','FFFFFF'],kind='linear',angle=100),
           dict(colors=['FFFFFF','DCEEDB'],kind='radial',focus=[.25,.35]),
           dict(colors=['E4EEF9','FFFFFF'],kind='linear',angle=145)]
gi=0
for s in slides:
    for b in s['blocks']:
        if b.get('panel')=='gradient':b['gradient']=gradients[gi%len(gradients)];gi+=1

deck=dict(version='1.0',title='神经网络入门——从神经元到深度学习',
          english_title='NEURAL NETWORKS  /  FROM NEURONS TO DEEP LEARNING',language='zh-CN',slides=slides)
(OUT/'deck.json').write_text(json.dumps(deck,ensure_ascii=False,indent=2),encoding='utf-8')
tokens=json.loads((ROOT/'references/design_tokens.json').read_text(encoding='utf-8'))
tokens['type'].update(title=30,body=22,node=16,table=18)
tokens['spacing']['line_height']=1.12
(OUT/'tokens.json').write_text(json.dumps(tokens,ensure_ascii=False,indent=2),encoding='utf-8')

print(f'{len(slides)} source slides; long tables will paginate automatically')
print(f'XOR: initial loss={history[0]["loss"]:.6f}, final loss={loss:.6f}, all 4 training predictions correct')
print(OUT/'deck.json')
