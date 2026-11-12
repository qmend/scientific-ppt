"""Portable reference intake: structural evidence plus actual render, never automatic style certification."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from lxml import etree
from pptx import Presentation
from PIL import Image
from .rendering import detect_backends,render_pptx,contact_sheet
from .models import load_tokens


def convert_legacy(source,out,backend='auto',timeout=180):
    source=Path(source).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    backends=detect_backends();errors=[]
    for name in (['powerpoint','libreoffice'] if backend=='auto' else [backend]):
        if not backends.get(name):continue
        target=out/'converted.pptx'
        try:
            if name=='powerpoint':
                subprocess.run([sys.executable,str(Path(__file__).with_name('render_worker.py')),str(source),str(target)],capture_output=True,text=True,timeout=timeout,check=True)
            else:
                subprocess.run([backends[name],f'-env:UserInstallation={(out/"profile").as_uri()}','--headless','--convert-to','pptx','--outdir',str(out),str(source)],capture_output=True,text=True,timeout=timeout,check=True)
                shutil.copyfile(out/(source.stem+'.pptx'),target)
            if not zipfile.is_zipfile(target):raise ValueError('Converted presentation is not a valid PPTX')
            return target
        except (OSError,ValueError,subprocess.SubprocessError) as exc:errors.append(str(exc))
    raise ValueError('Legacy PPT conversion needs a working PowerPoint/LibreOffice backend: '+'; '.join(errors))


def analyze_reference(source,output,backend='auto',do_render=True):
    source=Path(source).resolve();output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    files=[source] if source.is_file() else sorted(p for p in source.iterdir() if p.suffix.lower() in ('.ppt','.pptx'))
    if not files:raise ValueError('No PPT or PPTX reference files found')
    reports=[]
    for index,path in enumerate(files,1):
        folder=output/f'deck-{index:02}';folder.mkdir(exist_ok=True)
        pptx=convert_legacy(path,folder,backend) if path.suffix.lower()=='.ppt' else path
        pres=Presentation(pptx);fonts=Counter();colors=Counter();sizes=Counter();slides=[]
        with zipfile.ZipFile(pptx) as z:
            ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
            for name in z.namelist():
                if name.startswith('ppt/') and name.endswith('.xml'):
                    xml=etree.fromstring(z.read(name))
                    fonts.update(xml.xpath('//a:latin/@typeface | //a:ea/@typeface',namespaces=ns))
                    colors.update(xml.xpath('//a:srgbClr/@val',namespaces=ns))
                    sizes.update(xml.xpath('//a:rPr/@sz | //a:defRPr/@sz',namespaces=ns))
        def walk(shapes):
            for s in shapes:
                yield s
                if s.shape_type==6:yield from walk(s.shapes)
        for i,slide in enumerate(pres.slides,1):
            objects=[]
            for s in walk(slide.shapes):
                objects.append({'kind':int(s.shape_type),'box_pt':[round(v/12700,3) if v is not None else None for v in (s.left,s.top,s.width,s.height)],'text':s.text if s.has_text_frame else '', 'table':bool(s.has_table),'chart':bool(s.has_chart)})
            slides.append({'page':i,'objects':objects})
        render=render_pptx(pptx,folder/'previews',backend) if do_render else {'status':'unavailable','images':[],'backend':None,'errors':['Disabled by caller']}
        contacts=[]
        for start in range(0,len(render['images']),20):
            contacts.append(contact_sheet(render['images'][start:start+20],folder/f'contact-{start+1:03}.jpg'))
        sample_colors=Counter()
        for image_path in render['images']:
            with Image.open(image_path) as im:
                # Actual visible colors, unlike XML frequency dominated by inherited styles.
                thumb=im.convert('RGB').resize((80,60));sample_colors.update(thumb.getdata())
        summary={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'slides':len(pres.slides),'size_pt':[pres.slide_width/12700,pres.slide_height/12700],
            'fonts':fonts.most_common(20),'sizes_pt':[(int(k)/100,v) for k,v in sizes.most_common(20)],'xml_colors':colors.most_common(20),
            'rendered_colors':[(''.join(f'{v:02X}' for v in k),n) for k,n in sample_colors.most_common(20)],
            'render_status':render['status'],'rendered_count':len(render['images']),'renderer':render['backend'],'render_errors':render.get('errors',[]),'contact_sheets':contacts,
            'limits':['Font inheritance and group-local coordinates require interpretation.','Token candidates need Agent review of all rendered slides.']}
        (folder/'objects.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf-8')
        reports.append(summary)
    (output/'inventory.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
    candidate=load_tokens();candidate['canvas']={'width':reports[0]['size_pt'][0],'height':reports[0]['size_pt'][1]}
    candidate['provenance']='PROVISIONAL: canvas measured from first reference. Other values remain defaults until Agent visual review; see inventory.json.'
    (output/'token_candidates.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2),encoding='utf-8')
    return reports
