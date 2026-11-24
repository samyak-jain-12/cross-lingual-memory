"""Blog visuals: hero, method diagram, worked example, pipeline animation (GIF).

Drawn as HTML and rendered with headless Google Chrome, because Chrome shapes Devanagari correctly
(matplotlib does not). All example text and model outputs are real: item E031, results/main_r1.

Run from the project root with a Python that has pandas + Pillow:
    <venv>/bin/python report/blog/visuals/make_visuals.py
Writes report/blog/visuals/{hero,method,worked_example}.png and pipeline.gif
"""
import subprocess
import tempfile
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP = Path(tempfile.mkdtemp(prefix="clm_vis_"))

CSS = """
:root{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#8a8984;--line:#e4e3df;--card:#ffffff;
--blue:#2a78d6;--blue-t:#e8f1fc;--red:#e34948;--red-t:#fdecec;--green:#0f8a5f;--green-t:#e6f6ef;
--en:#6250d6;--hi:#b97d00;--hg:#c74f86}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg);color:var(--ink);
 font-family:-apple-system,"SF Pro Text","Helvetica Neue","Kohinoor Devanagari",sans-serif}
.dev{font-family:"Kohinoor Devanagari",-apple-system,sans-serif}
.tag{display:inline-block;font-weight:700;font-size:.72em;letter-spacing:.04em;color:#fff;border-radius:6px;
 padding:2px 8px;margin-right:8px;vertical-align:2px}
.en{background:var(--en)}.hi{background:var(--hi)}.hg{background:var(--hg)}
.card{background:var(--card);border:2px solid var(--line);border-radius:16px}
.h{font-weight:700}.mut{color:var(--muted)}.ink2{color:var(--ink2)}
.ok{color:var(--green)}.bad{color:var(--red)}
.stamp{display:inline-block;font-weight:800;letter-spacing:.06em;border:3px solid;border-radius:8px;padding:2px 12px}
"""


def render(name, body, w, h, scale=2, extra_css=""):
    html = TMP / f"{name}.html"
    html.write_text(f"<!doctype html><meta charset=utf-8><style>{CSS}{extra_css}</style>"
                    f"<body style='width:{w}px;height:{h}px;overflow:hidden'>{body}</body>", encoding="utf-8")
    png = TMP / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--user-data-dir={TMP / 'prof'}", f"--force-device-scale-factor={scale}",
                    f"--window-size={w},{h}", f"--screenshot={png}", html.as_uri()],
                   check=True, capture_output=True)
    return png


# --------------------------------------------------------------------- real example (item E031)
MEM_EN = "I saw a beautiful 3-bedroom bungalow in the Oakwood neighbourhood on January 22nd…"
MEM_HI = "मैंने 22 जनवरी को ओकवुड इलाक़े में एक ख़ूबसूरत 3-बेडरूम बंगला देखा…"
MEM_HG = "Maine 22 January ko Oakwood area mein ek khoobsurat 3-bedroom bungalow dekha…"
DISTR = "My parents viewed a house in the next street on February 5th."
Q_HG = "Maine Oakwood mein 3-bedroom bungalow kab dekha tha?"
Q_GLOSS = "When did I see the 3-bedroom bungalow in Oakwood?"
A_FC = "Maine yah nahin jaanta ki aapne <u>Maine mein</u> kis waqt 3-bedroom bungalow dekha tha."
A_FC_GLOSS = "I don't know when you saw a 3-bedroom bungalow <u>in Maine</u>."
A_RM = "Maine Oakwood neighbourhood mein <u>22 January</u> ko aapne ek sundar 3-bedroom bungalow dekha tha."
A_RM_GLOSS = "…you saw a beautiful 3-bedroom bungalow in Oakwood on <u>22 January</u>."
TOP5 = [("Session 4", "I saw a beautiful 3-bedroom bungalow in the Oakwood neighbourhood on January 22nd…", True),
        ("Session 2", "I like the organic cotton onesie and baby blanket set idea…", False),
        ("Session 7", "I'm looking for some advice on bedroom lighting…", False),
        ("Session 7", "I'm currently using a bedside lamp with a new bulb…", False),
        ("Session 4", "Should I get an inspection before making an offer?", False)]

