from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from .models import load_tokens
from .planner import plan
from .pptx_writer import write_pptx
from .rendering import render_pptx,contact_sheet
from .quality import inspect
from .typography import resolve_font


def prune_previous_outputs(out, current_images, has_pdf):
    """Remove only indexed previews and reserved artifacts from a previous build."""
    preview_dir=(out/'previews').resolve()
    index=preview_dir/'index.json'
    try:
        previous=json.loads(index.read_text(encoding='utf-8'))
    except (OSError,ValueError):
        previous=[]
    keep={Path(p).resolve() for p in current_images}
    if isinstance(previous,list):
        for value in previous:
            if not isinstance(value,str):continue
            path=Path(value).resolve()
            if path.parent==preview_dir and path.name.startswith('slide-') and path.suffix=='.png' and path not in keep:
                path.unlink(missing_ok=True)
    if (out/'qa_report.json').is_file():
        if not has_pdf:(out/'presentation.pdf').unlink(missing_ok=True)
        if not current_images:(out/'contact-sheet.jpg').unlink(missing_ok=True)


def build(deck,out_dir,base_dir='.',tokens=None,backend='auto',max_repairs=None,do_render=True,renderer=None):
    tokens=deepcopy(tokens or load_tokens());out=Path(out_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    renderer=renderer or render_pptx
    repairs=tokens['quality']['max_repairs'] if max_repairs is None else max_repairs
    if not 0<=repairs<=5:raise ValueError('max_repairs must be between 0 and 5')
    safety=tokens['quality']['measurement_safety'];history=[];font_warnings=[]
    for name in set(tokens['fonts'][k] for k in ['body','heading','latin']):
        path,actual,warning=resolve_font(name)
        if warning:font_warnings.append(warning)
    source_hash=hashlib.sha256(json.dumps(deck,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    for attempt in range(repairs+1):
        attempt_dir=out/f'attempt-{attempt}';attempt_dir.mkdir(exist_ok=True)
        try:
            pages=plan(deck,tokens,base_dir,out/'assets',safety)
            pptx=attempt_dir/'presentation.pptx'
            manifest,warnings=write_pptx(deck,pages,tokens,pptx)
        except (ValueError,OSError) as exc:
            failure={'status':'failed','source_sha256':source_hash,'error':str(exc),'attempt':attempt,'history':history}
            (out/'qa_report.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding='utf-8')
            raise
        rendered=renderer(pptx,attempt_dir/'previews',backend) if do_render else {'status':'unavailable','backend':None,'images':[],'metrics':[],'errors':['Rendering disabled by caller']}
        issues=inspect(manifest,tokens,rendered)
        history.append({'attempt':attempt,'measurement_safety':safety,'pages':len(pages),'errors':sum(i['severity']=='error' for i in issues),'issues':issues})
        repairable=any(i['code'] in ('text_overflow','rendered_text_overflow') for i in issues)
        if repairable and attempt<repairs:
            safety*=1.18
            tokens['type']['title']=max(24,tokens['type']['title']-2)
            continue
        break
    import shutil
    final=out/'presentation.pptx';shutil.copyfile(pptx,final)
    preview_dir=out/'previews';preview_dir.mkdir(exist_ok=True)
    final_images=[]
    for i,p in enumerate(rendered['images'],1):
        dest=preview_dir/f'slide-{i:03}.png';shutil.copyfile(p,dest);final_images.append(str(dest))
    prune_previous_outputs(out,final_images,bool(rendered.get('pdf')))
    (preview_dir/'index.json').write_text(json.dumps(final_images,indent=2),encoding='utf-8')
    html='<!doctype html><meta charset="utf-8"><title>Slide previews</title><style>body{background:#eee;font-family:serif;max-width:1100px;margin:30px auto}img{width:100%;height:auto}figure{margin:30px 0}figcaption{padding:8px}</style>'
    html+=''.join(f'<figure><figcaption>Slide {i}</figcaption><a href="{Path(p).name}"><img src="{Path(p).name}" alt="Slide {i}" loading="lazy"></a></figure>' for i,p in enumerate(final_images,1))
    (preview_dir/'index.html').write_text(html,encoding='utf-8')
    if rendered.get('pdf'):shutil.copyfile(rendered['pdf'],out/'presentation.pdf')
    contact_sheet(final_images,out/'contact-sheet.jpg')
    has_errors=any(i['severity']=='error' for i in issues)
    report={'status':'needs_review' if has_errors else ('rendered_needs_visual_review' if rendered['status']=='rendered' else 'unverified'),
        'pptx':str(final),'source_sha256':source_hash,'pptx_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),
        'slide_count':len(pages),'rendered_count':len(final_images),'renderer':rendered['backend'],'render_errors':rendered.get('errors',[]),
        'attempts':len(history),'max_repairs':repairs,'issues':issues,'font_warnings':font_warnings,'image_warnings':warnings,
        'history':history,'limitations':['Automated geometry and pixel checks do not prove scientific correctness or visual quality. Agent must inspect every preview.'],
        'manifest':manifest}
    (out/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'resolved_layout.json').write_text(json.dumps([asdict(p) for p in pages],ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'input.json').write_text(json.dumps(deck,ensure_ascii=False,indent=2),encoding='utf-8')
    return report
