from pathlib import Path
import hashlib
from PIL import Image, ImageOps
from .models import Box


def prepare_image(path,cache):
    path=Path(path)
    if not path.is_file(): raise FileNotFoundError(path)
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    key=hashlib.sha256(path.read_bytes()).hexdigest()[:20]
    output=cache/f'{key}.png'
    if path.suffix.lower()=='.svg':
        from resvg_py import svg_to_bytes
        # No remote fetching. SVG assets must be local, self-contained evidence.
        output.write_bytes(svg_to_bytes(svg_string=path.read_text(encoding='utf-8'),width=2400))
    else:
        with Image.open(path) as src:
            im=ImageOps.exif_transpose(src).convert('RGBA')
            im.save(output)
    with Image.open(output) as im: size=im.size
    if min(size)<=0: raise ValueError('Invalid image dimensions')
    return output,size


def fit_image(size,box,mode='contain',allow_crop=False,max_crop=.2):
    iw,ih=size
    if min(iw,ih,box.w,box.h)<=0: raise ValueError('Image and destination dimensions must be positive')
    ratio=iw/ih; target=box.w/box.h
    crop=1-min(ratio/target,target/ratio)
    warning=None
    if mode=='cover' and (not allow_crop or crop>max_crop):
        mode='contain';warning=f'Crop {crop:.1%} rejected; used contain'
    if mode=='cover': return box,mode,warning
    scale=min(box.w/iw,box.h/ih)
    w,h=iw*scale,ih*scale
    return Box(box.x+(box.w-w)/2,box.y+(box.h-h)/2,w,h),mode,warning