# ===================================================================== 1. hero (1200 x 630)
hero = f"""
<div style="display:flex;height:630px;padding:48px 56px;gap:48px;align-items:center">
 <div style="flex:1.15;display:flex;flex-direction:column;gap:18px;font-size:23px">
  <div class="mut" style="font-size:17px">Session 4</div>
  <div style="align-self:flex-end;max-width:560px;background:var(--blue);color:#fff;border-radius:22px 22px 6px 22px;
       padding:16px 22px;line-height:1.35"><span class="tag en" style="background:#fff;color:var(--en)">EN</span>
   I saw a beautiful 3-bedroom bungalow in Oakwood on <b>January 22nd</b>.</div>
  <div class="mut" style="text-align:center;font-size:17px;letter-spacing:.06em">· · ·  16 sessions later  · · ·</div>
  <div style="align-self:flex-end;max-width:560px;background:var(--blue);color:#fff;border-radius:22px 22px 6px 22px;
       padding:16px 22px;line-height:1.35"><span class="tag hg" style="background:#fff;color:var(--hg)">HG</span>
   <b>Maine</b> Oakwood mein bungalow kab dekha tha?</div>
  <div style="align-self:flex-start;max-width:600px;background:#efeeea;border-radius:22px 22px 22px 6px;padding:16px 22px;
       line-height:1.35">I don't know when you saw a bungalow <b class="bad">in Maine</b>.
   <div class="mut" style="font-size:16px;margin-top:6px">(Llama-3.1-8B, translated from Hinglish)</div></div>
 </div>
 <div style="flex:.85;display:flex;flex-direction:column;gap:22px">
  <div style="font-size:15px;font-weight:700;letter-spacing:.14em;color:var(--muted)">CROSS-LINGUAL MEMORY</div>
  <div style="font-size:46px;font-weight:800;line-height:1.08">“maine” means <span style="color:var(--blue)">“I”</span>,<br>
   not the US state</div>
  <div class="ink2" style="font-size:22px;line-height:1.4">Do LLM agents remember what you told them when you switch
   between <span class="h" style="color:var(--en)">English</span>, <span class="h dev" style="color:var(--hi)">हिंदी</span>
   and <span class="h" style="color:var(--hg)">Hinglish</span>?</div>
 </div>
</div>"""
p = render("hero", hero, 1200, 630)
Image.open(p).save(OUT / "hero.png")

# ===================================================================== 2. method diagram (1000 x 860)
def box(n, title, inner):
    return (f"<div class='card' style='padding:22px 24px'><div class='h' style='font-size:25px;margin-bottom:14px'>"
            f"<span style='display:inline-block;width:36px;height:36px;border-radius:50%;background:var(--ink);color:#fff;"
            f"text-align:center;line-height:36px;font-size:20px;margin-right:10px'>{n}</span>{title}</div>{inner}</div>")


grid = "".join(
    f"<div style='height:34px;border-radius:6px;background:{'var(--blue)' if i == 3 else 'var(--line)'};"
    f"{'outline:3px dashed var(--red);outline-offset:-3px;background:var(--red-t)' if i == 7 else ''}'></div>"
    for i in range(20))
m1 = f"""<div style="font-size:19px;line-height:1.45;display:flex;flex-direction:column;gap:8px">
 <div><span class="tag en">EN</span>{MEM_EN}</div>
 <div class="dev"><span class="tag hi">HI</span>{MEM_HI}</div>
 <div><span class="tag hg">HG</span>{MEM_HG}</div></div>"""
m2 = f"""<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin-bottom:12px">{grid}</div>
 <div style="font-size:18px;line-height:1.4" class="ink2"><b style="color:var(--blue)">■</b> the fact &nbsp;
 <b class="bad">▢</b> a distractor (“…viewed a house on <b>Feb 5</b>”)<br>19 other sessions are unrelated chat</div>"""
