# scientific-ppt

[English](README.en.md)

基于参考PPT设计语言的通用 Agent Skill。Agent负责阅读材料和规划内容，Python负责可编辑PPTX生成、图文布局、公式、表格分页与实际渲染检查。默认风格来自5份教学演示的448页分析：4:3、酒红标题带、浅底、宋体与有限强调色。内容和学科不写死。

## 快速开始

要求Python 3.11+。所有依赖安装在本项目`.venv`中。

```powershell
# Windows：在本仓库根目录运行
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.lock
.venv/Scripts/python scripts/scientific_ppt.py doctor
.venv/Scripts/python scripts/scientific_ppt.py build examples/demo.json --output artifacts/my-demo --strict
```

Linux/macOS把解释器路径换为`.venv/bin/python`。初始环境、可选Office依赖与锁定策略见[安装说明](references/installation.md)。实际渲染需要本机PowerPoint或LibreOffice之一；生成PPTX本身不需要Office、draw.io或TeX。

将完整的 Skill 源码目录复制到 Agent 的 skills 路径，目录名为 `scientific-ppt`。按上面的步骤安装依赖后，直接运行 `scripts/scientific_ppt.py`。示例请求：

> 使用 scientific-ppt，根据这篇论文面向研究生制作方法与实验汇报。保持参考风格，保留数据来源，允许按可读性调整页数，并检查全部渲染页面。

## 交付与能力

- 运行上方示例命令，在本地 `artifacts/my-demo/` 生成 PPTX、PDF、逐页预览和 QA 报告。示例使用合成数据，整个 `artifacts/` 目录由 Git 忽略。
- 原生文本、形状、箭头、表格和嵌入数据的柱形/折线图。
- 图片EXIF校正、等比适配、受限裁切和混合比例布局。
- LaTeX矩阵、求和、积分、分段与上下标，保留源LaTeX、MathML、SVG和清晰PNG。
- 长文本均衡拆页、可变行高表格、续表重复表头、行分组保护、行ID与数据守恒。
- PowerPoint/LibreOffice渲染、几何检查、PowerPoint实际文字测量、有限重排与明确的未解决问题报告。

```powershell
.venv/Scripts/python scripts/scientific_ppt.py extract paper.pdf --output artifacts/paper.txt
.venv/Scripts/python scripts/scientific_ppt.py plan outline.md --output artifacts/outline.json
.venv/Scripts/python scripts/scientific_ppt.py validate examples/demo.json
.venv/Scripts/python -m pytest
```

`plan`只是确定性提纲导入。智能摘要、研究和语义叙事由调用Skill的Agent完成；没有隐藏LLM调用或API密钥要求。

## 设计与开发

- [参考分析](references/style_guide.md)、[可执行tokens](references/design_tokens.json)、[架构](references/architecture.md)
- [页面Schema](references/deck.schema.json)、[字段和布局说明](references/schema_usage.md)
- [图形与公式](references/graphics.md)、[视觉验收](references/visual_qa.md)、[真实测试记录](references/test_report.md)

源码在`src/scientific_ppt/`，脚本在`scripts/`，pytest在`tests/`。`references/`存放详细规范，SKILL.md只负责触发和工作流。示例输入在`examples/`。

## 已知限制

自动QA不是视觉模型，不能证明科学正确性或美学质量。公式当前以高分辨率图片插入，保留矢量与LaTeX源，但不是Office原生方程。图中复杂回路、跳层连接和边标签仍需人工检查。极宽表格、单行高度超过一页或过密网络会要求显式重组，不丢弃数据。

无渲染器时输出状态为`unverified`；`--strict`返回非零。字体不随项目分发，跨平台字体替换会改变外观；本次验证环境为Windows、Python 3.11、PowerPoint 2013。扫描PDF没有自动OCR，DOCX/PDF提取不能替代对图片和复杂表格的阅读。

## 发布与许可

代码采用[MIT许可证](LICENSE)。发布前按[许可与第三方说明](THIRD_PARTY_NOTICES.md)确认素材权利。参考教材的转换副本和预览默认被Git忽略；不把素材版权随代码许可证一并授权。

`.venv/`、缓存、临时尝试和参考副本不提交。保留示例最终PPTX、PDF、预览、输入JSON与验收记录。项目不会自动上传GitHub。
