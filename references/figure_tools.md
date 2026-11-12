# 科研图选库规则

按每张图的任务、原始数据和交付格式选工具。跨学科汇报可以在同一套 PPT 里混用。例如，医学影像模型架构用 Drawlib，模型评估曲线用 Matplotlib，临床队列生存曲线用 lifelines。

| 图的用途 | 首选或可选工具 | 选择依据 |
|---|---|---|
| 计算机、人工智能、深度学习、智能运维的架构或流程 | [Drawlib](https://www.drawlib.com/en/06_diagrams/overview.html) | 默认用于数据流、模型模块、训练与推理、告警闭环等示意图。可复用图标、分区、折线路由与白底节点样式。 |
| 可编辑模块和连线 | 原生 PPT `diagram` | 按用户要求在 PowerPoint 中保留独立模块与连线。插入整张 SVG 时，它作为单个图片对象。 |
| 通用统计图、实验曲线、频谱、等值线和矢量场 | [Matplotlib](https://matplotlib.org/stable/plot_types/index.html) 或原生 PPT 图表 | 使用输入数据和正确的轴、单位、误差定义。需在 PPT 内改数据时优先支持对应类型的原生图表。 |
| 数学函数或符号推导 | [SymPy](https://docs.sympy.org/latest/modules/plotting.html) + Matplotlib，公式用现有 LaTeX 链 | 用表达式定义函数。检查定义域、间断点与采样分辨率。 |
| 物理模拟和电路 | [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html) + Matplotlib，电路用 [Schemdraw](https://schemdraw.readthedocs.io/en/stable/) | 模拟参数、单位和初边值来自用户或标注的教学例子。电路使用约定符号。 |
| 化学分子结构 | [RDKit](https://www.rdkit.org/docs/source/rdkit.Chem.Draw.html) | 从核对过的结构数据生成二维分子图，检查键型、电荷与立体化学。 |
| 生物和医学数据图 | [Biopython Phylo](https://biopython.org/wiki/Phylo)、[lifelines](https://lifelines.readthedocs.io/en/stable/fitters/univariate/KaplanMeierFitter.html)、Matplotlib | 分别用于进化树、生存曲线与常规数据可视化。检查树的分支定义、生存数据的删失标记和图注。 |
| 地理地图 | [GeoPandas](https://geopandas.org/en/stable/docs/user_guide/mapping.html) + [Cartopy](https://cartopy.readthedocs.io/stable/) | 前者处理矢量地理数据，后者负责地图投影。保留坐标参考系、单位和数据来源。 |

## 按需执行

1. 根据实际图形要求选工具，明确输入来源、输出格式和编辑要求。学科名称仅供初选。例如深度学习的张量流用 Drawlib，损失曲线用 Matplotlib。
2. 先检测可选库是否可用。例如在选定解释器内用 `importlib.util.find_spec("drawlib")`。只有选中的绘图脚本导入对应库。Drawlib 的独立环境见[安装说明](installation.md#可选绘图库)，其它工具按需核对官方安装指引与版本。
3. 生成图及其可复现源码。用 JSON 的 `image` 块放置 SVG 或 PNG，需要原生编辑时用 `diagram` 或 `chart` 块。Drawlib 示例会将中文和图标转为矢量路径，并将 SVG 画布尺寸改为像素数值，以兼容项目预览链。
4. 计算机示意图在 Drawlib 不可用时可使用原生 PPT `diagram` 块。数据图按图表类型使用上表的工具。专用科学图优先使用用户提供的原图或经验证的同类工具。记录所用工具、版本和必要的降级。
5. 架构图、流程图和 Pipeline 的每个节点都配一个含义相符的图标。同一张图统一图标库、尺寸和摆放位置，相同功能沿用同一个图标。例如用 Phosphor 波形标识卷积、芯片标识扫描、数据库标识缓存。图标与文字标签并用，布置在节点内部并给连线端点留出空间。
6. 在幻灯片的实际尺寸下检查图例、图标、连线、裁切、字体和数值含义。按需保留源文件、数据和参数。

选库发生在 Agent 的图件准备阶段。当前已跑通 Drawlib 示例、通用 SVG 入稿与原生 PPT 工作流。表中的其它专业工具是按需选项，使用时逐项验证。
