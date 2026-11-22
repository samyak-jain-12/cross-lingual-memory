"""Build the blind human-validation workbook for the LLM judge [design_spec 6.2].

Reads  results/<run>/judge_validation_sample.csv
Writes results/<run>/judge_validation_<run>.xlsx
  README  - instructions and one example row
  Label   - 200 responses; two annotators label independently; judge verdict NOT shown (blind)
  Key     - judge verdicts (do not open until labelling is done)
  Summary - human-human kappa and judge-vs-human kappa, computed by formulas

Run from the project root:  python3 src/make_judge_validation_sheet.py batch01_pilot_r2
"""
import csv
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
FONT = "Arial"
HEAD = PatternFill("solid", start_color="1F3864")
INPUT = PatternFill("solid", start_color="FFF2CC")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
LANG = {"en": "English", "hi": "Hindi", "hg": "Hinglish"}
LABELS = ("CORRECT", "INCORRECT", "NO_ANSWER")


def build(run):
    rows = list(csv.DictReader((ROOT / f"results/{run}/judge_validation_sample.csv").open(encoding="utf-8")))
    n = len(rows)
    last = n + 1
    wb = Workbook()

    rd = wb.active
    rd.title = "README"
    text = [
        ("Judge validation - blind human labelling", True),
        (f"Run: {run}  |  {n} model answers  |  Protocol: phase2/design_spec.md section 6.2", False),
        ("", False),
        ("WHAT YOU DO", True),
        ("Two people label every row in the 'Label' sheet independently (Annotator 1: column I, Annotator 2: column J).", False),
        ("Do not look at each other's column, and do not open the 'Key' sheet until both are finished.", False),
        ("", False),
        ("For each row, read the Question, the Gold answer and the Model answer, then pick ONE label:", True),
        ("  CORRECT    = the answer states the gold information (any language or script) and does not contradict it.", False),
        ("               Extra harmless words are fine. Hedging ('I think it is 45 minutes') is fine.", False),
        ("  INCORRECT  = wrong, incomplete, contradicts the gold, or lists several candidates (e.g. 'Luna and Coco').", False),
        ("  NO_ANSWER  = the model says it does not know / has no information.", False),
        ("", False),
        ("SPECIAL CASE - unanswerable questions (Gold says 'NO_ANSWER ...'):", True),
        ("  The user never said this. If the model says it doesn't know -> NO_ANSWER. If it gives any specific answer -> INCORRECT.", False),
        ("", False),
        ("Rules of thumb", True),
        ("  - Judge MEANING, not language: a Hindi or Hinglish answer to an English question can be CORRECT.", False),
        ("  - Different spelling or grammatical form is fine: 'पीला ड्रेस' = 'पीली ड्रेस' = 'yellow dress'.", False),
        ("  - Adding a wrong extra fact that contradicts the gold makes it INCORRECT (e.g. '45 minutes, so 90 minutes to get to work').", False),
        ("  - Unsure? Pick your best label and write why in Notes. Expect ~45-60 minutes for 200 rows.", False),
        ("", False),
        ("AFTER BOTH ARE DONE", True),
        ("  Rows where you disagree turn red in column K. Discuss them and fill 'Adjudicated label' (column L) for those rows only.", False),
        ("  The 'Summary' sheet then shows the agreement numbers for the report automatically.", False),
        ("", False),
        ("EXAMPLE (format only)", True),
    ]
    for r, (t, b) in enumerate(text, 1):
        c = rd.cell(row=r, column=1, value=t)
        c.font = Font(name=FONT, bold=b, size=12 if b else 10)
    ex_h = ["Question", "Gold answer", "Model answer", "Annotator 1 label", "Notes"]
    ex_v = ["How long does my commute to work take, one way?", "45 minutes (each way)",
            "Your commute takes 45 minutes each way.", "CORRECT", ""]
    r0 = len(text) + 1
    for j, (h, v) in enumerate(zip(ex_h, ex_v), 1):
        rd.cell(row=r0, column=j, value=h).font = Font(name=FONT, bold=True, size=10)
        c = rd.cell(row=r0 + 1, column=j, value=v)
        c.font = Font(name=FONT, size=10, italic=True)
        c.alignment = WRAP
    rd.column_dimensions["A"].width = 115
    for col in "BCDE":
        rd.column_dimensions[col].width = 30

    ws = wb.create_sheet("Label")
    heads = ["#", "Model", "Item", "Memory stored in", "Question asked in", "Setup", "Question", "Gold answer",
             "Model answer", "Annotator 1 label", "Annotator 2 label", "Agree?",
             "Adjudicated label (only if disagree)", "Final human label", "Notes"]
    for j, h in enumerate(heads, 1):
        c = ws.cell(row=1, column=j, value=h)
        c.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
        c.fill = HEAD
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BORDER
    for i, r in enumerate(rows, 2):
        vals = [i - 1, r["model"], r["item_id"], LANG[r["store"]], LANG[r["query"]], r["setup"], r["question"],
                r["gold"], r["response"], None, None,
                f'=IF(OR(J{i}="",K{i}=""),"",IF(J{i}=K{i},"yes","NO"))', None,
                f'=IF(AND(J{i}<>"",J{i}=K{i}),J{i},IF(M{i}<>"",M{i},""))', None]
        for j, v in enumerate(vals, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.font = Font(name=FONT, size=10)
            c.alignment = WRAP
            c.border = BORDER
            if j in (10, 11, 13, 15):
                c.fill = INPUT
    dv = DataValidation(type="list", formula1='"CORRECT,INCORRECT,NO_ANSWER"', allow_blank=True,
                        showErrorMessage=True, error="Choose CORRECT, INCORRECT or NO_ANSWER")
    ws.add_data_validation(dv)
    for col in "JKM":
        dv.add(f"{col}2:{col}{last}")
    red = PatternFill("solid", start_color="F8CBAD")
    ws.conditional_formatting.add(f"L2:L{last}", FormulaRule(formula=[f'$L2="NO"'], fill=red))
    for j, w in enumerate([5, 11, 8, 11, 11, 8, 38, 26, 48, 14, 14, 8, 16, 14, 24], 1):
        ws.column_dimensions[ws.cell(row=1, column=j).column_letter].width = w
    ws.freeze_panes = "J2"

    key = wb.create_sheet("Key")
    key["A1"], key["B1"], key["C1"] = "#", "Judge raw label", "Judge label (human scale)"
    for i, r in enumerate(rows, 2):
        key[f"A{i}"] = i - 1
        key[f"B{i}"] = r["judge"]
        # Unanswerable controls: the judge says ANSWERED for a hallucination = INCORRECT on the human scale.
        key[f"C{i}"] = {"ANSWERED": "INCORRECT"}.get(r["judge"], r["judge"])
    for c in ("A1", "B1", "C1"):
        key[c].font = Font(name=FONT, bold=True)
    key.sheet_state = "hidden"

    sm = wb.create_sheet("Summary")
    A, B = f"Label!$J$2:$J${last}", f"Label!$K$2:$K${last}"
    F, J = f"Label!$N$2:$N${last}", f"Key!$C$2:$C${last}"

    def kappa_block(top, title, X, Y):
        sm.cell(row=top, column=1, value=title).font = Font(name=FONT, bold=True, size=11)
        sm.cell(row=top + 1, column=1, value="Rows labelled by both")
        sm.cell(row=top + 1, column=2, value=f'=SUMPRODUCT(({X}<>"")*({Y}<>""))')
        sm.cell(row=top + 2, column=1, value="Observed agreement (po)")
        sm.cell(row=top + 2, column=2, value=f'=IF(B{top+1}=0,0,SUMPRODUCT(({X}={Y})*({X}<>""))/B{top+1})')
        terms = "+".join(f'(SUMPRODUCT(({X}="{l}")*({Y}<>""))/B{top+1})*(SUMPRODUCT(({Y}="{l}")*({X}<>""))/B{top+1})'
                         for l in LABELS)
        sm.cell(row=top + 3, column=1, value="Chance agreement (pe)")
        sm.cell(row=top + 3, column=2, value=f"=IF(B{top+1}=0,0,{terms})")
        sm.cell(row=top + 4, column=1, value="Cohen's kappa")
        sm.cell(row=top + 4, column=2, value=f"=IF(OR(B{top+1}=0,B{top+3}=1),0,(B{top+2}-B{top+3})/(1-B{top+3}))")
        sm.cell(row=top + 2, column=2).number_format = "0.0%"
        sm.cell(row=top + 3, column=2).number_format = "0.0%"
        sm.cell(row=top + 4, column=2).number_format = "0.00"
        sm.cell(row=top + 4, column=1).font = Font(name=FONT, bold=True)

    sm["A1"] = "Judge validation summary (updates automatically)"
    sm["A1"].font = Font(name=FONT, bold=True, size=12)
    kappa_block(3, "1. Human vs human (Annotator 1 vs Annotator 2)", A, B)
    kappa_block(9, "2. LLM judge vs final human label  <- the number the report needs", J, F)
    sm["A15"] = "Decision rule (design_spec 6.2): kappa >= 0.80 -> keep the judge; below -> revise judge prompt once; still below -> slot-match + human adjudication becomes primary."
    sm["A16"] = "Note: most answers are CORRECT, so kappa can look low even when raw agreement is high (the 'kappa paradox'). Report both po and kappa."
    sm["A18"], sm["B18"], sm["C18"], sm["D18"] = "Label counts", "Annotator 1", "Annotator 2", "Judge"
    for k, l in enumerate(LABELS, 19):
        sm[f"A{k}"] = l
        sm[f"B{k}"] = f'=COUNTIF({A},"{l}")'
        sm[f"C{k}"] = f'=COUNTIF({B},"{l}")'
        sm[f"D{k}"] = f'=COUNTIF({J},"{l}")'
    sm["A22"], sm["B22"] = "Rows still needing adjudication", f'=COUNTIF(Label!$L$2:$L${last},"NO")-COUNTIFS(Label!$L$2:$L${last},"NO",Label!$M$2:$M${last},"<>")'
    for row in sm.iter_rows(min_row=3, max_row=22):
        for c in row:
            if c.font is None or not c.font.bold:
                c.font = Font(name=FONT, size=10, bold=c.font.bold if c.font else False)
    sm.column_dimensions["A"].width = 70
    for col in "BCD":
        sm.column_dimensions[col].width = 14

    out = ROOT / f"results/{run}/judge_validation_{run}.xlsx"
    wb.save(out)
    print(f"wrote {out.relative_to(ROOT)} ({n} rows)")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "batch01_pilot_r2")
