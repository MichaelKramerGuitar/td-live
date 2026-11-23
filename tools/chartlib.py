"""Charts and the synesthesia palette, as plain Python (no TouchDesigner needed).

Used by the CLI (tools/check_book.py), the tests, and later by TouchDesigner the same way TDExperiement shares
metabolism_core.py: one source of truth, testable outside TD.

    import chartlib as cl
    chart = cl.load_chart('charts/gangster_flick.yaml')
    cl.form_plan(chart)          # [('A', 1, 8), ('A', 2, 8), ...]  (section, pass, bars)
    cl.total_bars(chart)         # 84
    pal = cl.load_palette()
    cl.color_for('Db', pal)      # '#C4EBD9'  (spelling decides: C# would be dark brown)
"""
import json
import os
import re

import yaml

try:
    from . import harmony  # noqa: F401  (package import)
except ImportError:
    import harmony

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(ROOT, 'charts', 'schema', 'chart.schema.json')
PALETTE_PATH = os.path.join(ROOT, 'synesthesia', 'palette.yaml')

# ---- spelled pitches ------------------------------------------------------------------------------------
_SPELLED = re.compile(r'^([A-G])(##|#|bb|b)?$')
_NATURAL_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
_ACC = {None: 0, '#': 1, '##': 2, 'b': -1, 'bb': -2}
_CHORD_ROOT = re.compile(r'^([A-G](?:##|#|bb|b)?)')


def parse_spelled(s):
    """'Db' -> ('D', 'b'). Raises ValueError for anything that isn't a single spelled pitch."""
    m = _SPELLED.match(s)
    if not m:
        raise ValueError('not a spelled pitch: %r' % s)
    return m.group(1), m.group(2)


def pitch_class(s):
    """Sounding pitch class 0..11 (C = 0). C# and Db both give 1: the sound can't tell them apart."""
    letter, acc = parse_spelled(s)
    return (_NATURAL_PC[letter] + _ACC[acc]) % 12


def fifths_index(s):
    """Position on the circle of fifths, C at the top = 0, clockwise G = 1, D = 2 ... F = 11."""
    return (pitch_class(s) * 7) % 12


def chord_root(symbol):
    """'Abm9' -> 'Ab', 'C#7alt' -> 'C#'. The spelled root that picks the colour."""
    m = _CHORD_ROOT.match(symbol)
    if not m:
        raise ValueError('no spelled root in chord symbol %r' % symbol)
    return m.group(1)


def alternatives(s):
    """'F#/Gb' -> ['F#', 'Gb'] (spelling still undecided); 'C' -> ['C']."""
    return s.split('/')


# ---- palette --------------------------------------------------------------------------------------------
def load_palette(path=PALETTE_PATH):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def color_for(spelled, palette):
    """Starting colour for a spelled pitch (or 'F#/Gb': the first spelling). Uses `fallback` for
    spellings Michael hasn't given a colour yet (e.g. Cb -> B)."""
    s = alternatives(spelled)[0]
    parse_spelled(s)
    cols = palette['colors']
    if s in cols:
        return cols[s]['start']
    fb = palette.get('fallback', {}).get(s)
    if fb and fb in cols:
        return cols[fb]['start']
    return cols[enharmonic_fallback(s)]['start']


def enharmonic_fallback(s):
    """A spelling with no colour of its own (e.g. Bbb, F##): the natural with the same sound if there is
    one, otherwise the single sharp/flat in the same direction (Fbb -> Eb, C## -> D). Michael hasn't given
    these colours yet (palette open_questions), so this is a stand-in."""
    letter, acc = parse_spelled(s)
    p = pitch_class(s)
    for n in _NATURAL_PC:
        if _NATURAL_PC[n] == p:
            return n
    flat = (acc or '').startswith('b')
    for n in _NATURAL_PC:
        cand = n + ('b' if flat else '#')
        if pitch_class(cand) == p:
            return cand
    raise KeyError('no colour for %s' % s)


