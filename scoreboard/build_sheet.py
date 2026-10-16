#!/usr/bin/env python3
"""Build the UseThisSI Scoreboard Google Sheet as SpreadsheetML (Excel 2003 XML).

Input : /workspace/usethissi/metrics.csv  (one row per date, COLUMNS order below)
Output: /workspace/usethissi/scoreboard/scoreboard.xml
        /workspace/usethissi/scoreboard/upload_args.json  (args for Drive update_file_content)

Upload (keeps the same file id / URL):
  user-Google-drive update_file_content
    fileId=13vsJlhRDT1PG8zXQEcRcjC1dMlPRW-0-3fQUTc3wTRg
    contentMimeType=application/vnd.ms-excel
    textContent="$file:/workspace/usethissi/scoreboard/scoreboard.xml"

Importer quirks this script works around (found by testing on a scratch copy):
  - ss:Formula must be R1C1; we write A1 and convert.
  - references to quoted sheet names ('Daily Log'!) and any "!" inside a formula get
    mangled, so the only cross-tab read uses INDIRECT("'Daily Log'"&CHAR(33)&...),
    into the helper tab "calc"; everything else reads calc!X (unquoted works).
  - {array literals} break: sparkline options live in calc cells.
  - spaces/+/- in number formats need backslash escapes; "ddd" breaks.
  - freeze panes, hidden gridlines, named ranges, conditional formatting: NOT imported.
    So banding and n/a styling are baked in here, and the log is newest-first.
"""
import csv, json, os, re, sys, datetime as dt
from xml.sax.saxutils import escape

BASE = '/workspace/usethissi'
CSV_PATH = os.environ.get('SCOREBOARD_CSV', f'{BASE}/metrics.csv')
OUT_XML = os.environ.get('SCOREBOARD_XML', f'{BASE}/scoreboard/scoreboard.xml')
OUT_ARGS = f'{BASE}/scoreboard/upload_args.json'
FILE_ID = '13vsJlhRDT1PG8zXQEcRcjC1dMlPRW-0-3fQUTc3wTRg'
LAUNCH = '2026-10-14'  # goal clock start (editable on the Dashboard after upload too)

# ---- schema: (csv key, Daily Log header, section, kind, number format, width pt) ----
# kind: date | int | money | pct | text
COLUMNS = [
    ('date',                 'Date',               'core',   'date',  r'yyyy\-mm\-dd', 66),
    ('subscribers',          'Subscribers \u2605', 'growth', 'int',   '#,##0', 62),
    ('net_new_subs',         'Net new subs',       'growth', 'int',   '#,##0', 50),
    ('referrals',            'Referrals',          'growth', 'int',   '#,##0', 52),
    ('top_signup_source',    'Top signup source',  'growth', 'text',  '@', 80),
    ('site_visitors',        'Site visitors',      'growth', 'int',   '#,##0', 52),
    ('google_indexed_pages', 'Google indexed pages','growth','int',   '#,##0', 56),
    ('search_clicks',        'Search clicks',      'growth', 'int',   '#,##0', 50),
    ('affiliate_clicks',     'Affiliate clicks',   'money',  'int',   '#,##0', 52),
    ('affiliate_revenue',    'Affiliate revenue',  'money',  'money', r'\$#,##0.00', 60),
    ('sponsor_inquiries',    'Sponsor inquiries',  'money',  'int',   '#,##0', 56),
    ('sponsor_revenue',      'Sponsor revenue',    'money',  'money', r'\$#,##0.00', 60),
    ('x_followers',          'X followers',        'brand',  'int',   '#,##0', 52),
    ('x_impressions',        'X impressions',      'brand',  'int',   '#,##0', 60),
    ('x_engagements',        'X engagements',      'brand',  'int',   '#,##0', 60),
    ('x_mentions_replies',   'Mentions + replies', 'brand',  'int',   '#,##0', 58),
    ('open_rate',            'Open rate',          'brand',  'pct',   '0.0%', 48),
    ('click_rate',           'Click rate',         'brand',  'pct',   '0.0%', 48),
    ('tools_listed',         'Tools listed',       'brand',  'int',   '#,##0', 50),
    ('notes',                'Notes  (n/a = not live yet)', 'core', 'text', '@', 300),
]
KEYS = [c[0] for c in COLUMNS]
LET = {k: chr(65 + i) for i, k in enumerate(KEYS)}  # A..T in calc + Daily Log

# palette
NAVY, NAVY2, INK, MUTED, FAINT, LINE, BAND, WHITE = '#0B1220', '#1E293B', '#0F172A', '#64748B', '#94A3B8', '#E2E8F0', '#F8FAFC', '#FFFFFF'
GREEN, AMBER, INDIGO = '#16A34A', '#D97706', '#4F46E5'
GREEN_BG, AMBER_BG, INDIGO_BG = '#F0FDF4', '#FFFBEB', '#EEF2FF'
SEC = {'growth': (GREEN, GREEN_BG), 'money': (AMBER, AMBER_BG), 'brand': (INDIGO, INDIGO_BG), 'core': (NAVY2, '#F1F5F9')}
FONT = 'Inter'

# ---------------- helpers ----------------
def col_num(letters):
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n

def col_let(n):
    s = ''
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

REF = re.compile(r'(?<![A-Za-z0-9_.])((?:calc|Dashboard)!)?\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?(?![A-Za-z0-9_(])')

def to_r1c1(formula):
    """A1 -> absolute R1C1, skipping string literals."""
    out, parts = [], re.split(r'("(?:[^"]|"")*")', formula)
    for p in parts:
        if p.startswith('"'):
            out.append(p); continue
        def rep(m):
            sheet = m.group(1) or ''
            a = f'R{m.group(3)}C{col_num(m.group(2))}'
            if m.group(4):
                a += f':R{m.group(5)}C{col_num(m.group(4))}'
            return sheet + a
        out.append(REF.sub(rep, p))
    f = ''.join(out)
    # guard: no literal "!" outside the sheet prefixes we emit
    assert '!' not in re.sub(r'(calc|Dashboard)!', '', re.sub(r'"(?:[^"]|"")*"', '""', f)), f
    lits = ''.join(re.findall(r'"(?:[^"]|"")*"', f))
    assert not any(ch in lits for ch in '!,()'), 'no ! or , inside formula strings (importer rewrites them): ' + f
    return f

