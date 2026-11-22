"""Phase 3, step 2: record the first-pass screening (design_spec.md §3.2) in candidates.csv.

Decisions below were made by reading every candidate. The team reviews the `keep` / `notes`
columns and may override any row before items are drafted.

Run from the project root:  python src/apply_screening.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data/candidates/candidates.csv"

# --- Facts: keep 50 of 64 -------------------------------------------------------------
FACT_DROP = {
    "FC107": "answer (Target) not stated in the evidence turn",
    "FC113": "needs world knowledge (Valentine's Day -> Feb 14)",
    "FC135": "answer is a clause, not a short slot",
    "FC144": "about an artist's album, not the user",
    "FC149": "sensitive (asylum status)",
    "FC124": "sensitive (religious belief)",
    "FC160": "sensitive (ethnicity)",
    "FC163": "reserve: fact about a third person (Alex)",
    "FC141": "reserve: vague evidence (conversation about destiny)",
    "FC117": "reserve: third Spotify item (FC109, FC148 kept)",
    "FC142": "reserve: overlaps FC120 (IKEA bookshelf)",
    "FC139": "reserve: second cocktail item (FC133 kept)",
}
FACT_TO_PREF = {
    "FC125": "moved to preference: favourite running-shoe brand",
    "FC140": "moved to preference: favourite type of rice",
}

# --- Preferences: 15 of 30 rewritable to a short-answer question --------------------------
PREF_KEEP = {
    "PC075": "Q: Which video editing software do I enjoy using? -> Adobe Premiere Pro",
    "PC076": "Q: Which camera brand do I use? -> Sony",
    "PC078": "Q: Apart from views, what hotel features do I like? -> rooftop pool; hot tub on the balcony",
    "PC080": "Q: Which comedy special do I like for its storytelling? -> John Mulaney's Kid Gorgeous",
    "PC081": "Q: By what time do I prefer to wind down at night? -> 9:30 pm",
    "PC085": "Q: Which herbs have I been using in my cooking? -> basil and mint",
    "PC089": "Q: Which sugar do I find gives a richer flavour? -> turbinado sugar",
    "PC090": "Q: What flavour of cake do I like baking? -> lemon",
    "PC091": "Q: Which furniture design style do I like? -> mid-century modern",
    "PC092": "Q: Which guitar am I thinking of upgrading to? -> Gibson Les Paul (built-in near-miss: Fender Stratocaster)",
    "PC093": "Q: Which milk do I use for my homemade creamer? -> almond milk",
    "PC098": "Q: What do I like to pair my meal-prep vegetables with? -> quinoa",
    "PC099": "Q: Which city's music scene do I love? -> Denver",
    "PC100": "Q: Where do I usually watch documentaries? -> Netflix",
    "PC103": "Q: Which podcast genres do I listen to on my commute? -> true crime and self-improvement",
}
PREF_DROP_REASON = "no single preferred entity to ask about (vague, factual, yes/no-guessable, or alcohol/US-specific)"

# --- Events: keep 50 of 83 ---------------------------------------------------------------
EVENT_KEEP = {
    "EC001", "EC002", "EC003", "EC004", "EC005", "EC009", "EC010", "EC012", "EC013", "EC014",
    "EC015", "EC017", "EC019", "EC020", "EC022", "EC023", "EC024", "EC026", "EC029", "EC030",
    "EC031", "EC032", "EC034", "EC035", "EC036", "EC039", "EC040", "EC041", "EC042", "EC043",
    "EC044", "EC045", "EC046", "EC047", "EC048", "EC049", "EC052", "EC054", "EC055", "EC057",
    "EC062", "EC063", "EC064", "EC065", "EC066", "EC069", "EC071", "EC072", "EC172", "EC176",
}
EVENT_DROP = {
    "EC006": "future event", "EC033": "future event", "EC070": "future event",
    "EC074": "future event", "EC169": "future event", "EC175": "future event",
    "EC177": "event did not happen (missed)",
    "EC007": "religious service detail", "EC008": "fragment + religious service",
    "EC011": "fragment + religious service", "EC059": "religious service detail",
    "EC060": "religious service detail", "EC061": "fragment + religious service",
    "EC027": "fragment (starts mid-sentence)", "EC050": "fragment + medical",
    "EC051": "fragment + medical", "EC028": "medical procedure",
    "EC021": "US-specific brand, weak event", "EC025": "date range; overlaps fact FC146 (Hawaii)",
    "EC174": "date range; overlaps fact FC151 (Japan)", "EC037": "duplicate of EC036",
    "EC038": "no object stated ('I got them')", "EC053": "same item as EC052",
    "EC056": "duplicate of EC055", "EC067": "date range", "EC068": "date range",
    "EC073": "list of many dates", "EC170": "magazine issue date, not an event",
    "EC171": "not personal (conference deadline)", "EC173": "duplicate of EC172",
    "EC016": "topic cap: charity runs (5 kept)", "EC018": "topic cap: charity events (5 kept)",
    "EC058": "topic cap: charity runs (5 kept)",
}


def main():
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    for r in rows:
        cid = r["cand_id"]
        if r["type"] == "fact":
            if cid in FACT_TO_PREF:
                r["keep"], r["notes"] = "Y", FACT_TO_PREF[cid]
                r["type"] = "preference"
            elif cid in FACT_DROP:
                r["keep"] = "RESERVE" if FACT_DROP[cid].startswith("reserve") else "N"
                r["notes"] = FACT_DROP[cid]
            else:
                r["keep"], r["notes"] = "Y", ""
        elif r["type"] == "preference":
            r["keep"], r["notes"] = ("Y", PREF_KEEP[cid]) if cid in PREF_KEEP else ("N", PREF_DROP_REASON)
        elif r["type"] == "event":
            if cid in EVENT_KEEP:
                r["keep"], r["notes"] = "Y", ""
            else:
                r["keep"], r["notes"] = "N", EVENT_DROP.get(cid, "not selected")

    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    kept = Counter(r["type"] for r in rows if r["keep"] == "Y")
    print("kept:", dict(kept), "| reserves:", sum(r["keep"] == "RESERVE" for r in rows))
    unexplained = [r["cand_id"] for r in rows if r["type"] == "event" and r["keep"] == "N"
                   and r["notes"] == "not selected"]
    print("events dropped without a reason:", unexplained or "none")


if __name__ == "__main__":
    main()