row = "display:flex;gap:12px;align-items:baseline;font-size:19px;line-height:1.35;padding:7px 0"
m3 = f"""<div style="display:flex;flex-direction:column">
 <div style="{row}"><b style="min-width:118px">Full context</b><span class="ink2">all 20 sessions in the prompt</span></div>
 <div style="{row};border-top:1px solid var(--line)"><b style="min-width:118px">Retrieval</b><span class="ink2">a search
  model picks the top 5 of 40 user turns, stored as <b>S1</b> original, <b>S2</b> English, <b>S3</b> both</span></div>
 <div style="{row};border-top:1px solid var(--line)"><b style="min-width:118px">Oracle</b><span class="ink2">only the right
  turn (best case)</span></div></div>"""
m4 = f"""<div style="font-size:19px;line-height:1.5">
 <div>Question in <span class="tag en">EN</span><span class="tag hi">HI</span><span class="tag hg">HG</span></div>
 <div class="ink2">→ <b style="color:var(--ink)">Llama-3.1-8B</b> or <b style="color:var(--ink)">Qwen3-8B</b> answers</div>
 <div class="ink2">→ <b style="color:var(--ink)">Qwen3-14B</b> judges it</div>
 <div style="margin-top:8px"><span class="stamp ok" style="font-size:16px">CORRECT</span>&nbsp;
  <span class="stamp bad" style="font-size:16px">INCORRECT</span></div></div>"""
method = f"""
<div style="padding:32px 34px">
 <div class="h" style="font-size:31px;margin-bottom:6px">How the benchmark works</div>
 <div class="ink2" style="font-size:20px;margin-bottom:22px">Every fact is stored in 3 languages and asked in 3 languages:
  9 language pairs for the same question.</div>
 <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">
  {box(1, "One fact, three languages", m1)}{box(2, "Hidden in 20 chat sessions", m2)}
  {box(3, "Three ways to give memory", m3)}{box(4, "Ask, answer, judge", m4)}
 </div>
 <div style="margin-top:20px;text-align:center;font-size:20px;background:var(--blue-t);border-radius:12px;padding:14px">
  165 items × 9 language pairs × 7 memory setups × 2 wordings × 2 models = <b>41,580 answers</b></div>
</div>"""
p = render("method", method, 1000, 860)
Image.open(p).save(OUT / "method.png")

# ===================================================================== 3. worked example (1000 x 820)
def answer(ok, who, how, text, gloss, note):
    c, t, mark = ("green", "green-t", "✓") if ok else ("red", "red-t", "✗")
    return f"""<div style="flex:1;border:3px solid var(--{c});background:var(--{t});border-radius:16px;padding:20px 22px">
 <div style="font-size:19px;margin-bottom:10px"><b class="{'ok' if ok else 'bad'}" style="font-size:26px">{mark}</b>
  <b>{who}</b> · {how}</div>
 <div style="font-size:21px;line-height:1.4;margin-bottom:8px">“{text}”</div>
 <div class="ink2" style="font-size:18px;line-height:1.4;margin-bottom:10px">({gloss})</div>
 <div style="font-size:17px" class="{'ok' if ok else 'bad'}"><b>{note}</b></div></div>"""


worked = f"""
<div style="padding:32px 34px">
 <div class="h" style="font-size:31px;margin-bottom:6px">Same memory, same question, two ways of reading</div>
 <div class="ink2" style="font-size:20px;margin-bottom:22px">Real input and outputs from our benchmark (item E031)</div>
 <div class="card" style="padding:18px 22px;margin-bottom:14px;font-size:21px;line-height:1.4">
  <div class="mut" style="font-size:16px;font-weight:700;letter-spacing:.08em;margin-bottom:6px">MEMORY · SESSION 4 OF 20</div>
  <span class="tag en">EN</span>{MEM_EN}</div>
 <div class="card" style="padding:18px 22px;margin-bottom:22px;font-size:21px;line-height:1.4">
  <div class="mut" style="font-size:16px;font-weight:700;letter-spacing:.08em;margin-bottom:6px">QUESTION · ASKED LATER</div>
  <span class="tag hg">HG</span><b>{Q_HG}</b><div class="ink2" style="font-size:18px;margin-top:4px">({Q_GLOSS})</div></div>
 <div style="display:flex;gap:18px">
  {answer(False, "Llama-3.1-8B", "full context", A_FC, A_FC_GLOSS,
          "Reads “maine” (I) as the US state and gives up")}
  {answer(True, "Llama-3.1-8B", "retrieval", A_RM, A_RM_GLOSS,
          "The fact was retrieved first of 40 turns")}
 </div>
</div>"""
p = render("worked", worked, 1000, 720)
Image.open(p).save(OUT / "worked_example.png")