class Styles:
    def __init__(self):
        self.ids, self.xml, self.pct_ids = {}, [], set()
    def get(self, **k):
        key = tuple(sorted((a, tuple(b) if isinstance(b, list) else b) for a, b in k.items()))
        if key in self.ids:
            return self.ids[key]
        sid = f's{len(self.ids) + 1}'
        self.ids[key] = sid
        if '%' in (k.get('fmt') or ''):
            self.pct_ids.add(sid)
        a = []
        h, v, wrap = k.get('h', 'Left'), k.get('v', 'Center'), k.get('wrap', False)
        a.append(f'<Alignment ss:Horizontal="{h}" ss:Vertical="{v}"' + (' ss:WrapText="1"' if wrap else '') + (f' ss:Indent="{k["indent"]}"' if k.get('indent') else '') + '/>')
        b = k.get('borders')
        if b:
            a.append('<Borders>' + ''.join(f'<Border ss:Position="{pos}" ss:LineStyle="Continuous" ss:Weight="{w}" ss:Color="{c}"/>' for pos, w, c in b) + '</Borders>')
        a.append(f'<Font ss:FontName="{k.get("font", FONT)}" ss:Size="{k.get("size", 10)}" ss:Color="{k.get("color", INK)}"' + (' ss:Bold="1"' if k.get('bold') else '') + (' ss:Italic="1"' if k.get('italic') else '') + '/>')
        a.append(f'<Interior ss:Color="{k.get("bg", WHITE)}" ss:Pattern="Solid"/>')
        if k.get('fmt'):
            a.append(f'<NumberFormat ss:Format="{escape(k["fmt"], {chr(34): "&quot;"})}"/>')
        self.xml.append(f'<Style ss:ID="{sid}">' + ''.join(a) + '</Style>')
        return sid

ST = Styles()

class Sheet:
    def __init__(self, name, ncols, widths, base_style):
        self.name, self.ncols, self.widths = name, ncols, widths
        self.cells, self.heights, self.base = {}, {}, base_style
    def set(self, r, c, value=None, formula=None, style=None, across=0, dtype=None):
        self.cells[(r, c)] = dict(v=value, f=formula, s=style or self.base, across=across, t=dtype)
        for k in range(1, across + 1):
            self.cells[(r, c + k)] = 'covered'
    def h(self, r, pts):
        self.heights[r] = pts
    def xml(self, nrows):
        rows = []
        for r in range(1, nrows + 1):
            cs = []
            for c in range(1, self.ncols + 1):
                cell = self.cells.get((r, c))
                if cell == 'covered':
                    continue
                if cell is None:
                    cell = dict(v=None, f=None, s=self.base, across=0, t=None)
                attrs = f' ss:StyleID="{cell["s"]}"'
                if cell['across']:
                    attrs += f' ss:MergeAcross="{cell["across"]}"'
                if cell['f']:
                    attrs += f' ss:Formula="{escape(to_r1c1(cell["f"]), {chr(34): "&quot;"})}"'
                v, t = cell['v'], cell['t']
                if (v is None or v == '') and cell['f'] and cell['s'] in ST.pct_ids:
                    data = '<Data ss:Type="Number">0</Data>'  # String-typed formula cells get % turned into a literal
                elif v is None or v == '':
                    data = '' if not cell['f'] else '<Data ss:Type="String"></Data>'
                elif t == 'date':
                    data = f'<Data ss:Type="DateTime">{v}T00:00:00.000</Data>'
                elif isinstance(v, (int, float)) and not isinstance(v, bool):
                    data = f'<Data ss:Type="Number">{v}</Data>'
                else:
                    data = f'<Data ss:Type="String">{escape(str(v))}</Data>'
                cs.append(f'<Cell{attrs}>{data}</Cell>')
            ht = f' ss:AutoFitHeight="0" ss:Height="{self.heights[r]}"' if r in self.heights else ''
            rows.append(f'<Row{ht}>' + ''.join(cs) + '</Row>')
        cols = ''.join(f'<Column ss:AutoFitWidth="0" ss:Width="{w}"/>' for w in self.widths)
        return (f'<Worksheet ss:Name="{escape(self.name)}"><Table>{cols}' + ''.join(rows) + '</Table></Worksheet>')

# ---------------- load data ----------------
def parse(key, kind, raw):
    raw = (raw or '').strip()
    if raw == '' or raw.lower() in ('n/a', 'na', '-'):
        return None
    if kind == 'date':
        return dt.date.fromisoformat(raw).isoformat()
    if kind == 'text':
        return raw
    s = raw.replace('$', '').replace(',', '')
    if kind == 'pct':
        return float(s[:-1]) / 100 if s.endswith('%') else (float(s) / 100 if float(s) > 1 else float(s))
    n = float(s)
    return int(n) if kind == 'int' and n.is_integer() else n

with open(CSV_PATH, newline='') as f:
    rd = csv.reader(f)
    header = next(rd)
    if header != KEYS:
        sys.exit(f'metrics.csv header mismatch.\n expected: {",".join(KEYS)}\n found:    {",".join(header)}')
    rows = []
    for i, r in enumerate(rd, start=2):
        if not any(x.strip() for x in r):
            continue
        if len(r) != len(KEYS):
            sys.exit(f'metrics.csv line {i}: {len(r)} fields, expected {len(KEYS)} (quote notes that contain commas)')
        rows.append({k: parse(k, kind, r[j]) for j, (k, _, _, kind, _, _) in enumerate(COLUMNS)})
dates = [r['date'] for r in rows]
if len(set(dates)) != len(dates):
    sys.exit('duplicate dates in metrics.csv: ' + ', '.join(sorted({d for d in dates if dates.count(d) > 1})))
