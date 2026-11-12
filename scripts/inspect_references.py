"""Extract structural evidence and contact sheets from converted reference decks."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import zipfile
from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

def main():
    reports = []
    out = ROOT / 'references'
    out.mkdir(exist_ok=True)
    for folder in sorted((ROOT / 'artifacts/reference-analysis').iterdir()):
        if not (folder / 'metadata.json').exists():
            continue
        prs = Presentation(folder / 'source.pptx')
        fonts, sizes, colors, fills, spacing = (Counter() for _ in range(5))
        with zipfile.ZipFile(folder / 'source.pptx') as z:
            for name in z.namelist():
                if name.startswith('ppt/') and name.endswith('.xml'):
                    root = etree.fromstring(z.read(name))
                    fonts.update(root.xpath('//a:latin/@typeface | //a:ea/@typeface', namespaces=NS))
                    sizes.update(root.xpath('//a:rPr/@sz | //a:defRPr/@sz', namespaces=NS))
                    colors.update(root.xpath('//a:srgbClr/@val', namespaces=NS))
                    fills.update(root.xpath('//a:solidFill/a:srgbClr/@val', namespaces=NS))
                    spacing.update(root.xpath('//a:lnSpc/a:spcPct/@val', namespaces=NS))
        slides = []
        def shapes(items):
            for s in items:
                yield s
                if s.shape_type == 6:
                    yield from shapes(s.shapes)
        for i, slide in enumerate(prs.slides, 1):
            objects = []
            for s in shapes(slide.shapes):
                item = {'type': int(s.shape_type), 'box_pt': [round(v/12700, 2) if v is not None else None for v in (s.left,s.top,s.width,s.height)]}
                if s.has_text_frame:
                    item['text'] = s.text
                    item['paragraphs'] = [{'alignment': str(p.alignment), 'runs':[{'text':r.text,'font':r.font.name,'pt':r.font.size.pt if r.font.size else None,'bold':r.font.bold} for r in p.runs]} for p in s.text_frame.paragraphs]
                if s.shape_type == 13:
                    item['image_size'] = s.image.size
                    item['crop'] = [s.crop_left,s.crop_top,s.crop_right,s.crop_bottom]
                item['table'] = bool(s.has_table)
                item['chart'] = bool(s.has_chart)
                objects.append(item)
            slides.append({'number':i,'objects':objects})
        raw = ROOT.parent / 'material' / (folder.name + '.ppt')
        report = {'file':raw.name,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'slides':len(prs.slides),'size_pt':[prs.slide_width/12700,prs.slide_height/12700], 'fonts':fonts.most_common(20),'sizes_pt':[(int(k)/100,v) for k,v in sizes.most_common(20)],'colors':colors.most_common(20),'fills':fills.most_common(15),'line_spacing_percent':spacing.most_common(10)}
        reports.append(report)
        (folder / 'objects.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf-8')
        imgs = sorted((folder/'slides').glob('*.PNG'), key=lambda p:int(re.search(r'(\d+)\.',p.name)[1]))
        for start in range(0,len(imgs),20):
            sheet = Image.new('RGB',(1600,1040),'#e6e6e6')
            draw = ImageDraw.Draw(sheet)
            for j,p in enumerate(imgs[start:start+20]):
                im = Image.open(p).convert('RGB'); im.thumbnail((316,237))
                x,y = (j%5)*320,(j//5)*260
                sheet.paste(im,(x,y+20)); draw.text((x+5,y+3),str(start+j+1),fill='black')
            sheet.save(folder/f'contact-{start+1:03}.jpg',quality=88)
    (out/'reference_inventory.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(reports,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
