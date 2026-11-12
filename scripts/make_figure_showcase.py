"""Recreate four paper-figure layouts as SVG and PNG."""

import argparse
from functools import lru_cache
from io import BytesIO
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw
from resvg_py import svg_to_bytes

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from scientific_ppt.figure_canvas import (
    FigureCanvas, INK, MUTED, LINE, WHITE, BLUE, TEAL, VIOLET, AMBER,
    BLUE_BG, TEAL_BG, VIOLET_BG, AMBER_BG,
)


@lru_cache
def sample_image(kind):
    """Make illustrative tiles from an analytic surface of revolution."""
    height, width = 112, 176
    u, v = np.meshgrid(np.linspace(-1.25, 1.25, width), np.linspace(-1, 1, height))
    radius = .25 + .37*np.exp(-((v-.30)/.52)**2) + .12*np.exp(-((v+.65)/.16)**2)
    x = u / radius
    visible = (np.abs(x) < 1) & (v > -.78) & (v < .79)
    z = np.sqrt(np.maximum(0, 1-x*x))
    stripe = .5+.5*np.sin(30*v+2.5*x)
    normal_y = np.clip(-np.gradient(radius, axis=0)*height/2, -.8, .8)
    light = np.clip(.33 + .65*(.64*z-.42*x+.28*normal_y), .12, 1)
    background = np.clip(.16 + .12*(v+1) - .035*u, .1, .5)
    base = np.stack([.22+.27*stripe, .42+.21*stripe, .54+.18*stripe], axis=-1)
    shaded = base * light[..., None]
    highlight = .65*np.exp(-((x+.30)**2+(v+.14)**2)/.054)
    flash = shaded + highlight[..., None]
    rough = .30 + .35*stripe

    if kind == "mask":
        pixels = np.repeat(visible[..., None], 3, axis=-1)
    elif kind == "light":
        a = np.exp(-((u+.46)**2+(v+.2)**2)/.08)
        b = np.exp(-((u-.4)**2+(v-.32)**2)/.12)
        pixels = np.stack([.04+.85*a+.20*b, .08+.62*a+.55*b, .12+.48*a+.74*b], axis=-1)
    elif kind in ("points", "mesh"):
        tile = Image.new("RGB", (width, height), "#E8EDF4")
        draw = ImageDraw.Draw(tile)
        for row in range(13, height-10, 4):
            for col in range(10, width-10, 4):
                if visible[row, col]:
                    dx = int(col + 12*z[row, col] - 5*v[row, col])
                    dy = int(row - 5*z[row, col])
                    tint = (int(44+92*z[row,col]), int(92+90*z[row,col]), int(134+72*z[row,col]))
                    if kind=="mesh" and col+4<width and visible[row,col+4]:
                        draw.line((dx,dy,dx+4,dy-2),fill=tint,width=1)
                    else:
                        draw.ellipse((dx,dy,dx+2,dy+2),fill=tint)
        output = BytesIO()
        tile.save(output, format="PNG")
        return output.getvalue()
    elif kind.startswith("local-"):
        fraction = {"local-fine": .32, "local-medium": .55, "local-coarse": .85}[kind]
        tile = Image.open(BytesIO(sample_image("points")))
        half_w, half_h = width*fraction/2, height*fraction/2
        cx, cy = width*.53, height*.56
        tile = tile.crop((cx-half_w, cy-half_h, cx+half_w, cy+half_h))
        output = BytesIO()
        tile.resize((width,height),Image.Resampling.LANCZOS).save(output, format="PNG")
        return output.getvalue()
    else:
        maps = {
            "rgb": shaded, "flash": flash, "ambient": shaded*.76, "albedo": base,
            "normal": np.stack([.5+.48*x, .5+.46*normal_y, .48+.50*z], axis=-1),
            "depth": np.stack([.12+.79*z, .24+.52*z, .58-.31*z], axis=-1),
            "rough": np.repeat(rough[..., None], 3, axis=-1),
            "residual": np.stack([highlight, .32*highlight, .10*highlight], axis=-1),
            "render": shaded+highlight[..., None]*.87,
        }
        pixels = np.where(visible[..., None], maps[kind], background[..., None])
    output = BytesIO()
    Image.fromarray(np.uint8(np.clip(pixels, 0, 1)*255)).save(output, format="PNG")
    return output.getvalue()


def tile(d, x, y, w, h, kind, label=None):
    return d.image(x, y, w, h, sample_image(kind), label)


def block(d, x, y, w, h, label, color=BLUE, *, size=18):
    return d.box(x, y, w, h, label, stroke=color, size=size, color=color)


