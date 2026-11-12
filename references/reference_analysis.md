# 新参考文件的分析流程

本项目已分析原始5份PPT。后续用户提供新的参考时，先建立文件清单和SHA256；不把旧风格直接套到新材料。

1. PPTX可用python-pptx和zip/XML读结构，但还要实际渲染。旧PPT需PowerPoint或LibreOffice转换副本，不能仅改后缀。
   通用入口：`.venv/Scripts/python scripts/scientific_ppt.py analyze path/to/references --output artifacts/reference-study`。支持单文件或目录。输出每页对象、字体/颜色频次、可见像素配色、实际预览和联系表。`token_candidates.json`只自动采用实测画布，其余明确标记为待Agent审阅的默认值；没有伪装为自动精确复刻。
2. 本次旧PPT转换命令（项目根目录）：
   ```powershell
   powershell -NoProfile -File scripts/analyze_legacy.ps1 -Source ../material -Output artifacts/reference-analysis
   .venv/Scripts/python scripts/inspect_references.py
   ```
   `inspect_references.py`目前按本项目目录和文件名读取材料，不是通用导入CLI。复用它前修改根路径映射；对象提取含组内局部坐标，不能把它们误当作绝对坐标。
3. 检查全部页的联系表并对每类代表页放大审阅。记录页数、比例、通栏/网格、字号、CJK与西文字体、强调色、母版、图/表/公式形式和异常。
4. 色值频次不能直接当作视觉主色。结合渲染判断；继承样式、嵌入OLE、位图中文字和动画需单独说明限制。
5. 写入style_guide，并将可执行参数放进tokens。区分“测得”“推断”“设计调整”。不要复制来源身份标识和图片作为通用Skill素材。
6. 每次更改tokens都重新生成代表性样例并视觉复核。
