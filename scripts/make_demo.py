"""Reproducible, synthetic environmental sensing example; no reference content reused."""
from pathlib import Path
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


def main():
    out=ROOT/'tests'/'fixtures'/'demo';assets=out/'assets';assets.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
    rng=np.random.default_rng(42)
    x=np.linspace(0,24,120)
    fig,ax=plt.subplots(figsize=(7,4));ax.plot(x,20+3*np.sin(x/24*2*np.pi),color='#A50021',label='Reference');ax.scatter(x[::4],20+3*np.sin(x[::4]/24*2*np.pi)+rng.normal(0,.5,len(x[::4])),s=15,color='#0000CC',label='Sensor');ax.set(xlabel='Time (h)',ylabel='Temperature (C)');ax.legend(frameon=False);fig.tight_layout();fig.savefig(assets/'signal.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(3,6));im=ax.imshow(rng.normal(size=(20,8)),cmap='YlGnBu');ax.set(xlabel='Channel',ylabel='Sample');fig.colorbar(im,ax=ax,shrink=.6);fig.tight_layout();fig.savefig(assets/'heatmap.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,3));ax.hist(rng.normal(0,.45,400),bins=20,color='#A50021',alpha=.8);ax.set(xlabel='Residual (C)',ylabel='Count');fig.tight_layout();fig.savefig(assets/'residuals.png',dpi=180);plt.close(fig)
    def text(s,**kw):return {'type':'text','text':s,**kw}
    def image(name,cap):return {'type':'image','path':'assets/'+name+'.png','caption':cap,'alt':cap}
    def slide(title,blocks,**kw):return {'title':title,'blocks':blocks,**kw}
    nodes=[{'id':k,'label':label,'color':c} for k,label,c in [('input','观测数据','cyan'),('clean','质量控制','green'),('model','状态估计','yellow'),('output','结果解释','cyan')]]
    pipeline={'type':'diagram','nodes':nodes,'edges':[{'from':'input','to':'clean'},{'from':'clean','to':'model'},{'from':'model','to':'output'}],'caption':'观测、处理、推断与解释形成可追溯的分析流程'}
    architecture={'type':'diagram','nodes':[{'id':k,'label':v,'color':c} for k,v,c in [('a','温度通道','cyan'),('b','湿度通道','cyan'),('c','数据对齐','green'),('d','特征提取','yellow'),('e','不确定性','yellow'),('f','状态融合','green'),('g','研究报告','cyan')]],'edges':[{'from':a,'to':b} for a,b in [('a','c'),('b','c'),('c','d'),('c','e'),('d','f'),('e','f'),('f','g')]],'caption':'并行观测与双分支分析；模块和连线均可编辑'}
    longtext=('观测记录应包含采样位置、时间、设备标识和校准信息。原始数据与处理结果分别保存，任何修订都应能够追溯到具体操作。'
      '不同通道的时间基准可能存在偏差，在比较信号之前，需要先明确对齐规则以及插值是否改变了观测的统计特征。'
      '缺失记录不能简单地视为零值。应区分通信中断、传感器故障和研究设计造成的缺失，并保留处理依据。'
      '误差分析应说明随机误差与系统偏差的不同来源。仅报告一个平均值不足以判断模型是否适合当前观测条件。'
      '数据分组应对应实际研究问题，例如不同设备、采样区域或观测时段。比较组之间应尽可能采用一致的单位与处理流程。'
      '模型选择需要结合解释目标。若关注机制，应检查变量关系是否有科学依据；若关注预测，应使用独立数据检验泛化表现。'
      '验证集不应参与参数选择。评估结果应说明样本范围、指标定义和异常值处理方式，避免把特定条件下的结果推广到所有场景。'
      '研究报告应同时展示支持结论的证据和主要限制。对于尚未验证的解释，应明确标记为假设，并提出能够检验该假设的后续实验。'
      '复现材料应包含输入数据版本、参数设置、随机种子和运行环境。公开数据前还应确认其授权范围，并去除不应公开的信息。'
      '最终图表应能追溯到相应的分析输出。更改数据、参数或模型之后，应重新生成图表并检查标题、单位和图注是否仍然准确。')
    rows=[{'id':f'R{i:03}','cells':[f'S{i:02}',f'{18+i*.13:.2f}',f'{.2+(i%5)*.03:.2f}','A' if i%2 else 'B'],'group':f'G{(i-1)//3}'} for i in range(1,46)]
    deck={'version':'1.0','title':'多源环境观测与不确定性分析','author':'scientific-ppt example','language':'zh-CN','slides':[
        slide('多源环境观测与不确定性分析',[text('科研与技术汇报示例',emphasis='blue'),text('从观测设计到可复核结果'),text('本演示的数据、曲线和观测记录均为合成示例，不代表真实实验结论。')]),
        slide('研究问题与观测设计',[text('研究问题：不同通道的观测误差如何影响状态估计？',emphasis='blue'),text('保留采样时间和校准记录，建立可比较的数据基础。'),image('signal','图1　合成温度观测与参考信号')]),
        slide('不同视角下的观测特征',[image('heatmap','通道与样本分布（合成数据）'),image('signal','时序变化（合成数据）'),image('residuals','残差分布（合成数据）')]),
        slide('多阶段分析流程',[pipeline]),
        slide('多源分析系统结构',[architecture]),
        slide('状态估计的数学表达',[{'type':'equation','latex':r'\hat{x}=\frac{\sum_{i=1}^{n}w_i x_i}{\sum_{i=1}^{n}w_i}','caption':'加权估计量；权重需由研究假设或观测误差确定'},{'type':'equation','latex':r'\Sigma=\begin{bmatrix}\sigma_1^2&\rho\sigma_1\sigma_2\\\rho\sigma_1\sigma_2&\sigma_2^2\end{bmatrix}','caption':'协方差矩阵保留通道之间的相关性'}]),
        slide('连续量与分段规则',[{'type':'equation','latex':r'E[X]=\int_{-\infty}^{\infty}x\,p(x)\,dx','caption':'期望的连续积分表达'},{'type':'equation','latex':r'q(x)=\begin{cases}1&|x|\le\tau\\0&|x|>\tau\end{cases}','caption':'示意质量门限规则，不作为实际实验推荐阈值'}]),
        slide('方法比较与不确定性',[{'type':'chart','kind':'bar','categories':['A','B','C'],'series':[{'name':'Baseline','values':[.85,.7,.62]},{'name':'Combined','values':[.63,.55,.49]}],'y_title':'Error (synthetic units)','caption':'图2　合成方法比较；数据仅演示图表能力，不支持实际效果结论'}]),
        slide('观测记录与分组结果',[{'type':'table','columns':['样本','观测值','标准差','通道'],'widths':[.22,.28,.28,.22],'rows':rows,'caption':'合成数据；每组三行，续页重复表头，行ID保存在备注中'}]),
        slide('复核与可重复性记录',[text(longtext)]),
        slide('结论与后续研究',[text('观测质量、模型假设和误差结构共同决定解释范围。',emphasis='blue'),text('真实研究应使用经过核验的数据，并将来源、单位和不确定性与结果一起报告。'),text('后续工作：设计独立验证实验，检查模型在不同条件下的适用性。')])
    ]}
    (out/'demo.json').write_text(json.dumps(deck,ensure_ascii=False,indent=2),encoding='utf-8')
    print(out/'demo.json')

if __name__=='__main__':main()