rows.sort(key=lambda r: r['date'], reverse=True)  # newest first (no freeze panes via import)

# ================= Daily Log =================
NC = len(COLUMNS)
log = Sheet('Daily Log', NC, [c[5] for c in COLUMNS], ST.get())
log.h(1, 40)
for j, (k, label, sec, kind, fmt, w) in enumerate(COLUMNS, start=1):
    fg, _ = SEC[sec]
    log.set(1, j, label, style=ST.get(bold=True, color=WHITE, bg=fg, h='Center' if kind != 'text' else 'Left', wrap=True, size=9,
                                       borders=[('Bottom', 2, NAVY)]))
for i, r in enumerate(rows, start=2):
    band = WHITE if i % 2 == 0 else BAND
    log.h(i, 30)
    for j, (k, label, sec, kind, fmt, w) in enumerate(COLUMNS, start=1):
        v = r[k]
        edge = [('Bottom', 1, LINE)]
        if v is None and k != 'notes':
            log.set(i, j, 'n/a', style=ST.get(italic=True, color=FAINT, bg=band, h='Center', size=9, borders=edge))
        elif kind == 'date':
            log.set(i, j, v, dtype='date', style=ST.get(bold=True, bg=band, fmt=fmt, h='Left', borders=edge))
        elif kind == 'text':
            log.set(i, j, v or '', style=ST.get(bg=band, wrap=(k == 'notes'), size=9 if k == 'notes' else 10, color=MUTED if k == 'notes' else INK, h='Left', borders=edge))
        else:
            bold = k == 'subscribers'
            log.set(i, j, v, style=ST.get(bg=band, fmt=fmt, h='Right', bold=bold, color=GREEN if bold else INK, borders=edge))
LOG_ROWS = max(len(rows) + 1, 2)

# ================= calc (helper) =================
# A1:T  = Daily Log sorted oldest->newest, "n/a" -> blank
# U = total revenue/day, V = X engagement rate/day, W = visitor->sub conversion/day
# Y/Z  = scalars, rows 10+ = per-metric stats, AI:AJ = goal bar data, AL:AM = sparkline options
N = 2000
calc = Sheet('calc', 40, [60] * 40, ST.get(size=9, color=MUTED))
SRC = 'INDIRECT("\'Daily Log\'"&CHAR(33)&"A2:T%d")' % N
SRCA = 'INDIRECT("\'Daily Log\'"&CHAR(33)&"A2:A%d")' % N
SORTED = f'SORT(FILTER({SRC},ISNUMBER({SRCA})),1,TRUE)'
calc.set(1, 1, formula=f'=IFERROR(ARRAYFORMULA(IF({SORTED}="n/a","",{SORTED})),"")')
rg = lambda c: f'${c}$1:${c}${N}'
A = rg('A')
calc.set(1, 21, formula=f'=ARRAYFORMULA(IF({A}="","",IF(ISNUMBER({rg("J")}),{rg("J")},0)+IF(ISNUMBER({rg("L")}),{rg("L")},0)))')
calc.set(1, 22, formula=f'=ARRAYFORMULA(IF(ISNUMBER({rg("O")})*ISNUMBER({rg("N")}),IF({rg("N")}>0,{rg("O")}/{rg("N")},""),""))')
calc.set(1, 23, formula=f'=ARRAYFORMULA(IF(ISNUMBER({rg("C")})*ISNUMBER({rg("F")}),IF({rg("F")}>0,{rg("C")}/{rg("F")},""),""))')
scal = [
    ('latest date', f'=IF(COUNT({A})=0,"",MAX({A}))'),
    ('latest - 7', '=IF($AA$1="","",$AA$1-7)'),
    ('previous logged date', f'=IF($AA$1="",0,MAXIFS({A},{A},"<"&$AA$1))'),
    ('month start', '=IF($AA$1="","",DATE(YEAR($AA$1),MONTH($AA$1),1))'),
    ('days logged', f'=COUNT({A})'),
    ('MTD revenue', f'=IF($AA$1="",0,SUMIFS({rg("U")},{A},">="&$AA$4,{A},"<="&$AA$1))'),
    ('lifetime revenue', f'=SUM({rg("U")})'),
    ('first revenue date', f'=IF(COUNTIF({rg("U")},">0")=0,"",MINIFS({A},{rg("U")},">0"))'),
]
for i, (lab, f) in enumerate(scal, start=1):
    calc.set(i, 25, lab)
    calc.set(i, 27, formula=f)
calc.set(9, 25, 'helper tab: auto-calculated, do not edit')
STATS = ['subscribers', 'net_new_subs', 'referrals', 'top_signup_source', 'site_visitors', 'google_indexed_pages', 'search_clicks',
         'affiliate_clicks', 'affiliate_revenue', 'sponsor_inquiries', 'sponsor_revenue', 'x_followers', 'x_impressions',
         'x_engagements', 'x_mentions_replies', 'open_rate', 'click_rate', 'tools_listed', 'total_revenue', 'engagement_rate', 'conversion']
LET2 = dict(LET, total_revenue='U', engagement_rate='V', conversion='W')
SR = {}  # key -> calc row
for i, k in enumerate(STATS, start=10):
    c = LET2[k]; SR[k] = i; cn = col_num(c)
    calc.set(i, 25, k)
    calc.set(i, 27, formula=f'=IF($AA$1="","",IFERROR(INDEX({rg(c)},MATCH($AA$1,{A},0)),""))')            # AA latest
    calc.set(i, 28, formula=f'=IF($AA$3=0,"",IFERROR(INDEX({rg(c)},MATCH($AA$3,{A},0)),""))')             # AB previous log
    calc.set(i, 29, formula=f'=IF($AA$1="","",IFERROR(VLOOKUP($AA$2,$A$1:$W${N},{cn},TRUE),""))')          # AC value 7d ago
    calc.set(i, 30, formula=f'=IF($AA$1="",0,SUMIFS({rg(c)},{A},">"&$AA$2,{A},"<="&$AA$1))')               # AD sum 7d
    calc.set(i, 31, formula=f'=IF($AA$1="",0,SUMPRODUCT(ISNUMBER({rg(c)})*({A}>$AA$2)*({A}<=$AA$1)))')      # AE count 7d
    calc.set(i, 32, formula=f'=IF($AA$1="",0,SUMIFS({rg(c)},{A},">"&($AA$1-14),{A},"<="&$AA$2))')          # AF sum prev 7d
    calc.set(i, 33, formula=f'=IF($AA$1="",0,SUMPRODUCT(ISNUMBER({rg(c)})*({A}>$AA$1-14)*({A}<=$AA$2)))')  # AG count prev 7d
    calc.set(i, 34, formula=f'=COUNT({rg(c)})')                                                          # AH count all
