"""Refresh routing/gpt_rows.json from Artificial Analysis model pages.

Usage: python3 -I routing/refresh.py routing/gpt_rows.json
"""
import sys, json, re
import urllib.request

EFFORT = {None: 0, 'low': 1, 'medium': 2, 'high': 3, 'xhigh': 4, 'max': 5}


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    s = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'ignore')
    return s.replace('\\"', '"')  # data sits in an escaped RSC payload


def headline(x):
    """First nested 'headline' speed block (AA moved speed there in 2026-11)."""
    if isinstance(x, dict):
        h = x.get('headline')
        if isinstance(h, dict) and 'outputSpeed' in h:
            return h
        x = x.values()
    if isinstance(x, (list, type({}.values()))):
        for v in x:
            h = headline(v)
            if h:
                return h
    return None


def row(o):
    g = o.get
    r = lambda x, n=3: None if x is None else round(x, n)
    cost = (g('intelligenceIndexCostPerTask') or {}).get('cost') or {}
    ts = g('timescaleData') or {}
    hl = headline(o) or {}
    return {
        'model': o['release']['slug'], 'effort': (g('effort') or {}).get('slug'),
        'intelligence': r(g('intelligenceIndex'), 1),
        'terminal_bench': r(g('terminalBench40')), 'scicode': r(g('scicode')),
        'long_context': r(g('lcr')), 'automation': r(g('automationBenchPartialScore')),
        'gdpval': r(g('gdpvalNormalized')), 'hle': r(g('hle')), 'critpt': r(g('critpt')),
        'hallucination': r(g('omniscienceHallucinationRate')),
        'price_in': g('price1mInputTokens'), 'price_out': g('price1mOutputTokens'),
        'cost_per_task': r(cost.get('total')),
        'sec_per_task': r(g('intelligenceIndexTimePerTask'), 0),
        'out_tokens_per_task': r((g('intelligenceIndexOutputTokensPerTask') or {}).get('output'), 0),
        'tok_per_sec': r(ts.get('medianOutputSpeed') or hl.get('outputSpeed'), 0),
        'ttft_sec': r(ts.get('medianTimeToFirstChunk') or hl.get('timeToFirstToken'), 1),
    }


TRACK = ('gpt-6-2-sol','gpt-6-2-astra','gpt-6-1-terra','gpt-6-1-sol','gpt-6-astra','gpt-6-sol','gpt-6-luna','gpt-5-6-sol','gpt-5-6-terra','gpt-5-6-luna')
dec, recs = json.JSONDecoder(), {}
for t in TRACK:
    try: s = get('https://artificialanalysis.ai/models/' + t)
    except Exception as e: print('ERR', t, e, file=sys.stderr); continue
    for m in re.finditer(r'\{"id":"[0-9a-f-]{36}","slug":"gpt-', s):
        try: o, _ = dec.raw_decode(s, m.start())
        except ValueError: continue
        if (o.get('release') or {}).get('slug') in TRACK and 'intelligenceIndex' in o:
            if len(o) > len(recs.get(o['slug'], {})): recs[o['slug']] = o
rows = sorted((row(o) for o in recs.values()), key=lambda r: (r['model'], EFFORT.get(r['effort'], 9)))
json.dump(rows, open(sys.argv[1], 'w'), indent=1)
for r in rows: print(r['model'], r['effort'], r['intelligence'], r['terminal_bench'], r['hallucination'], r['automation'], r['cost_per_task'], r['sec_per_task'], r['price_in'], r['price_out'], r['tok_per_sec'])
