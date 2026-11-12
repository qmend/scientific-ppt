"""Pure Python LaTeX subset to SVG paths and high resolution PNG, with source retention."""
from pathlib import Path
import hashlib
import re
import xml.etree.ElementTree as ET
from PIL import Image


def render_equation(latex,cache,size=28):
    from latex2mathml.converter import convert
    import ziamath
    from resvg_py import svg_to_bytes
    # Reject file access, macro programming and unsupported commands before rendering.
    if re.search(r'\\(?:input|include|write|read|openout|def|newcommand|usepackage|documentclass)\b',latex):
        raise ValueError('Only mathematical LaTeX expressions are accepted')
    try:
        mathml=convert(latex)
        root=ET.fromstring(mathml)
        if any('\\' in (el.text or '') for el in root.iter()):
            raise ValueError('Unknown LaTeX command remains in MathML')
        svg=ziamath.Math(mathml,size=size).svg()
    except Exception as exc:
        raise ValueError(f'Cannot render LaTeX {latex!r}: {exc}') from exc
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    key=hashlib.sha256((str(size)+'\n'+latex).encode()).hexdigest()[:20]
    prefix=cache/f'equation-{key}'
    prefix.with_suffix('.tex').write_text(latex,encoding='utf-8')
    prefix.with_suffix('.svg').write_text(svg,encoding='utf-8')
    prefix.with_suffix('.mml').write_text(mathml,encoding='utf-8')
    prefix.with_suffix('.png').write_bytes(svg_to_bytes(svg_string=svg,zoom=4))
    with Image.open(prefix.with_suffix('.png')) as im:
        w,h=im.size
        if not im.getbbox():raise ValueError('Formula rendered blank')
    return {'png':str(prefix.with_suffix('.png')),'svg':str(prefix.with_suffix('.svg')),'tex':str(prefix.with_suffix('.tex')),'size_px':[w,h],'size_pt':[w/4,h/4]}
