"""Phase 3, step 4: build the 2-annotator verification workbook (design_spec.md §3.4).

Reads  data/items/items_<batch>.jsonl
Writes data/items/verify_<batch>.xlsx   (one row per item x language x field)

Run from the project root:  python3 src/make_verification_sheet.py batch01_pilot
"""
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("memory_turn", "assistant_reply", "followup_turn", "followup_reply", "q1", "q2", "distractor_sentence")
LANG_NAME = {"hi": "Hindi (Devanagari)", "hg": "Hinglish (Roman)"}

FONT = "Arial"
HEAD_FILL = PatternFill("solid", start_color="1F3864")
INPUT_FILL = PatternFill("solid", start_color="FFF2CC")   # yellow = annotator fills these
KEY_FILL = PatternFill("solid", start_color="E2EFDA")     # green = memory turn (most important row)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")


def gold_text(it):
    if not it.get("is_answerable", True):
        return "UNANSWERABLE: question must stay about something never mentioned"
    slots = it["gold"]["slots"]
    return it["gold"]["answer_en"] + "  |  accepted: " + "; ".join(a for s in slots for a in s["aliases"][:6])


def build(batch):
    items = [json.loads(l) for l in (ROOT / f"data/items/items_{batch}.jsonl").open(encoding="utf-8")]
    wb = Workbook()

    # ---------------- README ----------------
    rd = wb.active
    rd.title = "README"
    lines = [
        ("Verification workbook", True),
        (f"Batch: {batch}  |  Items: {len(items)}  |  Protocol: phase2/design_spec.md section 3.4", False),
        ("", False),
        ("HOW TO USE", True),
        ("1. Two of the three team members check every row independently. Annotator 1 uses columns I-J, Annotator 2 uses K-L. Do not look at the other person's columns until both are done.", False),
        ("2. For each row compare 'Draft text' with 'English source'. Choose a decision from the dropdown:", False),
        ("     ACCEPT = same meaning, natural, follows conventions, no change needed", False),
        ("     EDIT   = meaning OK after a fix: write the full corrected text in the 'corrected text' column", False),
        ("     REJECT = cannot be fixed (meaning differs, unnatural, or the gold value is broken)", False),
        ("3. Checklist for every row: (a) same meaning as English, (b) gold value unchanged (column G), (c) natural register,", False),
        ("   (d) conventions: Hindi = Devanagari, brand/product names stay Latin, person/place names in Devanagari, Arabic digits;", False),
        ("   Hinglish = Roman script, spelling sheet in design_spec 2.2, (e) user's verbs match the gender in column C, (f) q1 and q2 ask the same thing.", False),
        ("4. Green rows are the memory turns: the gold value MUST appear there. Check these most carefully.", False),
        ("5. Disagreements are discussed and the agreed text goes in column M ('Final text'). Unresolved items are dropped.", False),
        ("6. The 'Summary' sheet computes acceptance rates and Cohen's kappa automatically. Report these numbers in the paper.", False),
        ("", False),
        ("EXAMPLE OF A FILLED ROW (format only)", True),
    ]
    for r, (text, bold) in enumerate(lines, 1):
        c = rd.cell(row=r, column=1, value=text)
        c.font = Font(name=FONT, bold=bold, size=12 if bold else 10)
    ex_head = ["item_id", "lang", "field", "Draft text", "Annotator 1 decision", "Annotator 1 corrected text", "notes"]
    ex_row = ["F002", "hg", "memory_turn", "Maine Business Administration mein degree li hai, ...", "EDIT",
              "Maine Business Administration mein degree li hai, aur isse meri nayi job mein kaafi help mili hai. ...",
              "'bahut' repeated twice in the turn; changed one to 'kaafi'"]
    r0 = len(lines) + 1
    for j, (h, v) in enumerate(zip(ex_head, ex_row), 1):
        rd.cell(row=r0, column=j, value=h).font = Font(name=FONT, bold=True, size=10)
        c = rd.cell(row=r0 + 1, column=j, value=v)
        c.font = Font(name=FONT, size=10, italic=True)
        c.alignment = WRAP
    rd.column_dimensions["A"].width = 120
    for col in "BCDEFG":
        rd.column_dimensions[col].width = 28

    # ---------------- Verify ----------------
    ws = wb.create_sheet("Verify")
    headers = ["item_id", "type", "user gender", "lang", "field", "English source", "Gold value (must stay intact)",
               "Draft text", "Annotator 1 decision", "Annotator 1 corrected text",
               "Annotator 2 decision", "Annotator 2 corrected text", "Final text (after discussion)", "Notes"]
    for j, h in enumerate(headers, 1):
        c = ws.cell(row=1, column=j, value=h)
        c.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
        c.fill = HEAD_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BORDER
    ws.cell(row=1, column=7).comment = Comment("The answer the model must recover. It has to survive translation unchanged.", "build script")

    row = 2
    for it in items:
        for lang in ("hi", "hg"):
            t, en = it["text"][lang], it["text"]["en"]
            for fld in FIELDS:
                if fld not in t:
                    continue
                vals = [it["item_id"], it["memory_type"], it.get("user_gender", "-"), LANG_NAME[lang], fld,
                        en.get(fld, ""), gold_text(it), t[fld], None, None, None, None, None, None]
                for j, v in enumerate(vals, 1):
                    c = ws.cell(row=row, column=j, value=v)
                    c.font = Font(name=FONT, size=10)
                    c.alignment = WRAP
                    c.border = BORDER
                    if j in (9, 10, 11, 12, 13):
                        c.fill = INPUT_FILL
                    elif fld == "memory_turn":
                        c.fill = KEY_FILL
                row += 1
    last = row - 1

    dv = DataValidation(type="list", formula1='"ACCEPT,EDIT,REJECT"', allow_blank=True,
                        showErrorMessage=True, errorTitle="Invalid", error="Choose ACCEPT, EDIT or REJECT")
    ws.add_data_validation(dv)
    dv.add(f"I2:I{last}")
    dv.add(f"K2:K{last}")
    # Highlight EDIT rows whose corrected text is still empty.
    red = PatternFill("solid", start_color="F8CBAD")
    ws.conditional_formatting.add(f"J2:J{last}", FormulaRule(formula=['AND($I2="EDIT",$J2="")'], fill=red))
    ws.conditional_formatting.add(f"L2:L{last}", FormulaRule(formula=['AND($K2="EDIT",$L2="")'], fill=red))

    widths = [8, 10, 8, 14, 14, 45, 30, 45, 12, 40, 12, 40, 40, 25]
    for j, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=j).column_letter].width = w
    ws.freeze_panes = "F2"
    ws.auto_filter.ref = f"A1:N{last}"

    # ---------------- Summary (formulas) ----------------
    sm = wb.create_sheet("Summary")
    rng1, rng2 = f"Verify!$I$2:$I${last}", f"Verify!$K$2:$K${last}"
    sm["A1"] = "Verification summary (updates automatically)"
    sm["A1"].font = Font(name=FONT, bold=True, size=12)
    sm["A3"], sm["B3"], sm["C3"] = "Decision", "Annotator 1", "Annotator 2"
    for j, d in enumerate(["ACCEPT", "EDIT", "REJECT"], 4):
        sm[f"A{j}"] = d
        sm[f"B{j}"] = f'=COUNTIF({rng1},"{d}")'
        sm[f"C{j}"] = f'=COUNTIF({rng2},"{d}")'
    sm["A7"], sm["B7"], sm["C7"] = "Rows decided", "=SUM(B4:B6)", "=SUM(C4:C6)"
    sm["A8"], sm["B8"] = "Total rows", f"=COUNTA(Verify!$A$2:$A${last})"
    sm["A9"], sm["B9"], sm["C9"] = "% accepted unedited", "=IF(B7=0,0,B4/B7)", "=IF(C7=0,0,C4/C7)"

    sm["A11"] = "Agreement on ACCEPT vs not (rows decided by both)"
    sm["A11"].font = Font(name=FONT, bold=True)
    both = f'SUMPRODUCT(({rng1}<>"")*({rng2}<>""))'
    sm["A12"], sm["B12"] = "Rows decided by both", f"={both}"
    sm["A13"], sm["B13"] = "Both ACCEPT", f'=COUNTIFS({rng1},"ACCEPT",{rng2},"ACCEPT")'
    sm["A14"], sm["B14"] = "Both not ACCEPT", f'=SUMPRODUCT(({rng1}<>"")*({rng1}<>"ACCEPT")*({rng2}<>"")*({rng2}<>"ACCEPT"))'
    sm["A15"], sm["B15"] = "A1 ACCEPT (among both-decided)", f'=SUMPRODUCT(({rng1}="ACCEPT")*({rng2}<>""))'
    sm["A16"], sm["B16"] = "A2 ACCEPT (among both-decided)", f'=SUMPRODUCT(({rng2}="ACCEPT")*({rng1}<>""))'
    sm["A17"], sm["B17"] = "Observed agreement (po)", "=IF(B12=0,0,(B13+B14)/B12)"
    sm["A18"], sm["B18"] = "Chance agreement (pe)", "=IF(B12=0,0,(B15/B12)*(B16/B12)+(1-B15/B12)*(1-B16/B12))"
    sm["A19"], sm["B19"] = "Cohen's kappa", "=IF(OR(B12=0,B18=1),0,(B17-B18)/(1-B18))"
    sm["A21"] = "Target from design spec: report kappa; drop or re-brief if REJECT rate > 15%."
    sm["A22"], sm["B22"] = "REJECT rate (either annotator)", f'=IF(B8=0,0,SUMPRODUCT((({rng1}="REJECT")+({rng2}="REJECT")>0)*1)/B8)'
    for r in range(1, 23):
        for col in "ABC":
            sm[f"{col}{r}"].font = Font(name=FONT, size=10, bold=(r in (1, 3, 11, 19)))
    for cell in ("B9", "C9", "B17", "B18", "B22"):
        sm[cell].number_format = "0.0%"
    sm["B19"].number_format = "0.00"
    sm.column_dimensions["A"].width = 48
    sm.column_dimensions["B"].width = 14
    sm.column_dimensions["C"].width = 14

    out = ROOT / f"data/items/verify_{batch}.xlsx"
    wb.save(out)
    print(f"wrote {out.relative_to(ROOT)}: {last - 1} rows to verify")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "batch01_pilot")
