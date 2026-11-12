"""Draw a conceptual ChatGPT web architecture. Requires drawlib 0.3.9."""

import argparse
import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "drawlib-matplotlib"))

from drawlib.canvas import clear, save, setup
from drawlib.fonts import FontFile
from drawlib.icons import phosphor
from drawlib.lines import lines
from drawlib.shapes import circle, rectangle
from drawlib.styles import Styles
from drawlib.text import text
from matplotlib import rc_context


WIDTH, HEIGHT = 160, 88
INK = "#162940"
MUTED = "#50617A"
STROKE = "#C8D4E3"
WHITE = "#FFFFFF"
BLUE = "#245A91"
TEAL = "#08796D"
PURPLE = "#6B4F96"
BLUE_TINT = "#EDF4FC"
TEAL_TINT = "#E7F4F1"
PURPLE_TINT = "#F1ECF8"


def panel(x, y, width, height, fill, border=STROKE, radius=1.6):
    rectangle(
        (x + width / 2, y + height / 2), width, height,
        style=Styles.Neutral.patch(
            shape_fill_color=fill, shape_line_color=border, shape_line_width=1,
            shape_r=radius,
        ),
    )


def label(x, y, value, font, size=15, color=INK):
    text(
        (x, y), value,
        style=Styles.Neutral.patch(
            text_size=size, text_font=font, text_color=color, halign="left", valign="center",
        ),
    )


def icon(glyph, x, y, size, color):
    glyph((x, y), size, style=Styles.Neutral.patch(icon_color=color, icon_style="regular"))


def connector(points, color, arrow="->", *, dashed=False, width=2.1):
    lines(
        points,
        style=Styles.Neutral.patch(
            line_color=color, line_width=width, line_style="dashed" if dashed else "solid",
            line_arrow_head_fill=True, line_arrow_head_scale=12,
        ),
        arrow_head=arrow,
    )


def node(x, y, width, height, title, detail, glyph, color, tint, regular, bold):
    panel(x, y, width, height, WHITE)
    panel(x+1.2, y+(height-5.4)/2, 5.4, 5.4, tint, tint, 1.1)
    icon(glyph, x+3.9, y+height/2, 3.5, color)
    label(x+7.8, y+height*.67, title, bold, size=14.5)
    label(x+7.8, y+height*.29, detail, regular, size=10.2, color=MUTED)


