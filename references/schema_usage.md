# Schema与布局

JSON Schema是输入合同。所有距离为pt，设计token默认720×540pt。使用JSON的数字类型定义图表值，使用字符串定义表格原始单元格。不存在强制每页固定模板。

```json
{
  "version": "1.0",
  "title": "Study design",
  "slides": [{
    "title": "Observation pipeline",
    "notes": "Source: supplied protocol, section 2",
    "blocks": [{"type": "text", "text": "Retain calibration records."}]
  }]
}
```

内容块：

| type | 必需字段 | 可选字段 |
|---|---|---|
| text | text | heading, bold, emphasis(normal/blue/primary) |
| image | path | caption, alt, fit(contain/cover), allow_crop |
| equation | latex | caption |
| table | columns, rows | widths(正数比例，总和1), caption |
| diagram | nodes, edges | direction(LR/TB), caption |
| chart | kind(bar/line), categories, series | y_title, caption |

全部块可以设置`id`、`source`。图片路径相对于**输入JSON目录**。表格行格式：`{"id":"R1","cells":["A","1.20"],"group":"G1"}`。无行ID、重复ID或列数不符均拒绝。

图节点：`{"id":"a","label":"Acquisition","kind":"process","color":"cyan"}`。形状还有decision/terminal/data/neuron；颜色还有green/yellow/white。边：`{"from":"a","to":"b","label":"yes","feedback":false}`。需要指定位置时，所有节点使用`position:[0..1,0..1]`，坐标以可用图区域归一化。自动DAG布局不从文字猜测关系。

图表series：`[{"name":"Measured","values":[1.2,2.1]}]`，每条序列长度必须与categories相等。

`layout`是候选布局提示：auto/stack/split/gallery/figure。适配器有最终可读性约束：一个图加短文可分栏，宽图改上下排布，多图选择面积利用率更好的规则网格或非对称组合；专用图、表、图表与文本解释目前可能分成不同页。`resolved_layout.json`是执行后的权威坐标，可用于定位问题，但不应作为新的输入Schema。

使用 `layout: composed` 可将图、表、公式与正文放在同页。每个块提供以 pt 为单位的 `box: [x,y,width,height]`，块之间应保留清晰间距。`cover` 和 `end` 同样使用显式区域并省略常规标题带。固定区域无法容纳的内容须调整布局。大型表格使用普通布局以自动分页。

文本支持 `font_size`、`heading`、`align` 和 `panel: outline|gradient`，以及 `**关键词**` 加粗。图节点可使用相对图区域的 `box`，边的 `route` 定义同坐标系的折线路径。显式节点区域从图块左侧加8pt、顶部加20pt处起算。

表头和数据单元格统一加粗。表格跨页时，仍有后续数据的页面将数据行扩展至正文区底边，最后一页和单页表格默认使用自然行高。跨页只重复表头，续页省略表题与续页脚注，表格下方留空。`fill_height: true` 为显式填满全部表格页的兼容选项。图题居中置于图下，首次表题居中置于表上，均为黑色。公式的 `caption` 可填 `(1)` 这样的编号，置于右侧。说明性图题居中置于公式下方。

首页信息表使用 `hide_header: true, style: "borderless"`，仍需 `columns` 定义列数。单元格透明且无框线，首列右对齐，值列左对齐。用较窄的 `box` 将表格置于页面水平中心。`english_title` 是整套演示的英文题目，用于首页与结束页的细线页眉。

内容页的正文、分点和提示框默认加粗。文献条目等需用常规字重的文本块可设 `bold: false`。需要定位重点时，可用 `==蓝字==` 或 `@@酒红字@@` 标注少量关键词组。数字、单独字母和符号使用正文色。颜色取自设计参数的 `blue` 和 `primary`。兼容 `**加粗**` 和 `__下划线__`（标记不嵌套）。`first_line_indent: 2` 表示首行缩进两字号宽，`paragraph_space: 18` 表示段后18pt。换行分隔段落。项目列表用 `bullet: {"symbol":"□","color":"A50021"}`，支持 ●、○、■、□，不要同时写文字项目符号。

浅色框例子：`panel: "gradient", gradient: {"colors":["FFFFFF","DDF0DE"],"kind":"radial","focus":[0.25,0.3]}`。线性渐变使用 `kind: "linear", angle: 135`，放射中心取0至1的相对坐标。优先用于正文分组，标题和大部分正文仍可无框。

图表可设 `palette: ["237DB5","239B73","E8B52B"]`；单系列柱形图设置 `vary_categories: true` 按类别着色。颜色需要有辨识度，浅色背景与数据颜色分别选择。

执行器不支持合并表格单元格、跨页单行切分、自动拆列、3D原生模型或任意动画。

运行时直接读取 `references/` 下的默认设计参数和 Schema。修改 Schema 结构时，编辑并运行 `scripts/create_schema.py`。使用 `--tokens` 加载自定义设计参数。
