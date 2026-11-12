from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from PIL import Image,ImageDraw


def detect_backends():
    office=False
    if sys.platform=='win32' and importlib.util.find_spec('win32com'):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,'PowerPoint.Application'):office=True
        except OSError:pass
    candidates=[os.getenv('SCIENTIFIC_PPT_SOFFICE'),shutil.which('soffice'),shutil.which('libreoffice'),
        'C:/Program Files/LibreOffice/program/soffice.exe','/Applications/LibreOffice.app/Contents/MacOS/soffice']
    soffice=next((str(Path(p)) for p in candidates if p and Path(p).is_file()),None)
    return {'powerpoint':office,'libreoffice':soffice}


def render_pptx(source,out_dir,backend='auto',timeout=180):
    source=Path(source).resolve();out=Path(out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    available=detect_backends();errors=[]
    order=['powerpoint','libreoffice'] if backend=='auto' else [backend]
    for name in order:
        if not available.get(name):continue
        try:
            # Isolated directory prevents stale PDFs/previews from counting as successful output.
            with tempfile.TemporaryDirectory(prefix='render-',dir=out) as temp:
                temp=Path(temp);pdf=temp/(source.stem+'.pdf')
                if name=='powerpoint':
                    worker=Path(__file__).with_name('render_worker.py')
                    subprocess.run([sys.executable,str(worker),str(source),str(pdf)],capture_output=True,text=True,timeout=timeout,check=True)
                else:
                    profile=(temp/'profile').as_uri()
                    subprocess.run([available[name],f'-env:UserInstallation={profile}','--headless','--convert-to','pdf','--outdir',str(temp),str(source)],capture_output=True,text=True,timeout=timeout,check=True)
                if not pdf.is_file() or pdf.stat().st_size==0:raise RuntimeError('Renderer produced no PDF')
                final=out/'slides.pdf';shutil.copyfile(pdf,final)
                metric_path=pdf.with_suffix('.metrics.json')
                metrics=json.loads(metric_path.read_text(encoding='utf-8')) if metric_path.exists() else []
            images=render_pdf(final,out)
            return {'status':'rendered','backend':name,'pdf':str(final),'images':images,'metrics':metrics,'errors':errors}
        except (OSError,RuntimeError,subprocess.SubprocessError) as exc:
            detail=(getattr(exc,'stderr','') or str(exc))[-3000:]
            errors.append(f'{name}: {detail}')
    return {'status':'unavailable','backend':None,'images':[],'metrics':[],'errors':errors or ['No actual PPT renderer available. Install LibreOffice or the optional Office backend.']}


def render_pdf(pdf,out,scale=1.6667):
    import pypdfium2 as pdfium
    out=Path(out);out.mkdir(parents=True,exist_ok=True);images=[]
    with pdfium.PdfDocument(str(pdf)) as doc:
        for i in range(len(doc)):
            page=doc[i];bitmap=page.render(scale=scale);im=bitmap.to_pil()
            path=out/f'slide-{i+1:03}.png';im.save(path);images.append(str(path))
            bitmap.close();page.close()
    return images


def contact_sheet(paths,output,columns=4):
    if not paths:return None
    thumbw=360;thumbh=290
    sheet=Image.new('RGB',(columns*thumbw,((len(paths)+columns-1)//columns)*thumbh),'#e8e8e8');draw=ImageDraw.Draw(sheet)
    for i,path in enumerate(paths):
        with Image.open(path) as im:
            image=im.convert('RGB');image.thumbnail((thumbw-8,thumbh-24))
            x=(i%columns)*thumbw;y=(i//columns)*thumbh
            sheet.paste(image,(x+4,y+20));draw.text((x+8,y+3),str(i+1),fill='black')
    sheet.save(output);return str(output)
