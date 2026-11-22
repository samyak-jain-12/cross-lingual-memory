"""Prompt templates, verbatim from design_spec.md Appendix A (plus the filler-translation prompts [3.5])."""

READER_SYSTEM = (
    "You are a personal assistant with memory of your past conversations with this user.\n"
    "Answer the user's question using only what the user told you in past conversations.\n"
    "Answer in one short sentence, in the same language as the question.\n"
    "If the information is not in the past conversations, say that you don't know."
)


def reader_fc(sessions, query):
    blocks = []
    for k, sess in enumerate(sessions, 1):
        lines = [f"[Session {k}]"] + [f"{'User' if t['role'] == 'user' else 'Assistant'}: {t['content']}" for t in sess]
        blocks.append("\n".join(lines))
    user = "Past conversations:\n" + "\n\n".join(blocks) + f"\n\nCurrent question: {query}"
    return [{"role": "system", "content": READER_SYSTEM}, {"role": "user", "content": user}]


def reader_memories(memories, query):
    lines = "\n".join(f"{i}. {m}" for i, m in enumerate(memories, 1))
    user = ("Relevant memories from past conversations (may be incomplete or irrelevant):\n"
            f"{lines}\n\nCurrent question: {query}")
    return [{"role": "system", "content": READER_SYSTEM}, {"role": "user", "content": user}]


def judge(query, gold_en, aliases, response):
    user = (
        "You are grading an assistant's answer about a user's personal information.\n"
        f"Question: {query}\n"
        f"Gold answer: {gold_en}   Accepted forms: {'; '.join(aliases) if aliases else '(none)'}\n"
        f"Assistant answer: {response}\n"
        "The answer may be in English, Hindi (Devanagari) or Hinglish (romanized). Judge meaning, not language.\n"
        "Reply with exactly one word:\n"
        "CORRECT - states the gold information without contradiction\n"
        "INCORRECT - wrong, incomplete, lists several candidates, or contradicts the gold\n"
        "NO_ANSWER - says it does not know / has no information"
    )
    return [{"role": "user", "content": user}]


def judge_abstention(query, response):
    """Unanswerable controls: the only correct behaviour is to say it does not know."""
    user = (
        "You are grading an assistant's answer about a user's personal information.\n"
        f"Question: {query}\n"
        "Gold answer: the user never told the assistant this, so the assistant should say it does not know.\n"
        f"Assistant answer: {response}\n"
        "The answer may be in English, Hindi (Devanagari) or Hinglish (romanized). Judge meaning, not language.\n"
        "Reply with exactly one word:\n"
        "ANSWERED - gives some specific answer to the question\n"
        "NO_ANSWER - says it does not know / has no information"
    )
    return [{"role": "user", "content": user}]


def to_english(text):
    return [{"role": "user", "content":
             "Translate the following text to English. It may be Hindi, Hinglish (romanized Hindi) or English.\n"
             "Keep names, numbers and dates exactly. Output only the translation.\n"
             f"Text: {text}"}]


def to_hindi(text):
    return [{"role": "user", "content":
             "Translate the following text into natural, conversational Hindi written in Devanagari script.\n"
             "Keep brand and product names in Latin script, write person and place names in Devanagari, "
             "and keep digits as 0-9. Output only the translation.\n"
             f"Text: {text}"}]


HINGLISH_INSTRUCTION = (
    "Rewrite the following text in Hinglish: the casual Hindi-English mix used in Indian chat, "
    "with Hindi grammar, common English words mixed in, written ONLY in Roman (Latin) script. "
    "Never use Devanagari. Keep names, numbers and brand names unchanged. Output only the rewritten text.\n"
)

# Few-shot pairs (EN -> HG) from batch01 items F001 (team-verified), F002, P009. Showing the target
# style fixes the first pilot's failure, where Qwen3-8B answered in Devanagari for 77/160 filler turns.
HINGLISH_SHOTS = [
    ("I've been listening to audiobooks during my daily commute, which takes 45 minutes each way. "
     "Can you recommend some good fiction audiobooks?",
     "Main aajkal daily office aate-jaate audiobooks sunti hoon, ek side ka travel 45 minute ka hota hai. "
     "Kya aap kuch acchi fiction audiobooks suggest kar sakte hain?"),
    ("Congratulations on the new role! A simple system helps: scan receipts the same day, keep one folder "
     "per month, and log every expense in a spreadsheet with date, amount and purpose.",
     "Nayi job ki congratulations! Ek simple system follow kijiye: receipts usi din scan karein, har mahine ka "
     "alag folder rakhein, aur har expense ko date, amount aur purpose ke saath ek spreadsheet mein likhein."),
    ("You could use a little less honey and add cinnamon or cardamom for sweetness without sugar.",
     "Honey thoda kam karke sweetness ke liye cinnamon ya elaichi daal sakti hain."),
]


def to_hinglish(text):
    msgs = []
    for en, hg in HINGLISH_SHOTS:
        msgs += [{"role": "user", "content": HINGLISH_INSTRUCTION + f"Text: {en}"},
                 {"role": "assistant", "content": hg}]
    return msgs + [{"role": "user", "content": HINGLISH_INSTRUCTION + f"Text: {text}"}]


def romanize_hindi(hindi_text):
    """Fallback: turn an existing Devanagari Hindi translation into Roman-script Hinglish."""
    return [{"role": "user", "content":
             "Write the following Hindi text in Roman (Latin) script the way Indians type Hindi in chat "
             "(e.g. 'Main kal office gaya tha'). Write common English loanwords in English spelling. "
             "Do not output any Devanagari characters. Output only the romanized text.\n"
             f"Text: {hindi_text}"}]