# ===================================================================== 4. pipeline animation (GIF)
# Drawn at 720 CSS px wide, about Substack's column width, so text shows near its true size
# (smallest text 16px). Rendered at 1.5x for sharpness. Few words per frame, long holds.
d = pd.read_csv(ROOT / "results" / "main_r1" / "scored.csv")
A = d[d.answerable & (d.model == "llama3.1-8b")]
acc = {s: A[A.setup == s].groupby(["store", "query"]).correct.mean() for s in ("FC", "RM-S1")}
STAGES = ["Store", "Ask", "Read all", "Retrieve", "Answer", "Count"]
GW, GH = 720, 450


def short(t, n):
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def stagebar(k):
    out = []
    for i, s in enumerate(STAGES):
        on, done = i == k, i < k
        out.append(f"<div style='flex:1;text-align:center;padding:7px 0;border-radius:9px;font-size:16px;font-weight:700;"
                   f"background:{'var(--ink)' if on else ('#d9d8d3' if done else 'transparent')};"
                   f"color:{'#fff' if on else ('var(--ink2)' if done else 'var(--muted)')};"
                   f"border:2px solid {'var(--ink)' if on else 'var(--line)'}'>{s}</div>")
    return "<div style='display:flex;gap:6px;margin-bottom:26px'>" + "".join(out) + "</div>"


def heat(setup, hl=None):
    cells = []
    for st in ("en", "hi", "hg"):
        for q in ("en", "hi", "hg"):
            v = acc[setup][(st, q)]
            a = (v - .6) / .4
            bg = f"rgba(42,120,214,{max(.12, min(1, a)):.2f})"
            border = "outline:4px solid var(--ink);outline-offset:-4px;" if (st, q) == hl else ""
            cells.append(f"<div style='height:54px;display:flex;align-items:center;justify-content:center;font-size:22px;"
                         f"font-weight:{700 if (st, q) == hl else 400};color:{'#fff' if a > .55 else 'var(--ink)'};"
                         f"background:{bg};{border}'>{100 * v:.0f}</div>")
    lab = "".join(f"<div class='mut' style='font-size:16px;text-align:center'>{x}</div>" for x in ("EN", "HI", "HG"))
    rows = ""
    for i, st in enumerate(("EN", "HI", "HG")):
        rows += f"<div class='mut' style='font-size:16px;align-self:center'>{st}</div>" + "".join(cells[3 * i:3 * i + 3])
    return (f"<div style='display:grid;grid-template-columns:36px repeat(3,74px);gap:3px'>"
            f"<div></div>{lab}{rows}</div>")


def head(t, sub=""):
    return (f"<div class='h' style='font-size:27px;line-height:1.2;margin-bottom:{8 if sub else 22}px'>{t}</div>"
            + (f"<div class='ink2' style='font-size:19px;margin-bottom:22px'>{sub}</div>" if sub else ""))


def bubble(text, gloss, me=False):
    side = "22px 22px 6px 22px" if me else "22px 22px 22px 6px"
    col = "background:var(--blue);color:#fff" if me else "background:#efeeea"
    g = f"<div style='font-size:18px;margin-top:8px;opacity:.8'>({gloss})</div>" if gloss else ""
    return f"<div style='{col};border-radius:{side};padding:16px 22px;font-size:23px;line-height:1.35'>“{text}”{g}</div>"


def stamp(ok):
    return (f"<div style='margin-top:24px;font-size:20px'>Judge: <span class='stamp {'ok' if ok else 'bad'}' "
            f"style='font-size:20px'>{'CORRECT' if ok else 'INCORRECT'}</span></div>")


