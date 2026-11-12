"""Conservative font measurements. Never hide overflow by shrinking body text."""
from functools import lru_cache
import os
from pathlib import Path
import subprocess
import re
import math
from PIL import ImageFont


@lru_cache(maxsize=32)
def resolve_font(family):
    override = os.getenv('SCIENTIFIC_PPT_FONT_PATH')
    if override and Path(override).is_file():
        return override, family, None
    windows = Path(os.getenv('WINDIR','C:/Windows'))/'Fonts'
    mapping = {'SimSun':'simsun.ttc','宋体':'simsun.ttc','SimHei':'simhei.ttf','黑体':'simhei.ttf',
               'Times New Roman':'times.ttf','Arial':'arial.ttf','Microsoft YaHei':'msyh.ttc'}
    candidate = windows/mapping.get(family,'missing')
    if candidate.is_file(): return str(candidate), family, None
    try:
        result = subprocess.run(['fc-match','-f','%{file}\n%{family}',family],capture_output=True,text=True,timeout=5,check=True)
        path,actual = result.stdout.split('\n',1)
        if Path(path).is_file():
            return path,actual.split(',')[0],None if family.lower() in actual.lower() else f'Font {family} substituted by {actual}'
    except (OSError,subprocess.SubprocessError,ValueError):
        pass
    for name in ('msyh.ttc','arial.ttf'):
        if (windows/name).exists(): return str(windows/name),'Microsoft YaHei' if name.startswith('msyh') else 'Arial',f'Font {family} unavailable; fallback {name}'
    import ziafont
    candidates = list(Path(ziafont.__file__).parent.rglob('*.ttf'))
    if candidates: return str(candidates[0]),'DejaVu Sans',f'Font {family} unavailable; fallback may lack CJK glyphs'
    raise ValueError('No measurable font found. Set SCIENTIFIC_PPT_FONT_PATH to a readable TTF/TTC.')


@lru_cache(maxsize=256)
def font(family,size):
    return ImageFont.truetype(resolve_font(family)[0], max(1,round(size*4)))


def width(text,size,family):
    return font(family,size).getlength(text)/4


def wrap(text,max_width,size,family):
    """Return lossless line chunks (concatenation equals input, including whitespace)."""
    if max_width <= 0: raise ValueError('Text width must be positive')
    lines, current = [], ''
    for token in re.findall(r'\n|[^\S\n]+|[A-Za-z0-9_.,:/@%+\-]+|[^\x00-\x7F]|.',text):
        if token == '\n':
            lines.append(current+'\n'); current=''; continue
        if current and width(current+token,size,family) > max_width:
            lines.append(current); current=''
        if width(token,size,family) > max_width:
            for char in token:
                if current and width(current+char,size,family)>max_width:
                    lines.append(current);current=''
                current += char
        else: current += token
    if current: lines.append(current)
    return lines or ['']


def text_height(text,w,size,tokens,safety=1.0):
    s=tokens['spacing']
    lines=wrap(text,max(1,w-2*s['text_padding']),size,tokens['fonts']['body'])
    return len(lines)*size*s['line_height']*safety + 2*s['text_padding']


def split_text(text,w,h,size,tokens,safety=1.0):
    s=tokens['spacing']; line_height=size*s['line_height']*safety
    capacity=int((h-2*s['text_padding'])/line_height)
    if capacity<1: raise ValueError('Text box cannot hold even one line')
    lines=wrap(text,w-2*s['text_padding'],size,tokens['fonts']['body'])
    # Balance page lengths so the last page does not contain one orphan line.
    count=math.ceil(len(lines)/capacity)
    per_page,extra=divmod(len(lines),count)
    chunks=[];start=0
    for i in range(count):
        end=start+per_page+(1 if i<extra else 0)
        chunks.append(''.join(lines[start:end]));start=end
    # Prefer nearby sentence boundaries while preserving bytes and the measured limit.
    if len(chunks)>1:
        balanced=[];remaining=text
        for i,chunk in enumerate(chunks[:-1]):
            target=len(chunk)
            boundaries=[m.end() for m in re.finditer(r'[。！？\n]|[.!?](?=\s)',remaining)]
            candidates=sorted((b for b in boundaries if target*.65<=b<=target*1.2),key=lambda b:abs(b-target))
            cut=next((b for b in candidates if len(wrap(remaining[:b],w-2*s['text_padding'],size,tokens['fonts']['body']))<=capacity),min(target,len(remaining)))
            balanced.append(remaining[:cut]);remaining=remaining[cut:]
        if remaining and len(wrap(remaining,w-2*s['text_padding'],size,tokens['fonts']['body']))<=capacity:
            chunks=balanced+[remaining]
    assert ''.join(chunks)==text
    return chunks
