"""Explicit figure layouts for standalone SVG output."""

import base64
from dataclasses import dataclass
from html import escape


INK = "#243448"
MUTED = "#516277"
LINE = "#A9B7C7"
WHITE = "#FFFFFF"
BLUE = "#2B628B"
TEAL = "#20736C"
VIOLET = "#72528B"
AMBER = "#9A5C1E"
BLUE_BG = "#EDF5FB"
TEAL_BG = "#EAF5F2"
VIOLET_BG = "#F4EEF8"
AMBER_BG = "#FCF3E7"


@dataclass(frozen=True)
class Region:
    x: float
    y: float
    w: float
    h: float

    def port(self, side, fraction=.5):
        if side in ("L", "R"):
            return (self.x + (self.w if side == "R" else 0), self.y + self.h * fraction)
        return (self.x + self.w * fraction, self.y + (self.h if side == "B" else 0))


class FigureCanvas:
    """Draw a figure with explicitly placed nodes and orthogonal waypoints."""

    def __init__(self, slug, title, subtitle, height=720, width=1440):
        self.slug = slug
        self.width = width
        self.height = height
        self.svg_layers = {key: [] for key in ("back", "edges", "front")}
        self.node_count = 0
        self.edge_count = 0
        self.image_count = 0
        self.text(28, 19, width - 56, 44, title, size=36, bold=True)
        self.text(29, 66, width - 58, 29, subtitle, size=19, color=MUTED)
        self.line([(28, 100), (width-28, 100)], color=LINE, width=1)

    def _region(self, x, y, w, h):
        if min(x, y) < 0 or w <= 0 or h <= 0 or x+w > self.width or y+h > self.height:
            raise ValueError(f"{self.slug}: shape outside canvas at {(x, y, w, h)}")
        return Region(x, y, w, h)

    @staticmethod
    def _label(x, y, text, size, color, bold, align):
        rows = text.split("\n")
        anchor = "middle" if align == "center" else "start"
        first_baseline = y - (len(rows)-1)*size*.6 + size*.34
        return "".join(
            f'<text x="{x}" y="{first_baseline+i*size*1.2:.2f}" text-anchor="{anchor}" '
            f'font-family="Arial" font-size="{size}" font-weight="{"700" if bold else "400"}" '
            f'fill="{color}">{escape(row)}</text>'
            for i, row in enumerate(rows)
        )

    def text(self, x, y, w, h, value, *, size=18, color=INK, bold=False, align="left"):
        region = self._region(x, y, w, h)
        self.svg_layers["front"].append(self._label(x+w/2 if align == "center" else x, y+h/2, value, size, color, bold, align))
        return region

    def box(self, x, y, w, h, label="", *, fill=WHITE, stroke=LINE, size=18, color=INK,
            radius=8, bold=True, layer="front", dashed=False):
        shape = self._region(x, y, w, h)
        dash = ' stroke-dasharray="7 5"' if dashed else ""
        self.svg_layers[layer].append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>'
        )
        if label:
            self.node_count += 1
            self.svg_layers[layer].append(self._label(x+w/2, y+h/2, label, size, color, bold, "center"))
        return shape

    def panel(self, x, y, w, h, label, *, fill=WHITE, color=INK, dashed=False):
        region = self.box(x, y, w, h, fill=fill, layer="back", radius=12, dashed=dashed)
        self.text(x+16, y+9, w-32, 24, label, size=18, bold=True, color=color)
        return region

    def image(self, x, y, w, h, png, label=None):
        payload = base64.b64encode(png).decode("ascii")
        region = self._region(x, y, w, h)
        self.svg_layers["front"].append(
            f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none" '
            f'xlink:href="data:image/png;base64,{payload}"/>'
        )
        self.svg_layers["front"].append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{LINE}" stroke-width="1"/>'
        )
        self.image_count += 1
        if label:
            self.text(x-5, y+h+4, w+10, 25, label, size=16, align="center")
        return region

    def line(self, points, *, color=INK, width=2, dashed=False, arrow=False, layer="edges"):
        coords = " ".join(f"{x},{y}" for x, y in points)
        dash = ' stroke-dasharray="7 6"' if dashed else ""
        path = f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"{dash}/>'
        if arrow:
            x, y = points[-1]
            px, py = points[-2]
            length = ((x-px)**2+(y-py)**2)**.5
            dx, dy = (x-px)/length, (y-py)/length
            wings = [(x-9*dx+sign*4*dy, y-9*dy-sign*4*dx) for sign in (-1, 1)]
            path += f'<polygon points="{x},{y} ' + " ".join(f"{u:.2f},{v:.2f}" for u, v in wings) + f'" fill="{color}"/>'
            self.edge_count += 1
        self.svg_layers[layer].append(path)

    def link(self, a, b, *, start="R", end="L", at=.5, into=.5, bends=(), **kwargs):
        self.line([a.port(start, at), *bends, b.port(end, into)], arrow=True, **kwargs)

    def tensor(self, x, y, w, h, label, fill, *, layers=4):
        for offset in range(layers-1, 0, -1):
            self.box(x+offset*8, y-offset*7, w, h, fill=fill, stroke=LINE, radius=3)
        front = self.box(x, y, w, h, fill=fill, stroke=BLUE, radius=3)
        for column in range(1, 4):
            self.line([(x+w*column/4, y), (x+w*column/4, y+h)], color=WHITE, width=1, layer="front")
        for row in range(1, 5):
            self.line([(x, y+h*row/5), (x+w, y+h*row/5)], color=WHITE, width=1, layer="front")
        self.text(x-18, y+h+4, w+50, 25, label, size=16, align="center")
        return front

    def footer(self, label, source):
        y = self.height-49
        self.line([(28, y), (self.width-28, y)], color=LINE, width=1)
        self.text(29, y+9, self.width-58, 27, label+"   |   "+source, size=16, color=MUTED)

    def svg(self):
        art = "".join("".join(items) for items in self.svg_layers.values())
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">'
            f'<rect width="100%" height="100%" fill="white"/>{art}</svg>'
        )