def frame(k):
    body = stagebar(k)
    if k == 0:
        g = "".join(
            f"<div style='height:38px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:16px;"
            f"background:{'var(--blue)' if i == 3 else ('var(--red-t)' if i == 7 else 'var(--line)')};"
            f"color:{'#fff' if i == 3 else ('var(--red)' if i == 7 else 'var(--muted)')};font-weight:700;"
            f"{'outline:3px dashed var(--red);outline-offset:-3px' if i == 7 else ''}'>{i + 1}</div>" for i in range(20))
        body += head("A fact is hidden in 20 chat sessions")
        body += f"""<div style="display:grid;grid-template-columns:repeat(10,1fr);gap:6px;margin-bottom:24px">{g}</div>
          <div style="font-size:21px;line-height:1.4"><b style="color:var(--blue)">Session 4:</b>
           “I saw a beautiful 3-bedroom bungalow in the Oakwood neighbourhood on <b>January 22nd</b>.”</div>
          <div style="font-size:21px;line-height:1.4;margin-top:10px"><b class="bad">Session 8 (decoy):</b>
           “My parents viewed a house in the next street on February 5th.”</div>"""
    elif k == 1:
        body += head("Later, the user asks in Hinglish")
        body += bubble("<b>Maine</b> Oakwood mein 3-bedroom bungalow kab dekha tha?",
                       "When did I see the bungalow in Oakwood?", me=True)
        body += "<div style='font-size:21px;margin-top:22px'><b>maine</b> = “I” in Hindi</div>"
    elif k == 2:
        body += head("Full context: Llama reads all 20 sessions", "The fact is lost in the long history")
        body += bubble(A_FC, A_FC_GLOSS)
        body += stamp(False)
    elif k == 3:
        rows = "".join(
            f"<div style='display:flex;gap:12px;align-items:center;padding:9px 14px;border-radius:10px;font-size:19px;"
            f"background:{'var(--blue-t)' if gd else 'transparent'};border:2px solid {'var(--blue)' if gd else 'var(--line)'}'>"
            f"<b style='min-width:30px'>#{i + 1}</b><span>{short(t, 46)}</span></div>"
            for i, (_, t, gd) in enumerate(TOP5[:3]))
        body += head("Retrieval: search all 40 user turns", "The Hinglish question finds the English memory first")
        body += f"""<div style="display:flex;flex-direction:column;gap:7px">{rows}</div>
          <div class="ink2" style="font-size:18px;margin-top:12px">Only the top 5 turns go to the model</div>"""
    elif k == 4:
        body += head("Llama reads only those 5 turns")
        body += bubble(A_RM, A_RM_GLOSS)
        body += stamp(True)
    else:
        body += head("Repeat for every item, language pair and setup")
        body += f"""<div style="display:flex;gap:44px">
          <div><div class="h" style="font-size:19px;margin-bottom:8px">Full context</div>{heat("FC", ("en", "hg"))}</div>
          <div><div class="h" style="font-size:19px;margin-bottom:8px">Retrieval</div>{heat("RM-S1", ("en", "hg"))}</div></div>
          <div style="font-size:19px;line-height:1.4;margin-top:16px">Llama accuracy (%). Rows: memory language.
           Columns: question language. Outlined: English memory, Hinglish question.</div>"""
    return f"<div style='padding:24px 30px'>{body}</div>"


frames, hold = [], [4500, 4000, 5500, 5500, 4500, 7500]
for k in range(len(STAGES)):
    p = render(f"f{k}", frame(k), GW, GH, scale=1.5)
    frames.append(Image.open(p).convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT))
frames[0].save(OUT / "pipeline.gif", save_all=True, append_images=frames[1:], duration=hold, loop=0, optimize=True)
for k in range(len(STAGES)):
    Image.open(render(f"f{k}x", frame(k), GW, GH, scale=1)).save(TMP / f"check{k}.png")
Image.open(render("f5x", frame(5), GW, GH, scale=2)).save(OUT / "pipeline_last_frame.png")
print("check frames in", TMP)
print("wrote", *sorted(x.name for x in OUT.glob("*.png")), "pipeline.gif")