# NOTE: column Z (26) is never referenced: the importer maps R?C26 to column A.
Z = lambda k: f'calc!$AA${SR[k]}'   # latest
AA = lambda k: f'calc!$AB${SR[k]}'  # previous logged day
AB = lambda k: f'calc!$AC${SR[k]}'  # 7 days ago
S7 = lambda k: f'calc!$AD${SR[k]}'
C7 = lambda k: f'calc!$AE${SR[k]}'
SP = lambda k: f'calc!$AF${SR[k]}'
CP = lambda k: f'calc!$AG${SR[k]}'
CA = lambda k: f'calc!$AH${SR[k]}'
# sparkline options (key/value pairs)
opts = {
    'bar':   [('charttype', 'bar'), ('color1', GREEN), ('color2', '#E5E7EB')],
    'barA':  [('charttype', 'bar'), ('color1', AMBER), ('color2', '#E5E7EB')],
    'line':  [('charttype', 'line'), ('color', GREEN), ('linewidth', 2), ('empty', 'ignore')],
    'lineI': [('charttype', 'line'), ('color', INDIGO), ('linewidth', 2), ('empty', 'ignore')],
    'col':   [('charttype', 'column'), ('color', '#94A3B8'), ('highcolor', GREEN), ('empty', 'ignore'), ('ymin', 0)],
    'colA':  [('charttype', 'column'), ('color', '#FCD34D'), ('highcolor', AMBER), ('empty', 'ignore'), ('ymin', 0)],
    'colI':  [('charttype', 'column'), ('color', '#A5B4FC'), ('highcolor', INDIGO), ('empty', 'ignore'), ('ymin', 0)],
}
OPT = {}
r0 = 10
for name, pairs in opts.items():
    calc.set(r0 - 1, 38, name)
    OPT[name] = f'calc!$AL${r0}:$AM${r0 + len(pairs) - 1}'
    for kk, vv in pairs:
        calc.set(r0, 38, kk); calc.set(r0, 39, vv); r0 += 1
    r0 += 1
CALC_ROWS = max(r0, 10 + len(STATS))

# ================= Dashboard =================
W = [10, 156, 60, 60, 60, 60, 124, 10]
dash = Sheet('Dashboard', 8, W, ST.get())
B, Cc, D, E, F, G = 2, 3, 4, 5, 6, 7
row = 1
def sp(h):
    global row
    dash.h(row, h); row += 1
NA = '"n/a"'
def numcell(expr, fmt_text):
    return f'=IF(ISNUMBER({expr}),{expr},{NA})'

# header band
dash.h(1, 8)
for c in range(1, 9):
    dash.set(1, c, style=ST.get(bg=NAVY))
dash.h(2, 34)
dash.set(2, 1, style=ST.get(bg=NAVY))
dash.set(2, B, 'UseThisSI', style=ST.get(bg=NAVY, color=WHITE, bold=True, size=20, v='Bottom'), across=2)
dash.set(2, E, formula='=IF(calc!$AA$1="","No data yet","Updated "&TEXT(calc!$AA$1,"mmm d yyyy"))',
         style=ST.get(bg=NAVY, color='#CBD5E1', size=9, h='Right', v='Bottom'), across=2)
dash.set(2, 8, style=ST.get(bg=NAVY))
dash.h(3, 20)
dash.set(3, 1, style=ST.get(bg=NAVY))
dash.set(3, B, 'Scoreboard  \u00b7  AI tools directory + weekday AI newsletter  \u00b7  North star: subscribers',
         style=ST.get(bg=NAVY, color=FAINT, size=9, v='Top'), across=5)
dash.set(3, 8, style=ST.get(bg=NAVY))
dash.h(4, 4)
for c in range(1, 9):
    dash.set(4, c, style=ST.get(bg=GREEN))
row = 5
sp(12)

# KPI cards (rows 6-8)
card_lab = ST.get(bg='#F1F5F9', color=MUTED, size=8, bold=True, indent=1, borders=[('Top', 1, LINE)])
card_val = ST.get(bg='#F1F5F9', color=INK, size=22, bold=True, indent=1)
card_sub = ST.get(bg='#F1F5F9', color=MUTED, size=8, indent=1, borders=[('Bottom', 1, LINE)])
hero_lab = ST.get(bg=NAVY, color='#86EFAC', size=8, bold=True, indent=1)
hero_val = ST.get(bg=NAVY, color=WHITE, size=30, bold=True, indent=1, fmt='#,##0')
hero_sub = ST.get(bg=NAVY, color='#CBD5E1', size=8, indent=1)
gap = ST.get()
dash.h(6, 18); dash.h(7, 42); dash.h(8, 18)
dash.set(6, B, 'SUBSCRIBERS  \u2605  NORTH STAR', style=hero_lab)
dash.set(7, B, formula=numcell(Z('subscribers'), ''), style=hero_val)
dash.set(8, B, formula=(f'=IF(ISNUMBER({Z("net_new_subs")}),TEXT({Z("net_new_subs")},"+0;-0;0")&" today","")'
                        f'&IF(ISNUMBER({AB("subscribers")}),"  \u00b7  "&TEXT({Z("subscribers")}-{AB("subscribers")},"+0;-0;0")&" vs 7d ago","  \u00b7  WoW after day 8")'), style=hero_sub)
