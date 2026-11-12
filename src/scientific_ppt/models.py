from dataclasses import dataclass, field
from pathlib import Path
import json
from jsonschema import Draft202012Validator

REFERENCES_DIR = Path(__file__).resolve().parents[2] / 'references'


class LayoutError(ValueError):
    """Content cannot fit without violating a readability or integrity constraint."""


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float

    def as_list(self):
        return [self.x, self.y, self.w, self.h]


@dataclass
class Element:
    block: dict
    box: Box
    role: str = "content"


@dataclass
class Page:
    title: str
    elements: list[Element] = field(default_factory=list)
    notes: str = ""
    source_slide: int = 0
    continuation: int = 1
    layout: str = "stack"


def resource(name):
    return json.loads((REFERENCES_DIR / name).read_text(encoding='utf-8'))


def load_tokens(path=None):
    tokens = json.loads(Path(path).read_text(encoding='utf-8')) if path else resource('design_tokens.json')
    for key in ('canvas','colors','fonts','type','spacing','quality'):
        if key not in tokens:
            raise ValueError(f'Missing design-token section: {key}')
    if min(tokens['canvas'].values()) <= 0 or tokens['spacing']['content_top'] >= tokens['canvas']['height'] - tokens['spacing']['footer']:
        raise ValueError('Invalid canvas or content area')
    return tokens


def validate_deck(deck):
    errors = sorted(Draft202012Validator(resource('deck.schema.json')).iter_errors(deck), key=lambda e:str(e.path))
    if errors:
        raise ValueError('\n'.join(f'{list(e.path)}: {e.message}' for e in errors[:10]))
    for slide in deck['slides']:
        for b in slide['blocks']:
            if b['type'] == 'table':
                n = len(b['columns'])
                if any(len(r['cells']) != n for r in b['rows']):
                    raise ValueError('Every table row must have exactly one cell per column')
                ids = [r['id'] for r in b['rows']]
                if len(ids) != len(set(ids)):
                    raise ValueError('Table row IDs must be unique')
                if 'widths' in b and (len(b['widths']) != n or abs(sum(b['widths'])-1) > .001):
                    raise ValueError('Table widths must match columns and sum to 1')
            if b['type'] == 'diagram':
                ids = [n['id'] for n in b['nodes']]
                if len(ids) != len(set(ids)):
                    raise ValueError('Diagram node IDs must be unique')
                if any(e['from'] not in ids or e['to'] not in ids for e in b['edges']):
                    raise ValueError('Diagram edges must refer to existing nodes')
            if b['type'] == 'chart':
                if any(len(s['values']) != len(b['categories']) for s in b['series']):
                    raise ValueError('Chart category and series lengths differ')
    return deck
