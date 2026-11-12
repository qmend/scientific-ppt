# 架构与技术选型

阶段一完成后确定的架构。Python 3.11+，所有执行使用项目`.venv`。Agent负责语义规划，Python负责验证、测量、布局和生成，二者通过版本化JSON Schema隔离。无需在线模型API，不把某一学科知识写进引擎。

`输入材料 → Agent编排或Markdown确定性导入 → deck.schema.json → planner → layout → pptx → renderer → quality → bounded repair`

| 模块 | 职责 |
|---|---|
| schema / models | 严格验证内容块、图边、行列数据、资源引用 |
| ingest / planner | 提取md/txt/pdf/docx文字、保留来源；按测量高度拆文本/表格；输入不可变 |
| typography / layout | 字体检测、字符测量、布局候选评分、图片比例适配 |
| images | EXIF、contain/受限cover、SVG转换 |
| tables | 可变行高、连续组保护、重复表头、数据守恒 |
| diagrams | 原生节点、连接线、层级DAG布局、显式位置与回路 |
| equations | LaTeX → MathML → SVG paths → PNG，保存源式 |
| pptx_writer | 原生文本、形状、表格、图表、备注、行ID可追溯 |
| rendering | PowerPoint COM或LibreOffice → PDF → PDFium PNG；超时隔离 |
| quality / pipeline | 边界、文本测量、重叠、图片比例、密度、渲染覆盖率；有限重排 |

## 选择理由和限制

- 用户明确要求Python，因此采用[python-pptx](https://python-pptx.readthedocs.io/en/latest/user/intro.html)作为主要可编辑生成库，不引入Node运行时。
- [Ziamath](https://ziamath.readthedocs.io/en/stable/usage.html)与latex2mathml支持常见数学排版；[resvg-py](https://resvg-py.readthedocs.io/en/latest/usage.html)把SVG光栅化。无需TeX完整发行版，不执行LaTeX shell命令。不是任意LaTeX包兼容器，未知命令应报错，不静默输出原代码冒充公式。
- PPTX没有通用纯Python高保真渲染器。PowerPoint是Windows可选后端；LibreOffice是跨平台可选后端。无两者时仍生成PPTX和结构报告，但状态是`unverified`，不以重绘场景图冒充PPT实际预览。
- PDFium用于导出PDF的逐页预览，pypdf用于输入文字提取，避免给项目增加PyMuPDF商业/AGPL许可选择的负担。
- 字体不捆绑；字体回退和缺字风险必须进入报告。
- 自动QA是几何与像素启发式，不能判断科学正确性、所有连线语义或美学质量。Agent必须审阅实际渲染后再交付。
- 表格数据守恒为硬约束；不能容纳的一整行、太宽的表格、过密图应明确报错并提示Agent重组，不得丢数据或无限缩字。

## 分阶段验收

先跑图文、比例、分页测试并生成初稿，再加入图形/公式验证，随后实际渲染、审阅、有限修复，最后执行完整 pytest 并从源码运行 CLI。测试记录只描述真实运行结果。