def card(c, label, valexpr, fmt, subf):
    dash.set(6, c, label, style=card_lab, across=1)
    dash.set(7, c, formula=valexpr, style=ST.get(bg='#F1F5F9', color=INK, size=20, bold=True, indent=1, fmt=fmt), across=1)
    dash.set(8, c, formula=subf, style=card_sub, across=1)
def delta_txt(k):
    return (f'=IF(ISNUMBER({AA(k)})*ISNUMBER({Z(k)}),TEXT({Z(k)}-{AA(k)},"+0;-0;0")&" since last log","first log")'
            f'&IF(ISNUMBER({AB(k)})*ISNUMBER({Z(k)}),"  \u00b7  "&TEXT({Z(k)}-{AB(k)},"+0;-0;0")&" 7d","")')
card(Cc, 'X FOLLOWERS', numcell(Z('x_followers'), ''), '#,##0', delta_txt('x_followers'))
card(E, 'TOOLS LISTED', numcell(Z('tools_listed'), ''), '#,##0', delta_txt('tools_listed'))
dash.set(6, G, 'REVENUE  \u00b7  LIFETIME', style=card_lab)
dash.set(7, G, formula='=calc!$AA$7', style=ST.get(bg='#F1F5F9', color=INK, size=20, bold=True, indent=1, fmt=r'\$#,##0.00'))
dash.set(8, G, formula='="MTD "&TEXT(calc!$AA$6,"$0.00")', style=card_sub)
row = 9
sp(6)
# latest note
dash.h(10, 30)
dash.set(10, B, formula=f'=IF(calc!$AA$1="","",IFERROR("Latest note:  "&INDEX(calc!$T$1:$T${N},MATCH(calc!$AA$1,calc!$A$1:$A${N},0)),""))',
         style=ST.get(color=MUTED, italic=True, size=8, wrap=True, v='Top'), across=5)
row = 11
sp(8)

def section(title, color, right=''):
    global row
    dash.h(row, 24)
    dash.set(row, B, title, style=ST.get(bold=True, size=11, color=color, v='Bottom', borders=[('Bottom', 2, color)]), across=3)
    dash.set(row, F, right, style=ST.get(size=8, color=FAINT, h='Right', v='Bottom', borders=[('Bottom', 2, color)]), across=1)
    row += 1
def colheads(labels):
    global row
    dash.h(row, 18)
    st = ST.get(size=8, color=FAINT, bold=True, h='Right')
    stl = ST.get(size=8, color=FAINT, bold=True)
    dash.set(row, B, labels[0], style=stl)
    dash.set(row, Cc, labels[1], style=st)
    dash.set(row, D, labels[2], style=st)
    dash.set(row, E, labels[3], style=st)
    dash.set(row, F, labels[4], style=ST.get(size=8, color=FAINT, bold=True, h='Center'), across=1)
    row += 1

# ---- GOALS ----
section('GOALS', NAVY, 'clock starts at launch date (bottom)')
colheads(['Goal', 'Target', 'Now', '', 'Progress'])
START = None  # filled after we know the settings row
goals = [  # label, target, current expr, due offset expr (uses START), bar option
    ('1 week  \u00b7  Subscribers (stretch 50)', 25, Z('subscribers'), 'START+7', 'bar'),
    ('1 month  \u00b7  Subscribers (stretch 500)', 300, Z('subscribers'), 'EDATE(START,1)', 'bar'),
    ('1 month  \u00b7  Tools listed', 150, Z('tools_listed'), 'EDATE(START,1)', 'bar'),
    ('1 year  \u00b7  Subscribers', 10000, Z('subscribers'), 'EDATE(START,12)', 'bar'),
    ('First dollar of revenue', 1, 'calc!$AA$7', None, 'barA'),
]
goal_rows = []
for gi, g in enumerate(goals):
    goal_rows.append(row); row += 1
GOAL_END = row
sp(10)

# ---- metric tables ----
lab = ST.get(indent=1, borders=[('Bottom', 1, LINE)])
labstar = ST.get(indent=1, bold=True, borders=[('Bottom', 1, LINE)])
def vstyle(fmt, bold=False, color=INK):
    return ST.get(h='Right', fmt=fmt, bold=bold, color=color, borders=[('Bottom', 1, LINE)])
wow_st = ST.get(h='Right', size=9, color=MUTED, borders=[('Bottom', 1, LINE)])
trend_st = ST.get(borders=[('Bottom', 1, LINE)])
def fmt_of(k):
    return {'int': '#,##0', 'money': r'\$#,##0.00', 'pct': '0.0%', 'text': '@'}[[c for c in COLUMNS if c[0] == k][0][3]]
def trend(k, opt):
    c = LET2[k]
    return (f'=IF({CA(k)}<2,"",SPARKLINE(FILTER(calc!${c}$1:${c}${N},calc!$A$1:$A${N}<>""),{OPT[opt]}))')
def pct_wow(cur, prev, ok):
    return f'=IF(AND({ok},{prev}<>0),IF({cur}>={prev},"\u25b2 ","\u25bc ")&TEXT(ABS({cur}/{prev}-1),"0%"),"\u2014")'