def architecture():
    d = FigureCanvas("01-architecture", "01   Network architecture",
                     "Distilling an offline dynamic NeRF into a video-to-mesh student")
    d.panel(28, 243, 248, 390, "INPUT  /  VIDEO", fill=BLUE_BG, color=BLUE)
    d.panel(306, 116, 1106, 104, "OFFLINE TEACHER  /  TRAINING ONLY", fill=TEAL_BG, color=TEAL, dashed=True)
    teacher = block(d, 332, 157, 214, 42, "Dynamic NeRF", TEAL)
    targets = block(d, 620, 157, 352, 42, "Pseudo-targets: pose, joints, surface", TEAL)
    loss = block(d, 1087, 157, 290, 42, "Distillation supervision", TEAL)
    d.link(teacher, targets, color=TEAL)
    d.link(targets, loss, color=TEAL)
    for y, kind, label in [(292, "rgb", "RGB frame"), (400, "mask", "Foreground"), (508, "normal", "CSE features\n(illustrated)")]:
        tile(d, 49, y, 113, 72, kind)
        d.text(174, y+12, 93, 48, label, size=15)

    d.panel(306, 243, 856, 178, "POSE & ARTICULATION", fill=BLUE_BG, color=BLUE)
    encode = block(d, 327, 299, 161, 70, "Stacked\nhourglass")
    temporal = block(d, 524, 299, 153, 70, "Temporal\npose encoder")
    viewpoint = block(d, 719, 280, 138, 43, "Viewpoint")
    joints = block(d, 719, 346, 138, 43, "Joint code")
    frozen = block(d, 907, 346, 210, 43, "Frozen joint decoder", VIOLET)
    d.link(encode, temporal)
    d.link(temporal, viewpoint, bends=((699,334),(699,301.5)))
    d.link(temporal, joints, bends=((699,334),(699,367.5)))
    d.link(joints, frozen, color=VIOLET)
    d.line([(276,436),(289,436),(289,334),(327,334)], arrow=True)

    d.panel(306, 444, 856, 189, "APPEARANCE", fill=AMBER_BG, color=AMBER)
    app = block(d, 327, 504, 161, 60, "ResNet-18", AMBER)
    texture = block(d, 524, 504, 153, 60, "Texture\ncode", AMBER)
    temporal_texture = block(d, 719, 504, 138, 60, "Temporal\nencoder", AMBER)
    texture_decoder = block(d, 907, 504, 210, 60, "Frozen texture\ndecoder", VIOLET)
    d.line([(276,436),(289,436),(289,534),(327,534)], arrow=True)
    d.link(app, texture, color=AMBER)
    d.link(texture, temporal_texture, color=AMBER)
    d.link(temporal_texture, texture_decoder, color=VIOLET)
    d.text(330, 584, 790, 24, "Per-frame features are combined across time before decoding vertex colors.", size=16, color=MUTED)

    d.panel(1190, 243, 222, 390, "OUTPUT  /  MESH", fill=TEAL_BG, color=TEAL)
    assemble = block(d, 1210, 315, 182, 96, "Deform & shade\ncanonical mesh", TEAL)
    mesh = tile(d, 1212, 470, 178, 112, "mesh", "Posed, textured mesh")
    d.link(viewpoint, assemble, into=.2, bends=((1140,301.5),(1140,334.2)))
    d.link(frozen, assemble, into=.55, bends=((1175,367.5),(1175,367.8)), color=VIOLET)
    d.link(texture_decoder, assemble, into=.86, bends=((1176,534),(1176,397.56)), color=VIOLET)
    d.link(assemble, mesh, start="B", end="T", color=TEAL)
    d.link(assemble, loss, start="R", at=.15, end="B", color=TEAL, dashed=True,
           bends=((1401,329.4),(1401,230),(1232,230)))
    d.footer("Dashed arrows indicate training supervision", "Simplified after Tan et al., CVPR 2023, Fig. 2")
    return d


