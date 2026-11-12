import argparse
import json
from pathlib import Path
import sys
from .models import load_tokens,validate_deck
from .rendering import detect_backends,render_pptx
from .typography import resolve_font


def main(argv=None):
    p=argparse.ArgumentParser(prog='scientific-ppt')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor',help='Report fonts and optional actual-PPT renderers')
    a=sub.add_parser('analyze');a.add_argument('input');a.add_argument('--output',required=True);a.add_argument('--backend',default='auto',choices=['auto','powerpoint','libreoffice']);a.add_argument('--no-render',action='store_true')
    v=sub.add_parser('validate');v.add_argument('input')
    e=sub.add_parser('extract');e.add_argument('input');e.add_argument('--output',required=True)
    m=sub.add_parser('plan');m.add_argument('input');m.add_argument('--output',required=True)
    r=sub.add_parser('render');r.add_argument('input');r.add_argument('--output',required=True);r.add_argument('--backend',default='auto',choices=['auto','powerpoint','libreoffice'])
    b=sub.add_parser('build');b.add_argument('input');b.add_argument('--output',required=True);b.add_argument('--tokens');b.add_argument('--backend',default='auto',choices=['auto','powerpoint','libreoffice']);b.add_argument('--max-repairs',type=int);b.add_argument('--no-render',action='store_true');b.add_argument('--strict',action='store_true',help='Fail on QA errors or unavailable renderer')
    args=p.parse_args(argv)
    try:
        if args.command=='doctor':
            t=load_tokens();print(json.dumps({'renderers':detect_backends(),'fonts':{k:resolve_font(t['fonts'][k]) for k in ['body','heading','latin']}},ensure_ascii=False,indent=2));return 0
        if args.command=='analyze':
            from .reference_analysis import analyze_reference
            reports=analyze_reference(args.input,args.output,args.backend,not args.no_render)
            print(json.dumps([{k:r[k] for k in ['file','slides','render_status','rendered_count']} for r in reports],ensure_ascii=False,indent=2))
            return 0 if all(r['render_status']=='rendered' for r in reports) else 2
        if args.command in ('extract','plan'):
            from .ingest import extract,markdown_plan
            out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
            result=extract(args.input) if args.command=='extract' else json.dumps(markdown_plan(args.input),ensure_ascii=False,indent=2)
            out.write_text(result,encoding='utf-8');print(out);return 0
        if args.command=='render':
            result=render_pptx(args.input,args.output,args.backend);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']=='rendered' else 2
        source=Path(args.input).resolve();deck=json.loads(source.read_text(encoding='utf-8-sig'));validate_deck(deck)
        if args.command=='validate':print('Valid deck schema and data invariants');return 0
        from .pipeline import build
        report=build(deck,args.output,source.parent,load_tokens(args.tokens),args.backend,args.max_repairs,not args.no_render)
        print(json.dumps({k:report[k] for k in ['status','pptx','slide_count','rendered_count','attempts']},ensure_ascii=False,indent=2))
        return 2 if args.strict and report['status'] in ('needs_review','unverified') else 0
    except (ValueError,OSError) as exc:
        print(f'Error: {exc}',file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