def metric(label, kind, k, opt='col', star=False, fmt=None):
    global row
    dash.h(row, 22)
    dash.set(row, B, label, style=labstar if star else lab)
    fm = fmt or (fmt_of(k) if k in LET else '0.0%')
    if kind == 'stock':
        dash.set(row, Cc, formula=numcell(Z(k), ''), style=vstyle(fm, bold=star, color=GREEN if star else INK))
        dash.set(row, D, formula=f'=IF(ISNUMBER({AB(k)})*ISNUMBER({Z(k)}),{Z(k)}-{AB(k)},"\u2014")', style=vstyle(r'\+#,##0;\-#,##0;0'))
        dash.set(row, E, formula=pct_wow(Z(k), AB(k), f'ISNUMBER({AB(k)})*ISNUMBER({Z(k)})'), style=wow_st)
    elif kind == 'flow':
        dash.set(row, Cc, formula=numcell(Z(k), ''), style=vstyle(fm))
        dash.set(row, D, formula=f'=IF({C7(k)}>0,{S7(k)},{NA})', style=vstyle(fm))
        dash.set(row, E, formula=pct_wow(S7(k), SP(k), f'{CP(k)}>0'), style=wow_st)
    elif kind == 'rate':
        dash.set(row, Cc, formula=numcell(Z(k), ''), style=vstyle('0.0%'))
        dash.set(row, D, formula=f'=IF({C7(k)}>0,{S7(k)}/{C7(k)},{NA})', style=vstyle('0.0%'))
        dash.set(row, E, formula=(f'=IF(AND({C7(k)}>0,{CP(k)}>0),IF({S7(k)}/{C7(k)}>={SP(k)}/{CP(k)},"\u25b2 ","\u25bc ")'
                                  f'&TEXT(ABS({S7(k)}/{C7(k)}-{SP(k)}/{CP(k)})*100,"0.0")&" pts","\u2014")'), style=wow_st)
    elif kind == 'ratio':  # num/den keys, 7d = sum/sum
        num, den = k
        dash.set(row, Cc, formula=f'=IF(AND(ISNUMBER({Z(num)}),ISNUMBER({Z(den)})),IF({Z(den)}>0,{Z(num)}/{Z(den)},{NA}),{NA})', style=vstyle('0.0%'))
        dash.set(row, D, formula=f'=IF(AND({C7(num)}>0,{C7(den)}>0,{S7(den)}>0),{S7(num)}/{S7(den)},{NA})', style=vstyle('0.0%'))
        cur, prev = f'({S7(num)}/{S7(den)})', f'({SP(num)}/{SP(den)})'
        dash.set(row, E, formula=(f'=IF(AND({C7(num)}>0,{C7(den)}>0,{S7(den)}>0,{CP(num)}>0,{CP(den)}>0,{SP(den)}>0),IF({cur}>={prev},"\u25b2 ","\u25bc ")'
                                  f'&TEXT(ABS({cur}-{prev})*100,"0.0")&" pts","\u2014")'), style=wow_st)
        k = num if den != 'x_impressions' else 'engagement_rate'
        k = 'conversion' if den == 'site_visitors' else k
    elif kind == 'text':
        dash.set(row, Cc, formula=f'=IF(LEN({Z(k)})=0,{NA},{Z(k)})', style=ST.get(h='Right', borders=[('Bottom', 1, LINE)]), across=1)
        dash.set(row, E, '', style=wow_st)
        dash.set(row, F, '', style=trend_st, across=1)
        row += 1; return
    dash.set(row, F, formula=trend(k, opt), style=trend_st, across=1)
    row += 1

section('GROWTH', GREEN, 'n/a = not live yet')
colheads(['Metric', 'Latest', '7 days', 'WoW', 'Trend'])
metric('Subscribers  \u2605', 'stock', 'subscribers', 'line', star=True)
metric('Net new subs', 'flow', 'net_new_subs', 'col')
metric('Referrals', 'flow', 'referrals', 'col')
metric('Top signup source', 'text', 'top_signup_source')
metric('Site visitors', 'flow', 'site_visitors', 'col')
metric('Visitor \u2192 sub conversion', 'ratio', ('net_new_subs', 'site_visitors'), 'col')
metric('Google indexed pages', 'stock', 'google_indexed_pages', 'line')
metric('Search clicks', 'flow', 'search_clicks', 'col')
sp(10)

section('MONEY', AMBER, 'USD  \u00b7  revenue logged on the day it is earned')
colheads(['Metric', 'Latest', '7 days', 'WoW', 'Trend'])
metric('Affiliate clicks', 'flow', 'affiliate_clicks', 'colA')
metric('Affiliate revenue', 'flow', 'affiliate_revenue', 'colA')
metric('Sponsor inquiries', 'flow', 'sponsor_inquiries', 'colA')
metric('Sponsor revenue', 'flow', 'sponsor_revenue', 'colA')
# revenue summary rows
def money_row(label, formula, fmt, note_formula=''):
    global row
    dash.h(row, 22)
    dash.set(row, B, label, style=lab)
    dash.set(row, Cc, formula=formula, style=vstyle(fmt, bold=True), across=1)
    dash.set(row, E, formula=note_formula or None, value='' if not note_formula else None, style=ST.get(size=8, color=MUTED, h='Right', borders=[('Bottom', 1, LINE)]), across=2)
    row += 1
money_row('Revenue this month (running)', '=calc!$AA$6', r'\$#,##0.00', '=IF(calc!$AA$1="","",TEXT(calc!$AA$4,"mmmm yyyy")&" to date")')
money_row('Revenue per subscriber (MTD)', f'=IF(N({Z("subscribers")})>0,calc!$AA$6/{Z("subscribers")},{NA})', r'\$#,##0.000', '="industry note: $0.05-$0.50/sub/mo is typical early"')
money_row('Lifetime revenue', '=calc!$AA$7', r'\$#,##0.00', '=IF(calc!$AA$8="","first dollar not earned yet","first dollar on "&TEXT(calc!$AA$8,"mmm d yyyy"))')
sp(10)

section('BRAND', INDIGO)
colheads(['Metric', 'Latest', '7 days', 'WoW', 'Trend'])
metric('X followers', 'stock', 'x_followers', 'lineI')
metric('X impressions', 'flow', 'x_impressions', 'colI')
metric('X engagement rate', 'ratio', ('x_engagements', 'x_impressions'), 'colI')
metric('X mentions + replies', 'flow', 'x_mentions_replies', 'colI')
metric('Newsletter open rate', 'rate', 'open_rate', 'colI')
metric('Newsletter click rate', 'rate', 'click_rate', 'colI')
metric('Directory tools listed', 'stock', 'tools_listed', 'lineI')
sp(10)