def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


# ---- charts ---------------------------------------------------------------------------------------------
def load_chart(path, validate=True):
    chart = resolve(_read(path), os.path.dirname(path))
    if validate:
        problems = check_chart(chart)
        if problems:
            raise ValueError('%s:\n  - %s' % (path, '\n  - '.join(problems)))
    return chart


def _read(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def resolve(chart, folder=None, _seen=()):
    """Chart inheritance. `extends: <id>` copies the parent chart (charts/<id>.yaml) and lets this chart
    replace any top-level field; `changes_patch: {section: {bar number: [[symbol, beats], ...]}}` then
    replaces single bars (1-based). Lets a variant (basic blues, bebop blues, a reharm) say only what differs."""
    import copy
    parent_id = chart.get('extends')
    if not parent_id:
        return chart
    if parent_id in _seen:
        raise ValueError('extends loop: %s' % ' -> '.join(_seen + (parent_id,)))
    folder = folder or os.path.join(ROOT, 'charts')
    parent = resolve(_read(os.path.join(folder, parent_id + '.yaml')), folder, _seen + (chart.get('id', '?'),))
    merged = copy.deepcopy(parent)
    for k, v in chart.items():
        if k not in ('extends', 'changes_patch'):
            merged[k] = copy.deepcopy(v)
    for sec, bars in (chart.get('changes_patch') or {}).items():
        if sec not in merged.get('changes', {}):
            raise ValueError('changes_patch: section %r not in %s' % (sec, parent_id))
        for bar_no, content in bars.items():
            merged['changes'][sec][int(bar_no) - 1] = content
    merged['extends_from'] = parent_id
    return merged


def schema_problems(chart):
    """JSON-Schema problems (empty list = fine). Skipped if the jsonschema package isn't installed."""
    try:
        import jsonschema
    except ImportError:
        return []
    with open(SCHEMA_PATH, encoding='utf-8') as f:
        schema = json.load(f)
    v = jsonschema.Draft202012Validator(schema)
    return ['%s: %s' % ('/'.join(str(p) for p in e.absolute_path) or '(top)', e.message)
            for e in sorted(v.iter_errors(chart), key=lambda e: list(e.absolute_path))]


def check_chart(chart):
    """Schema problems plus the musical checks a schema can't express."""
    out = schema_problems(chart)
    if out:
        return out
    beats = chart['rhythm']['meter']['beats']
    for a in chart['rhythm'].get('accents', []):
        if not (1 <= a < beats + 1):
            out.append('rhythm/accents: %s is outside a bar of %d beats' % (a, beats))
    names = [s['name'] for s in chart['form']['sections']]
    if len(set(names)) != len(names):
        out.append('form/sections: section names must be unique')
    for n in chart['form'].get('order', []):
        if n not in names:
            out.append('form/order: unknown section %r' % n)
    bars_by_name = {s['name']: section_bars(s) for s in chart['form']['sections']}
    roman = chart.get('changes_notation') == 'roman'
    if roman and chart.get('default_key') and chart['default_key'] not in harmony.KEYS:
        out.append('default_key %r is not one of %s' % (chart['default_key'], ', '.join(harmony.KEYS)))
    for name, bars in (chart.get('changes') or {}).items():
        if name not in bars_by_name:
            out.append('changes: unknown section %r' % name)
            continue
        if len(bars) != bars_by_name[name]:
            out.append('changes/%s: %d bars written, form says %d' % (name, len(bars), bars_by_name[name]))
        for i, bar in enumerate(bars):
            total = sum(e[1] for e in bar)
            if abs(total - beats) > 1e-6:
                out.append('changes/%s bar %d: chords add up to %s beats, meter has %d' % (name, i + 1, total, beats))
            for entry in bar:
                sym = entry[0]
                if len(entry) > 2 and entry[2].get('scale') not in harmony.SCALES:
                    out.append('changes/%s bar %d: unknown scale %r (known: %s)' % (
                        name, i + 1, entry[2].get('scale'), ', '.join(sorted(harmony.SCALES))))
                try:
                    if roman:
                        harmony.chord(sym, chart.get('default_key') or 'C')
                    else:
                        chord_root(sym)
                except ValueError as e:
                    out.append('changes/%s bar %d: %s' % (name, i + 1, e))
    for sec in chart['form']['sections']:
        for k, ph in enumerate(sec.get('phrasings') or []):
            total = sum(g if isinstance(g, int) else sum(g) for g in ph)
            if total != section_bars(sec):
                out.append('form/%s phrasing %d: groups add up to %d bars, section has %d' % (
                    sec['name'], k + 1, total, section_bars(sec)))
    for name, bars in (chart.get('melody') or {}).items():
        if name not in bars_by_name:
            out.append('melody: unknown section %r' % name)
        elif len(bars) > bars_by_name[name]:
            out.append('melody/%s: %d bars written, form says %d' % (name, len(bars), bars_by_name[name]))
    if chart.get('status') == 'playable' and not chart.get('changes'):
        out.append('status is playable but there are no changes')
    return out


def section_bars(section):
    return section['shape'] * section.get('multiplier', 1)


def form_plan(chart):
    """The form as played: [(section name, pass number, bars), ...]."""
    secs = {s['name']: s for s in chart['form']['sections']}
    order = chart['form'].get('order') or [s['name'] for s in chart['form']['sections']]
    plan = []
    for name in order:
        s = secs[name]
        for p in range(s.get('hashes', 0) + 1):
            plan.append((name, p + 1, section_bars(s)))
    return plan


def total_bars(chart):
    return sum(b for _, _, b in form_plan(chart))


def describe(chart):
    """A short human summary, e.g. for the CLI."""
    m = chart['rhythm']['meter']
    lines = ['%s (%s) - %d/%d, %d bars, status: %s' % (chart['title'], chart['id'], m['beats'], m['unit'],
                                                         total_bars(chart), chart.get('status', 'sketch'))]
    for s in chart['form']['sections']:
        plays = s.get('hashes', 0) + 1
        lines.append('  %-3s %3d bars x %d = %d' % (s['name'], section_bars(s), plays, section_bars(s) * plays))
    if chart.get('changes_notation') == 'roman':
        lines.append('  key-free (roman numerals), default key %s' % chart.get('default_key'))
    nodes = chart['pitch'].get('melodic_nodes', [])
    if nodes:
        lines.append('  melodic nodes: ' + ', '.join(nodes))
    return '\n'.join(lines)


def phrasing_groups(section, choice=0):
    """The section's phrase groups for hearing `choice` (wraps): [[sub, sub], [sub]] — always lists of ints.
    No phrasings: one group of shape x multiplier bars, its sub-groups the zig-zag passes."""
    ph = section.get('phrasings')
    if not ph:
        return [[section['shape']] * section.get('multiplier', 1)]
    return [g if isinstance(g, list) else [g] for g in ph[choice % len(ph)]]


def phrasing_text(section, choice=0):
    """'2+8 · 4' for display."""
    if not section.get('phrasings'):
        return 'as written'
    return ' \u00b7 '.join('+'.join(str(x) for x in g) for g in phrasing_groups(section, choice))


def melody_plan(chart, key, plan):
    """Melodic nodes per chorus bar: {bar: [spelled notes]} following the form plan (from form_plan);
    a null bar carries the previous node on (across sections too)."""
    mel = chart.get('melody') or {}
    out, prev, bar = {}, [], 0
    for name, pass_, nbars in plan:
        bars = mel.get(name) or []
        for i in range(nbars):
            bar += 1
            e = bars[i] if i < len(bars) else None
            if e is None:
                cur = prev
            else:
                degs = e if isinstance(e, list) else [e]
                cur = [harmony.spell(key, d) for d in degs]
            out[bar] = cur
            prev = cur
    return out
