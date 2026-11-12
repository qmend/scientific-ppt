"""Regenerate the deck schema used by the Skill."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def obj(props, required):
    return {'type':'object','properties':props,'required':required,'additionalProperties':False}
def array(item, minimum=0): return {'type':'array','items':item,'minItems':minimum}
S = {'type':'string'}
NONEMPTY = {'type':'string','minLength':1}
POS = {'type':'number','exclusiveMinimum':0}
NUM = {'type':'number'}
def block(kind, props, required):
    return obj({'type':{'const':kind},'id':NONEMPTY,'source':S,'box':{'type':'array','items':NUM,'minItems':4,'maxItems':4},**props},['type',*required])

blocks = [
    block('text',{'text':NONEMPTY,'emphasis':{'enum':['normal','blue','primary']},'heading':{'type':'boolean'},'bold':{'type':'boolean'}},['text']),
    block('image',{'path':NONEMPTY,'caption':S,'fit':{'enum':['contain','cover']},'allow_crop':{'type':'boolean'},'alt':S},['path']),
    block('equation',{'latex':NONEMPTY,'caption':S},['latex']),
    block('table',{'columns':array(NONEMPTY,1),'rows':array(obj({'id':NONEMPTY,'cells':array(S,1),'group':S},['id','cells']),1),'widths':array(POS,1),'caption':S},['columns','rows']),
    block('diagram',{'direction':{'enum':['LR','TB']},'nodes':array(obj({'id':NONEMPTY,'label':NONEMPTY,'kind':{'enum':['process','decision','terminal','data','neuron']},'color':{'enum':['cyan','green','yellow','white']},'position':array({'type':'number','minimum':0,'maximum':1},2)},['id','label']),1),'edges':array(obj({'from':NONEMPTY,'to':NONEMPTY,'label':S,'feedback':{'type':'boolean'}},['from','to'])),'caption':S},['nodes','edges']),
    block('chart',{'kind':{'enum':['bar','line']},'categories':array(NONEMPTY,1),'series':array(obj({'name':NONEMPTY,'values':array(NUM,1)},['name','values']),1),'y_title':S,'caption':S},['kind','categories','series'])
]
blocks[4]['properties']['nodes']['items']['properties']['position']['maxItems']=2
blocks[0]['properties'].update(font_size={'type':'number','minimum':16,'maximum':60},panel={'enum':['outline','gradient']},align={'enum':['left','center']})
blocks[3]['properties']['fill_height']={'type':'boolean'}
HEX={'type':'string','pattern':'^[0-9A-Fa-f]{6}$'}
blocks[0]['properties'].update(
    first_line_indent={'type':'number','minimum':0,'maximum':4},
    paragraph_space={'type':'number','minimum':0,'maximum':40},
    bullet=obj({'symbol':{'enum':['●','○','■','□']},'color':HEX},['symbol']),
    gradient=obj({'colors':{'type':'array','items':HEX,'minItems':2,'maxItems':2},'kind':{'enum':['linear','radial']},'angle':NUM,'focus':{'type':'array','items':{'type':'number','minimum':0,'maximum':1},'minItems':2,'maxItems':2}},['colors']))
blocks[3]['properties'].update(hide_header={'type':'boolean'},style={'enum':['grid','bands','underline','borderless']})
blocks[5]['properties'].update(palette=array(HEX,1),vary_categories={'type':'boolean'})
blocks[4]['properties']['nodes']['items']['properties']['box']={'type':'array','items':NUM,'minItems':4,'maxItems':4}
blocks[4]['properties']['edges']['items']['properties']['route']={'type':'array','minItems':2,'items':{'type':'array','items':NUM,'minItems':2,'maxItems':2}}
schema = {'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://example.org/scientific-ppt/deck.schema.json',**obj({'version':{'const':'1.0'},'title':NONEMPTY,'author':S,'language':S,'slides':array(obj({'title':NONEMPTY,'layout':{'enum':['auto','stack','split','gallery','figure']},'notes':S,'blocks':array({'oneOf':blocks},1)},['title','blocks']),1)},['version','title','slides'])}
path = ROOT / 'references' / 'deck.schema.json'
schema['properties']['slides']['items']['properties']['layout']['enum'] += ['composed','cover','end']
schema['properties']['english_title']=S
path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