# ---- charts ----
section('CHARTS', NAVY, 'fill in from day 2')
def chart(title, k, opt, h=96):
    global row
    dash.h(row, 18)
    dash.set(row, B, title, style=ST.get(size=9, bold=True, color=MUTED), across=5)
    row += 1
    dash.h(row, h)
    c = LET2[k]
    dash.set(row, B, formula=(f'=IF({CA(k)}<2,"Chart appears once 2+ days are logged  \u00b7  "&TEXT({CA(k)},"0")&" so far",'
                              f'SPARKLINE(FILTER(calc!${c}$1:${c}${N},calc!$A$1:$A${N}<>""),{OPT[opt]}))'),
             style=ST.get(bg=BAND, color=FAINT, italic=True, size=9, h='Center', borders=[('Top', 1, LINE), ('Bottom', 1, LINE), ('Left', 1, LINE), ('Right', 1, LINE)]), across=5)
    row += 1
    sp(6)
chart('Subscribers over time', 'subscribers', 'line')
chart('X followers over time', 'x_followers', 'lineI')
chart('Net new subscribers per day', 'net_new_subs', 'col', h=70)
sp(6)

# ---- settings / footer ----
SETROW = row
dash.h(row, 22)
dash.set(row, B, 'Launch date (goal clock start)', style=ST.get(size=9, color=MUTED, borders=[('Top', 1, LINE)]))
dash.set(row, Cc, LAUNCH, dtype='date', style=ST.get(bg='#FEF9C3', bold=True, fmt=r'yyyy\-mm\-dd', h='Center', borders=[('Top', 1, LINE)]), across=1)
dash.set(row, E, '\u2190 editable; deadlines update', style=ST.get(size=8, color=FAINT, borders=[('Top', 1, LINE)]), across=2)
row += 1
dash.h(row, 30)
dash.set(row, B, 'Data source: Daily Log tab (one row per day, added nightly ~8 PM PT). Everything on this tab is a formula. See Guide for definitions.',
         style=ST.get(size=8, color=FAINT, italic=True, wrap=True, v='Top'), across=5)
row += 1
DASH_ROWS = row + 2
START = f'$C${SETROW}'

# fill goal rows now that START is known
for (label, target, cur, due, opt), r in zip(goals, goal_rows):
    dash.h(r, 24)
    dash.set(r, B, label, style=lab)
    dash.set(r, Cc, target, style=vstyle(r'\$#,##0' if opt == 'barA' else '#,##0'))
    dash.set(r, D, formula=f'=N({cur})', style=vstyle(r'\$#,##0.00' if opt == 'barA' else '#,##0', bold=True))
    gi = goal_rows.index(r)
    calc.set(30 + gi, 35, formula=f'=MIN(N({cur}),{target})')
    calc.set(30 + gi, 36, formula=f'=MAX({target}-N({cur}),0)')
    dash.set(r, E, formula=f'=SPARKLINE(calc!$AI${30 + gi}:$AJ${30 + gi},{OPT[opt]})', style=trend_st, across=1)
    if due:
        d = due.replace('START', START)
        status = (f'=TEXT(MIN(N({cur})/{target},1),"0%")&"  \u00b7  "&IF(N({cur})>={target},"hit \u2713",'
                  f'IF({d}-TODAY()<0,"missed "&TEXT({d},"mmm d"),TEXT({d}-TODAY(),"0")&"d left  \u00b7  need "'
                  f'&TEXT(({target}-N({cur}))/MAX(1,{d}-TODAY()),"0.0")&"/day"))')
    else:
        status = f'=IF(N({cur})>={target},"\u2713 earned","not yet  \u00b7  $0 so far")'
    dash.set(r, G, formula=status, style=ST.get(size=8, color=MUTED, h='Right', borders=[('Bottom', 1, LINE)]))
calc.set(29, 35, 'goal bar filled'); calc.set(29, 36, 'goal bar remaining')

# white canvas on dashboard to hide gridlines
for r in range(1, DASH_ROWS + 1):
    for c in range(1, 9):
        dash.cells.setdefault((r, c), dict(v=None, f=None, s=gap, across=0, t=None))