def overview():
    d = FigureCanvas("02-method-overview", "02   Method overview",
                     "MoGe separates image-to-geometry inference from global and local supervision")
    d.panel(28, 116, 1384, 219, "INFERENCE", fill=BLUE_BG, color=BLUE)
    rgb = tile(d, 55, 173, 178, 112, "rgb", "Input image")
    vit = block(d, 278, 190, 164, 78, "ViT\nencoder")
    decoder = block(d, 482, 190, 172, 78, "Conv.\ndecoder")
    point_map = tile(d, 721, 155, 157, 92, "depth", "Point map P")
    mask = tile(d, 927, 221, 147, 84, "mask", "Mask M")
    points = tile(d, 1184, 170, 187, 112, "points", "Masked point cloud")
    d.link(rgb, vit)
    d.link(vit, decoder)
    d.link(decoder, point_map, bends=((683,229),(683,201)))
    d.link(decoder, mask, start="B", bends=((568,287),(905,287),(905,263)))
    d.link(point_map, points, into=.28, bends=((1128,201),(1128,201.36)))
    d.link(mask, points, into=.83)

    d.panel(28, 358, 1384, 286, "TRAINING SUPERVISION", fill=VIOLET_BG, color=VIOLET)
    d.panel(49, 407, 599, 209, "GLOBAL  /  SCENE SHAPE", fill=WHITE, color=VIOLET)
    predicted = tile(d, 70, 457, 128, 82, "points", "Prediction")
    reference = tile(d, 231, 457, 128, 82, "mesh", "Reference")
    align = block(d, 404, 465, 218, 64, "Robust scale / shift\nalignment", VIOLET)
    d.link(reference, align, color=VIOLET)
    d.link(predicted, align, at=.12, into=.22, bends=((212,466.84),(212,449),(387,449),(387,479.08)), color=VIOLET)
    d.text(69, 573, 551, 27, "Compare the aligned point maps over valid pixels.", size=16, color=MUTED)

    d.panel(667, 407, 722, 209, "LOCAL  /  MULTISCALE GEOMETRY", fill=WHITE, color=VIOLET)
    patches = []
    for i, (kind, label) in enumerate([("local-fine", "Fine"), ("local-medium", "Medium"), ("local-coarse", "Coarse")]):
        patches.append(tile(d, 692+i*120, 459, 96, 72, kind, label))
    local = block(d, 1107, 460, 253, 70, "Align & compare\nlocal neighborhoods", VIOLET)
    for i, patch in enumerate(patches):
        y = 442+i*5
        d.link(patch, local, start="T", into=.19+i*.3,
               bends=((patch.port("T")[0],y),(1068+i*12,y),(1068+i*12,473.3+i*21)),
               color=VIOLET, width=1.5)
    d.text(691, 571, 665, 27, "Sample neighborhoods at several scales to retain local detail.", size=16, color=MUTED)
    d.line([(1371,259.6),(1388,259.6),(1388,383),(1044,383),(1044,407)], color=VIOLET, dashed=True, arrow=True)
    d.line([(1388,383),(354,383),(354,407)], color=VIOLET, dashed=True, arrow=True)
    d.footer("Training uses global alignment and multiscale local geometry", "Simplified after Wang et al., CVPR 2025")
    return d


def internals():
    d = FigureCanvas("03-module-detail", "03   Complex module detail",
                     "A reversible feature transform with separate rendering and pixel-wise heads")
    d.panel(29, 117, 904, 321, "A   FEATURE TRANSFORM", fill=BLUE_BG, color=BLUE)
    d.panel(953, 117, 457, 321, "B   OUTPUT HEADS", fill=TEAL_BG, color=TEAL)
    f = d.tensor(67, 226, 83, 105, "H × W × C", "#BFDDF2")
    inn1 = block(d, 211, 244, 140, 67, "INN-1")
    latent = d.tensor(405, 226, 83, 105, "Latent F", "#D8C4E8")
    inn2 = block(d, 554, 244, 140, 67, "INN-2")
    out = d.tensor(752, 226, 83, 105, "Decoded F′", "#C5E5DB")
    d.link(f, inn1)
    d.link(inn1, latent)
    d.link(latent, inn2)
    d.link(inn2, out)
    d.link(out, f, at=.85, into=.85, bends=((878,315.25),(878,391),(52,391),(52,315.25)),
           color=AMBER, dashed=True)
    d.text(227, 397, 442, 29, "Inverse path through INN-2 and INN-1", size=16, color=AMBER, align="center")
    render = block(d, 977, 189, 179, 58, "Render head", TEAL)
    pixel = block(d, 977, 310, 179, 58, "Pixel decoder", TEAL)
    rendered = tile(d, 1210, 161, 170, 101, "render", "Rendered view")
    channels = tile(d, 1210, 292, 170, 101, "normal", "Per-pixel channels")
    d.link(out, render, bends=((911,278.5),(911,218)), color=TEAL)
    d.link(out, pixel, bends=((911,278.5),(911,339)), color=TEAL)
    d.link(render, rendered, color=TEAL)
    d.link(pixel, channels, color=TEAL)

    d.panel(29, 462, 1381, 187, "C   COUPLING SUBNETWORKS  /  DETAIL", fill=VIOLET_BG, color=VIOLET)
    for y, name, terms in [(515, "INN-1", ("Sine features", "Linear + ReLU", "Linear")),
                           (577, "INN-2", ("Linear + ReLU", "Linear + ReLU", "Linear"))]:
        d.text(55, y, 150, 42, name, size=18, bold=True, color=VIOLET)
        nodes = [block(d, 212+i*284, y, 216, 42, term, VIOLET, size=16) for i, term in enumerate(terms)]
        for left, right in zip(nodes, nodes[1:]):
            d.link(left, right, color=VIOLET)
        d.line([(996,y+21),(1094,y+21)], arrow=True, color=VIOLET)
    d.text(1111, 525, 255, 88, "Subnetworks predict\nparameters of the\nreversible coupling.", size=17, color=MUTED)
    d.footer("Colored planes denote tensor channels", "Illustrative layout based on the supplied reference")
    return d