def build(output, font_path, bold_path):
    output.mkdir(parents=True, exist_ok=True)
    regular = FontFile(str(font_path.resolve()))
    bold = FontFile(str(bold_path.resolve()))
    clear()
    setup(width=WIDTH, height=HEIGHT, dpi=144, background_color="#F7F9FC")

    panel(0, 72, WIDTH, 16, "#142942", "#142942", 0)
    label(5, 82, "ChatGPT 网页技术架构", bold, size=32, color=WHITE)
    label(5, 76.2, "一次对话如何经过浏览器、模型与工具，再流式返回", regular, size=15, color="#D8E6F6")
    panel(133, 79.2, 22, 4.8, "#253D58", "#253D58", 1.3)
    label(136, 81.6, "概念架构示意", regular, size=13, color="#D8E6F6")

    # Three system boundaries. The pale fills belong to the groups; nodes are white.
    panel(4, 23, 35, 44.5, BLUE_TINT)
    panel(44, 23, 64, 44.5, "#EFF3F8")
    panel(114, 23, 42, 44.5, PURPLE_TINT)
    for x, title, glyph, color in (
        (6, "浏览器", phosphor.browser, BLUE),
        (46, "对话服务", phosphor.tree_structure, BLUE),
        (116, "模型与工具", phosphor.cpu, PURPLE),
    ):
        icon(glyph, x+1.6, 62.8, 3.25, color)
        label(x+4.5, 62.8, title, bold, size=19, color=color)

    # Draw connections before content so edges end at the cards.
    connector([(39, 51.5), (47, 51.5)], BLUE)
    connector([(73, 51.5), (78, 51.5)], BLUE)
    connector([(60, 37.5), (60, 42), (84, 42), (84, 46.5)], BLUE, "<->", width=1.6)
    connector([(94, 46.5), (94, 37.5)], TEAL)
    connector([(91.5, 28.5), (91.5, 16), (21.5, 16), (21.5, 23)], TEAL, width=2.3)
    connector([(105, 51.5), (117, 51.5)], BLUE, "<->")
    connector([(105, 48.5), (110.7, 48.5), (110.7, 40), (117, 40)], PURPLE, "<->", dashed=True, width=1.7)
    connector([(110.7, 40), (110.7, 28.8), (117, 28.8)], PURPLE, dashed=True, width=1.7)

    # Browser mock-up gives the three abstract lanes a concrete interface.
    panel(7, 29, 29, 28.5, WHITE, radius=1.2)
    panel(7, 53.6, 29, 3.9, "#DEE8F6", "#DEE8F6", .9)
    for index, color in enumerate(("#BA7680", "#D6A258", "#58A899")):
        circle(
            (9.1+index*1.25, 55.55), .31,
            style=Styles.Neutral.patch(shape_fill_color=color, shape_line_color=color, shape_line_width=.4),
        )
    label(15, 55.55, "chatgpt.com", regular, size=13, color=BLUE)
    panel(13, 46.6, 20.5, 4.8, BLUE_TINT, BLUE_TINT, .9)
    label(14.3, 49, "比较这两份资料", regular, size=11.5)
    icon(phosphor.chat_circle_text, 10.4, 42.2, 2.7, TEAL)
    label(12.9, 42.25, "正在归纳共同点…", regular, size=10.5)
    for y, width in ((39.7, 17), (38.0, 13.8)):
        panel(13, y, width, .48, "#B1C6DA", "#B1C6DA", .15)
    panel(9, 31, 25, 4.5, "#F7F9FC", STROKE, .8)
    label(10.3, 33.25, "输入消息或添加附件", regular, size=10, color=MUTED)
    icon(phosphor.paper_plane_tilt, 32, 33.2, 2, BLUE)
    label(7.4, 26, "提交消息 · 逐段渲染回复", regular, size=11.5, color=BLUE)

    node(47, 46.5, 26, 10, "接入与校验", "身份与请求校验", phosphor.shield_check,
         BLUE, BLUE_TINT, regular, bold)
    node(78, 46.5, 27, 10, "对话编排", "组装上下文", phosphor.tree_structure,
         BLUE, BLUE_TINT, regular, bold)
    node(47, 28.5, 26, 9, "会话状态", "历史与附件引用", phosphor.database,
         BLUE, BLUE_TINT, regular, bold)
    node(78, 28.5, 27, 9, "流式响应", "增量文本与状态", phosphor.broadcast,
         TEAL, TEAL_TINT, regular, bold)
    node(117, 47.4, 36, 8.2, "模型推理", "生成文本或请求调用工具", phosphor.cpu,
         PURPLE, PURPLE_TINT, regular, bold)
    node(117, 35.9, 36, 8.2, "网页搜索", "查询网页并返回来源", phosphor.globe,
         PURPLE, PURPLE_TINT, regular, bold)
    node(117, 24.7, 36, 8.2, "文件与数据分析", "读取附件并返回分析结果", phosphor.file_text,
         PURPLE, PURPLE_TINT, regular, bold)

    panel(42, 13.5, 31, 5, TEAL_TINT, TEAL_TINT, 1)
    label(44, 16, "回复片段持续回传", bold, size=15, color=TEAL)
    for x, caption, color, dashed in (
        (5, "请求与上下文", BLUE, False),
        (34, "流式回复", TEAL, False),
        (59, "可选工具调用", PURPLE, True),
    ):
        connector([(x, 8.6), (x+5, 8.6)], color, dashed=dashed, width=1.7)
        label(x+7, 8.6, caption, regular, size=13, color=MUTED)
    label(91, 8.6, "依据公开产品能力绘制，服务边界为示意", regular, size=13, color=MUTED)

    save(str((output / "chatgpt-web-architecture.png").resolve()))
    svg_path = output / "chatgpt-web-architecture.svg"
    # Outline text and icon glyphs so the SVG is portable across machines.
    with rc_context({"svg.fonttype": "path"}):
        save(str(svg_path.resolve()))
    # The Skill's SVG renderer expects unitless root dimensions.
    head, separator, body = svg_path.read_text(encoding="utf-8").partition("viewBox=")
    head = re.sub(r'((?:width|height)="[\d.]+)pt"', r'\1"', head)
    svg_path.write_text(head + separator + body, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "drawlib-chatgpt")
    parser.add_argument("--font", type=Path, default=Path("C:/Windows/Fonts/msyh.ttc"))
    parser.add_argument("--bold-font", type=Path, default=Path("C:/Windows/Fonts/msyhbd.ttc"))
    args = parser.parse_args()
    build(args.output, args.font, args.bold_font)