# ================= Guide =================
WHY = {
 'date': ('Day the numbers describe (PT).', 'one row per day; newest on top', '-'),
 'subscribers': ('North star. Audience size drives sponsor price and affiliate volume.', 'total active subscribers at end of day', 'beehiiv'),
 'net_new_subs': ('Daily growth velocity; tells you if what you did today worked.', 'new minus unsubscribes today', 'beehiiv'),
 'referrals': ('Word of mouth is the cheapest, highest-intent channel.', 'subs that came from referral links today', 'beehiiv referral program'),
 'top_signup_source': ('Tells you which channel to double down on.', 'largest signup source today (X, site, referral, search...)', 'beehiiv acquisition sources'),
 'site_visitors': ('Top of the funnel for both the directory and signups.', 'unique visitors today', 'Vercel Web Analytics'),
 'google_indexed_pages': ('Every indexed tool page is a free, compounding traffic entry point.', 'indexed page count (latest known)', 'Google Search Console'),
 'search_clicks': ('Free, durable traffic; the directory\'s long-term growth engine.', 'clicks from Google search for the day (GSC lags 2-3 days)', 'Google Search Console'),
 'affiliate_clicks': ('Leading indicator for affiliate revenue.', 'outbound clicks on affiliate links today', 'site click tracking / affiliate dashboards'),
 'affiliate_revenue': ('Directory monetization; scales with traffic, not just subscribers.', 'USD commission booked today', 'affiliate dashboards'),
 'sponsor_inquiries': ('Demand signal for the main newsletter revenue line.', 'new sponsor inquiries today', 'inbox / beehiiv ad network'),
 'sponsor_revenue': ('Primary newsletter money; priced per subscriber/open.', 'USD sponsor revenue booked today', 'invoices / beehiiv'),
 'x_followers': ('Owned distribution for posts that drive signups.', 'follower count at end of day', 'X'),
 'x_impressions': ('Reach of today\'s content; top of the X funnel.', 'sum of impressions on posts published today', 'X analytics'),
 'x_engagements': ('Feeds engagement rate: is the content resonating?', 'likes+replies+reposts+bookmarks+link clicks on today\'s posts', 'X analytics'),
 'x_mentions_replies': ('Brand conversation; people talking about/with you.', 'mentions + replies received today', 'X'),
 'open_rate': ('Inbox trust and subject line quality; sponsors ask for it.', 'open rate of the issue sent today (blank if none)', 'beehiiv'),
 'click_rate': ('Proof readers act; drives affiliate and sponsor value.', 'click rate of the issue sent today (blank if none)', 'beehiiv'),
 'tools_listed': ('Directory depth = more pages to index and more affiliate surface.', 'tools live on the site', 'data.csv / site'),
 'notes': ('Context for anomalies; keep it to one or two sentences.', 'short free text', '-'),
}
guide = Sheet('Guide', 7, [56, 120, 120, 300, 250, 150, 40], ST.get(wrap=True, v='Top', size=9))
gh = ST.get(bold=True, color=WHITE, bg=NAVY2, size=9, wrap=True)
guide.h(1, 30)
guide.set(1, 1, 'UseThisSI Scoreboard: metric guide', style=ST.get(bold=True, size=14, color=INK), across=5)
guide.h(2, 44)
guide.set(2, 1, 'Nightly routine: append ONE row to /workspace/usethissi/metrics.csv using the CSV keys below in this exact order '
                '(blank = not live yet, shown as n/a), then run scoreboard/build_sheet.py and upload scoreboard.xml to this file id. '
                'Daily Log is shown newest-first. Derived metrics (conversion, engagement rate, revenue per sub, MTD) are computed on the Dashboard, not logged.',
          style=ST.get(size=9, color=MUTED, wrap=True, v='Top'), across=5)
for j, t in enumerate(['#', 'Section', 'CSV key', 'Why it matters', 'How to log', 'Source'], start=1):
    guide.set(3, j, t, style=gh)
for i, (k, label, sec, kind, fmt, w) in enumerate(COLUMNS, start=4):
    why, how, src = WHY[k]
    fg, bg = SEC[sec]
    st = ST.get(wrap=True, v='Top', size=9, bg=bg, borders=[('Bottom', 1, LINE)])
    guide.h(i, 30)
    guide.set(i, 1, i - 3, style=st)
    guide.set(i, 2, sec.upper(), style=ST.get(wrap=True, v='Top', size=9, bg=bg, bold=True, color=fg, borders=[('Bottom', 1, LINE)]))
    guide.set(i, 3, k, style=ST.get(wrap=True, v='Top', size=9, bg=bg, font='Roboto Mono', borders=[('Bottom', 1, LINE)]))
    guide.set(i, 4, why, style=st)
    guide.set(i, 5, how, style=st)
    guide.set(i, 6, src, style=st)
r = 4 + len(COLUMNS) + 1
derived = [
    ('GROWTH', 'Visitor \u2192 sub conversion', 'Turns traffic into the north star; fix this before buying traffic.', 'net_new_subs / site_visitors (7-day)'),
    ('MONEY', 'Revenue this month (running)', 'The number that pays for the business; resets each month.', 'sum of affiliate + sponsor revenue, month to date'),
    ('MONEY', 'Revenue per subscriber', 'Monetization efficiency; what each new subscriber is worth.', 'MTD revenue / subscribers'),
    ('MONEY', 'First dollar', 'Milestone proof that someone pays.', 'lifetime revenue vs $1'),
    ('BRAND', 'X engagement rate', 'Content resonance, independent of reach.', 'x_engagements / x_impressions'),
]
guide.set(r, 1, 'Computed on the Dashboard (not logged)', style=ST.get(bold=True, size=10), across=5); r += 1
for sec, name, why, how in derived:
    fg, bg = SEC[sec.lower()]
    st = ST.get(wrap=True, v='Top', size=9, bg=bg, borders=[('Bottom', 1, LINE)])
    guide.h(r, 30)
    guide.set(r, 1, '', style=st)
    guide.set(r, 2, sec, style=ST.get(wrap=True, v='Top', size=9, bg=bg, bold=True, color=fg, borders=[('Bottom', 1, LINE)]))
    guide.set(r, 3, name, style=st); guide.set(r, 4, why, style=st); guide.set(r, 5, how, style=st); guide.set(r, 6, 'formula', style=st)
    r += 1
r += 1
guide.set(r, 1, 'Cut as vanity / not decision-driving: top_page (keep in notes when notable), x post count (impressions covers it), last_open/click naming (now open_rate/click_rate).',
          style=ST.get(size=8, italic=True, color=FAINT, wrap=True), across=5)
guide.h(r, 30)
GUIDE_ROWS = r + 1

# ================= write =================
sheets = [dash.xml(DASH_ROWS), log.xml(LOG_ROWS), guide.xml(GUIDE_ROWS), calc.xml(CALC_ROWS)]
xml = ('<?xml version="1.0"?>\n<?mso-application progid="Excel.Sheet"?>\n'
       '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:o="urn:schemas-microsoft-com:office:office" '
       'xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n'
       f'<Styles><Style ss:ID="Default" ss:Name="Normal"><Font ss:FontName="{FONT}" ss:Size="10"/></Style>' + ''.join(ST.xml) + '</Styles>\n'
       + '\n'.join(sheets) + '\n</Workbook>\n')
with open(OUT_XML, 'w', encoding='utf-8', newline='\n') as f:
    f.write(xml)
with open(OUT_ARGS, 'w') as f:
    json.dump({'fileId': FILE_ID, 'contentMimeType': 'application/vnd.ms-excel', 'textContent': f'$file:{OUT_XML}'}, f, indent=1)
print(f'ok: {len(rows)} log rows, latest {rows[0]["date"] if rows else "-"}, {len(xml):,} bytes -> {OUT_XML}')