def pipeline():
    d = FigureCanvas("04-pipeline", "04   Multistage pipeline",
                     "Two-shot inverse rendering with geometry, lighting and material estimates")
    d.panel(28, 118, 222, 523, "INPUTS", fill=BLUE_BG, color=BLUE)
    d.panel(274, 118, 648, 523, "CASCADED ESTIMATION", fill=TEAL_BG, color=TEAL)
    d.panel(948, 118, 464, 523, "RE-RENDER & REFINE", fill=VIOLET_BG, color=VIOLET)
    flash = tile(d, 53, 167, 172, 100, "flash", "Flash")
    tile(d, 53, 322, 172, 100, "ambient", "No flash")
    tile(d, 53, 477, 172, 100, "mask", "Object mask")

    stages = [
        (173, "1   Geometry", "Merge convolution", "normal", "Depth / normals", BLUE),
        (328, "2   Illumination", "Shape-guided encoder", "light", "Environment light", VIOLET),
        (483, "3   Material", "Guided SVBRDF", "albedo", "Diffuse / roughness", TEAL),
    ]
    nets, estimates = [], []
    for y, name, method, kind, label, color in stages:
        d.text(321, y-12, 292, 29, name, size=19, bold=True, color=color)
        nets.append(block(d, 321, y+27, 239, 57, method, color, size=17))
        estimates.append(tile(d, 654, y-4, 174, 100, kind, label))
        d.link(nets[-1], estimates[-1], into=.595, color=color)
    d.line([(250,433),(289,433),(289,228.5),(321,228.5)], arrow=True)
    d.line([(289,383.5),(321,383.5)], arrow=True)
    d.line([(289,433),(289,538.5),(321,538.5)], arrow=True)
    d.link(estimates[0], nets[1], start="L", end="R", at=.84, into=.7,
           bends=((611,253),(611,394.9)), color=BLUE)
    d.link(estimates[1], nets[2], start="L", end="R", at=.84, into=.7,
           bends=((611,408),(611,549.9)), color=VIOLET)
    d.link(estimates[0], nets[2], start="L", end="R", at=.96, into=.30,
           bends=((586,265),(586,527.1)), color=BLUE)

    renderer = block(d, 974, 201, 183, 55, "Renderer", VIOLET)
    synthesized = tile(d, 1201, 170, 178, 112, "render", "Re-rendered image")
    residual = block(d, 1177, 339, 204, 61, "Flash − re-render", AMBER)
    refiner = block(d, 975, 477, 187, 62, "Joint refinement", VIOLET)
    result = tile(d, 1201, 457, 178, 112, "mesh", "Refined shape + BRDF")
    for index, estimate in enumerate(estimates):
        x = 860+index*26
        y = estimate.port("R")[1]
        target_y = renderer.port("L", .28+index*.24)[1]
        d.link(estimate, renderer, into=.28+index*.24, bends=((x,y),(x,target_y)), color=stages[index][-1])
    d.link(renderer, synthesized, color=VIOLET)
    d.link(synthesized, residual, start="R", at=.7, end="T",
           bends=((1388,248.4),(1388,324),(1279,324)), color=AMBER)
    d.link(residual, refiner, start="L", end="T", bends=((1068.5,369.5),), color=AMBER)
    d.link(refiner, result, color=VIOLET)
    d.link(flash, residual, start="T", end="R", bends=((139,152),(1395,152),(1395,369.5)), color=AMBER, dashed=True)
    d.text(977, 597, 404, 33, "Refinement also uses the initial shape and material.", size=15, color=MUTED)
    d.footer("Dashed line carries the observed flash image", "Simplified after Boss et al., CVPR 2020, Fig. 2")
    return d


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"artifacts"/"figure-showcase")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    figures = [architecture(), overview(), internals(), pipeline()]
    summary = []
    for figure in figures:
        svg = figure.svg()
        (args.output/f"{figure.slug}.svg").write_text(svg, encoding="utf-8")
        (args.output/f"{figure.slug}.png").write_bytes(svg_to_bytes(svg_string=svg, width=2160))
        summary.append(dict(page=figure.slug, labels=figure.node_count, arrows=figure.edge_count, images=figure.image_count))
    (args.output/"figure_counts.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(args.output)


if __name__ == "__main__":
    main()
