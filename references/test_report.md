# 真实执行记录与功能限制

日期：2026-11-11。环境：Windows、Python 3.11、PowerPoint 2013，本项目独立 `.venv`。此记录区分真实 Office 集成、程序测试与人工视觉检查，不把模拟渲染器当作集成通过。

## 已执行

2026-11-12 提交前复核。在不含原有 `artifacts/`、`material/` 和缓存的源码副本中，复用本机锁定环境执行 pytest，27 项通过。主环境与 Drawlib 环境的已启用版本均匹配各自锁文件，`pip check` 通过。

README 示例通过 PowerPoint 严格构建，实际渲染 19 页。完整性脚本核对了 45 行表格、正文、LaTeX、原生图表及预览页数。Transformer 脚本在源码副本中独立生成因果掩码并通过 17 页严格渲染。Drawlib 架构示例和四张 SVG/PNG 科研图示例均成功生成。

2026-11-11 修订补充：混排页、渐变/边框文本框、局部加粗、黑体标题和满高续表已实现。pytest 现为26项通过。Transformer修订版为14页，已实际渲染。另用15行分组数据生成三页满高续表进行实际渲染检查。原有19页示例的记录属于此前版本。

| 验证 | 实际结果 | 证据 |
|---|---|---|
| 五套原始 PPT | 73+69+60+115+131=448 页全部转换、实际渲染并提取对象结构 | `reference_inventory.json`；本地 `artifacts/reference-analysis/` |
| 风格观察 | 24 张覆盖全部页面的联系表，另放大代表页面；非448页逐字校对 | `style_guide.md` |
| pytest | 24 passed，1 条上游弃用警告 | `artifacts/pytest.xml` |
| Skill 元数据 | skill-creator 的 quick_validate.py 输出 Skill is valid! | `SKILL.md`；同时对照 [Agent Skills 规范](https://agentskills.io/specification) |
| 依赖一致性 | pip check 输出 No broken requirements found | `requirements.lock` 已实际安装 |
| 源码启动 | 移除项目的可编辑安装后，Windows 初始化脚本通过。从项目外调用源码 CLI，成功验证输入并生成19页PPTX | `scripts/bootstrap.ps1` 和 `scripts/scientific_ppt.py`，本项使用 `--no-render` |
| 通用参考分析 CLI | 独立一页 PPTX 的对象分析和 PowerPoint 渲染成功 | `artifacts/analyzer-smoke/inventory.json` |
| 综合示例 | 11 个语义页面自动展开为19页，真实PDF19页、PNG19张 | `artifacts/demo/` |
| 最终文件完整性 | PPTX内45行表格与源数据逐单元格同序相等；8页重复表头；正文无损；LaTeX保留；10条原生连接线及1个原生图表和嵌入工作簿 | `artifacts/demo/integrity_report.json` |

## 测试覆盖

`test_core.py` 覆盖图文混排、多图、超宽/超高图片、正文拆页与字节保真、75行分组表格分页、超大行拒绝及数据Schema约束。`test_graphics.py` 覆盖求和、积分、矩阵、分段和上下标、未知公式命令拒绝、循环图与反馈边、原生图表和公式原文。

`test_pipeline.py` 覆盖缺失实际渲染器的明确降级、最多三次尝试的修复上限、重叠检查、Markdown输入、只清理先前索引拥有的预览并保护目录外文件。`test_reference_analysis.py` 覆盖新输入的结构分析、明确标记未渲染。缺依赖与超限修复使用测试替身，未冒充真实 Office 集成。

测试命令（从项目根目录）：

```powershell
.venv/Scripts/python -m pytest -q --junitxml=artifacts/pytest.xml
.venv/Scripts/python scripts/scientific_ppt.py build examples/demo.json --output artifacts/demo --backend powerpoint --strict
.venv/Scripts/python scripts/verify_demo.py
.venv/Scripts/python -m pip check
```

## 实际视觉修复

已修复：主题继承的形状阴影、图注距离过大、长文续页孤行、表格边框XML顺序、图表过重网格线、中文行首标点和旧预览残留。最终自动修复使用2次尝试，测量安全系数从1.12提升至1.3216，标题32→30pt；正文24pt、表格18pt保持不变。最终自动问题列表为空。中文禁则采用语言标记与非悬挂标点，避免把伸出文本框的标点误算为成功。

Agent实际检查所有19页预览，并在最后中文换行调整后再次检查联系表与页面。独立视觉记录及最终文件SHA256见 `artifacts/demo/visual_review.md`。自动报告仍保留 `rendered_needs_visual_review`，不把自动检查等同人工通过。

与参考保持的设计语言：4:3、酒红标题带、白标题、宋体正文、西文衬线字体、蓝色强调、浅青表头、浅色模块与细线。横纹背景被明确简化为纯浅灰。第16页续表只有3行，保留整组；第17–18页是长文本压力案例，比常规讲演内容密集，但未靠缩小字体容纳。参考中局部遮挡和极小文字未复现。

## 尚未解决及未验证范围

- LibreOffice 后端已实现检测、独立profile和失败报告，但本机未安装，**未做其真实集成验收**；Linux/macOS、其他Python版本和Office版本未真实验收。
- 缺渲染器仍可生成PPTX，但不能宣称通过视觉验收。自动检查是几何、字体测量和基础像素检查，不是通用视觉理解模型。
- 语义规划、论文理解和证据选择由调用Skill的Agent完成；CLI `plan` 只是确定性Markdown导入。PDF/DOCX不提供OCR或复杂图表语义恢复。
- 公式为清晰PNG，保留LaTeX/MathML/SVG，**不是可直接编辑的Office数学方程**；不保证全部LaTeX宏覆盖，不调用完整TeX引擎。
- 跳层边、反馈边及复杂网络可能需要Agent调整位置；连接线不保证在用户移动节点后自动重新路由。超密图和单行超大表格明确报错，需上层重新组织内容。
- 字体不随仓库分发。替换字体可能缺字或改变换行；必须重新渲染，不能保证跨平台视觉完全相同。
- 自动抽取的新参考token仅是候选，颜色语义、留白和布局规律仍需Agent根据实际页面判断。原参考部分字体/OLE细节未精确确认。
- pytest有一条ziamath内部 `importlib.resources.path` 弃用警告，当前功能通过，未来升级需重新测试。

代码采用MIT；原参考教材、商业字体不因此获得再分发授权。本地参考渲染证据和虚拟环境已排除Git。没有执行GitHub上传。
# 2026-11-12 Transformer v3 修订验证

- pytest实际执行：27 passed，1条ziamath上游弃用警告；`artifacts/pytest.xml`。
- `artifacts/my-transformer-v3/presentation.pptx`：17页，PowerPoint实际渲染17页，逐页人工检查，自动issues为空。完整记录见该目录的`visual_review.md`。
- `artifacts/table-natural-qa/`：3页实际渲染并查看。15行按6/6/3分组，表头重复，续页无表题和续页脚注，行高自然，最后一页留白。
- 新测试覆盖话题不跨源页合并、自然行高、无续页标注、透明横条式原生表格、蓝字/下划线、放射渐变与原生项目符号。
- 早期“表格填满高度”记录仅描述历史版本，已由最新自然行高策略替换。

# 神经网络入门成品：2026-11-12

`artifacts/neural-network-intro/`：26页真实渲染，所有页面逐页查看；两轮修订后最终自动issues为空。目录为竖排列表，首页/end页英文居中。两组12行长表各分页为6+6行，续页无表题，原始数据逐单元格守恒。

`scripts/verify_neural_intro.py`实际运行通过，核验页数、居中页眉、列表目录、跨页表格、原生图表/图节点及保存权重重算的XOR结果。pytest仍为27 passed。详细记录及限制见成品目录的`visual_review.md`与`verification.json`。

本轮排版修订重新渲染26页并复核改动页。第16、19页表格撑满正文区，第17、20页保留自然行高。验证脚本确认18pt页码、首尾页无页码、封面表格居中且只有下边线。pytest 27项通过。

后续修订去掉封面信息表边框，上移首尾页页眉线，两页叙述均新增手写数字识别示例，31个流程图方框改为白底。26页重新渲染，自动检查无问题，改动页通过目视复核，pytest 27项通过。

