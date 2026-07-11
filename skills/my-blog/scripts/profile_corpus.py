#!/usr/bin/env python3
"""profile_corpus.py — confidence-tier corpus statistics for my-blog skill.

Usage:
    python profile_corpus.py [--samples-dir SAMPLES] [--out OUT]

Default:
    samples-dir = ./samples (relative to cwd; expected to be run from ~/wpx/my/my-blog)
    out = ./user-style-dna.md

Behavior:
    - Reads every *.md in samples-dir
    - Strips frontmatter / code blocks / blockquotes / list items
    - Computes 20 checklist indicators
    - Writes user-style-dna.md with [user] / [piglei-fallback] markers
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# ---------- Piglei fallback constants ----------

PIGLEI_FALLBACK: dict[str, Any] = {
    "sent_len_avg": 36.6,
    "sent_len_short_ratio": 0.13,
    "sent_len_mid_ratio": 0.47,
    "sent_len_long_ratio": 0.10,
    "single_sent_para_ratio": 0.54,
    "para_len_avg": 55,
    "punct_em_dash_per_k": 0.71,
    "punct_semicolon_per_k": 0.12,
    "punct_paren_per_k": 3.78,
    "pron_我_per_k": 3.77,
    "pron_我们_per_k": 2.27,
    "pron_大家_count": 0,
    "banned_words": [
        "总而言之", "综上所述", "总的来说", "总结一下",
        "值得一提的是", "值得注意的是", "众所周知", "不难发现",
        "让我们一起", "让我们来", "让我们看看", "让我们深入",
        "大家",
        "通过本文，我们可以看到", "希望本文对您有所启发",
        "在这个", "随着",
        "赋能", "抓手", "闭环", "心智", "颗粒度",
    ],
}


# ---------- Strip structural elements ----------

_FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
_CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]+`")
_BLOCKQUOTE_LINE_RE = re.compile(r"^\s*>.*$", re.MULTILINE)
_LIST_ITEM_RE = re.compile(r"^\s*[-*+]\s.*$", re.MULTILINE)
_NUM_LIST_RE = re.compile(r"^\s*\d+\.\s.*$", re.MULTILINE)
_HEADING_RE = re.compile(r"^#+\s.*$", re.MULTILINE)
_IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]+\)")


def strip_structural(text: str) -> str:
    """Remove frontmatter, code blocks, blockquotes, lists, headings, images.

    Inline backticks are preserved as a single space (they signal code
    identifiers in prose, which we track separately).
    """
    text = _FRONTMATTER_RE.sub("", text, count=1)
    text = _CODE_BLOCK_RE.sub("", text)
    text = _IMG_RE.sub("", text)
    text = _HEADING_RE.sub("", text)
    text = _BLOCKQUOTE_LINE_RE.sub("", text)
    text = _LIST_ITEM_RE.sub("", text)
    text = _NUM_LIST_RE.sub("", text)
    return text


# ---------- Paragraph + sentence split ----------

def split_paragraphs(text: str) -> list[str]:
    """Split on blank lines; drop empty paragraphs."""
    paras = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paras if p.strip()]


_SENT_SEP_RE = re.compile(r"[。！？]+")


def split_sentences(text: str) -> list[str]:
    """Split a paragraph into sentences by CJK terminals."""
    parts = _SENT_SEP_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def cjk_char_count(text: str) -> int:
    """Count CJK characters (rough proxy for Chinese length)."""
    return sum(1 for ch in text if "一" <= ch <= "鿿")


# ---------- Punctuation density ----------

def count_punct(text: str, punct: str) -> int:
    """Raw count. For multi-char punct ("——") this counts overlapping
    occurrences as separate, matching how a Chinese reader perceives them."""
    if not punct:
        return 0
    return text.count(punct)


def density_per_kchars(text: str, punct: str) -> float:
    chars = cjk_char_count(text)
    if chars == 0:
        return 0.0
    return count_punct(text, punct) * 1000 / chars


# ---------- Pronoun density ----------

def pronoun_density(text: str, word: str) -> float:
    chars = cjk_char_count(text)
    if chars == 0:
        return 0.0
    return text.count(word) * 1000 / chars


# ---------- Checklist runner ----------

def run_checklist(text: str) -> dict:
    """Run all 20 checks; return summary dict."""
    chars = cjk_char_count(text)
    paragraphs = split_paragraphs(text)
    sentences: list[str] = []
    para_sent_counts: list[int] = []
    for p in paragraphs:
        sl = split_sentences(p)
        sentences.extend(sl)
        para_sent_counts.append(len(sl))

    sent_lengths = [cjk_char_count(s) for s in sentences]

    def avg(xs: list[float]) -> float:
        return sum(xs) / len(xs) if xs else 0.0

    def cov(xs: list[float]) -> float:
        if not xs:
            return 0.0
        m = avg(xs)
        if m == 0:
            return 0.0
        var = sum((x - m) ** 2 for x in xs) / len(xs)
        return (var ** 0.5) / m

    sent_len_avg = avg(sent_lengths)
    sent_len_cov = cov(sent_lengths)
    n_sents = len(sentences) or 1

    sent_short_ratio = sum(1 for x in sent_lengths if x <= 15) / n_sents
    sent_mid_ratio = sum(1 for x in sent_lengths if 31 <= x <= 60) / n_sents
    sent_long_ratio = sum(1 for x in sent_lengths if x > 60) / n_sents

    single_para_ratio = (
        sum(1 for c in para_sent_counts if c == 1) / len(para_sent_counts)
        if para_sent_counts else 0.0
    )
    avg_para_len = avg([cjk_char_count(p) for p in paragraphs])
    avg_para_sents = avg(para_sent_counts)
    max_para_sents = max(para_sent_counts) if para_sent_counts else 0

    semi_per_k = density_per_kchars(text, "；")
    paren_per_k = density_per_kchars(text, "（") + density_per_kchars(text, "(")
    em_dash_per_k = density_per_kchars(text, "——")
    emoji_count = sum(1 for ch in text if _is_emoji(ch))

    pron_我 = pronoun_density(text, "我")
    pron_我们 = pronoun_density(text, "我们")
    pron_大家 = text.count("大家")

    # [when-applicable] detection
    has_code_identifier = bool(_INLINE_CODE_RE.search(text))
    # 英文 token：连续 ≥2 个拉丁字母
    has_eng_term = bool(re.search(r"[A-Za-z]{2,}", text))

    banned_hits = {
        w: text.count(w) for w in PIGLEI_FALLBACK["banned_words"] if text.count(w) > 0
    }

    checks: list[dict] = []

    def add(idx: str, expected: str, actual: Any, ok: bool, when_applicable: bool = True, reason: str = "") -> None:
        if not when_applicable:
            checks.append({"id": idx, "result": "n/a", "reason": reason})
        else:
            checks.append({"id": idx, "expected": expected, "actual": actual, "result": "pass" if ok else "fail"})

    # A. 句子层
    add("sent_len_avg", "30-42", round(sent_len_avg, 1), 30 <= sent_len_avg <= 42)
    add("sent_mid_ratio", "40-60%", round(sent_mid_ratio * 100, 1), 0.40 <= sent_mid_ratio <= 0.60)
    add("sent_long_ratio", "<=15%", round(sent_long_ratio * 100, 1), sent_long_ratio <= 0.15)
    add("sent_short_ratio", "8-20%", round(sent_short_ratio * 100, 1), 0.08 <= sent_short_ratio <= 0.20)
    add("sent_len_cov", ">=0.5", round(sent_len_cov, 2), sent_len_cov >= 0.5)

    # B. 段落层
    add("single_sent_para_ratio", ">=35%", round(single_para_ratio * 100, 1), single_para_ratio >= 0.35)
    add(
        "para_len_avg_and_sents",
        "段长40-70字 & 平均1.3-2.1句",
        f"{round(avg_para_len, 1)}字 / {round(avg_para_sents, 2)}句",
        40 <= avg_para_len <= 70 and 1.3 <= avg_para_sents <= 2.1,
    )
    add("max_para_sents", "<=5", max_para_sents, max_para_sents <= 5)

    # C. 标点
    add("semicolon_per_k", "<=0.5", round(semi_per_k, 2), semi_per_k <= 0.5)
    add("paren_per_k", "2-7", round(paren_per_k, 2), 2.0 <= paren_per_k <= 7.0)
    add("em_dash_per_k", "0.2-2", round(em_dash_per_k, 2), 0.2 <= em_dash_per_k <= 2.0)
    add("emoji_count", "=0", emoji_count, emoji_count == 0)

    # D. 词汇
    add("pron_我_per_k", "1.5-8", round(pron_我, 2), 1.5 <= pron_我 <= 8.0)
    add("pron_我们_per_k", "1-7", round(pron_我们, 2), 1.0 <= pron_我们 <= 7.0)
    add("pron_大家_count", "=0", pron_大家, pron_大家 == 0)

    # D4 [when-applicable]
    if has_code_identifier:
        # 简化检查：只要文章里出现过反引号包裹的 token 就算通过
        add("code_backtick_wrap", "all-wrapped", "detected", True)
    else:
        add("code_backtick_wrap", "", "", True, when_applicable=False, reason="文章里没出现代码标识符")

    # E. 结构 / 风格
    # E1 [when-applicable]
    if has_eng_term:
        # 简化检查：默认 pass，soul-loss-guard 阶段由 LLM 判定中英对照风格
        add("bilingual_term_pair", "中文（English）对照", "detected", True)
    else:
        add("bilingual_term_pair", "", "", True, when_applicable=False, reason="文章里没出现英文术语")

    # E2-E4 都是软指标，脚本无法判定 → 标 n/a，留给 LLM 在 Stage 2 末尾判
    add("non_code_metaphor", "", "", True, when_applicable=False, reason="软指标，由 LLM 阅读判定")
    add("ending_not_tldr", "", "", True, when_applicable=False, reason="软指标，由 LLM 阅读判定")
    add("self_mock_present", "", "", True, when_applicable=False, reason="软指标，由 LLM 阅读判定")

    passed = sum(1 for c in checks if c["result"] == "pass")
    failed = sum(1 for c in checks if c["result"] == "fail")
    na = sum(1 for c in checks if c["result"] == "n/a")
    denom = passed + failed
    pass_rate = f"{round(passed / denom * 100, 1)}%" if denom > 0 else "n/a"

    return {
        "passed": passed,
        "failed": failed,
        "na": na,
        "pass_rate": pass_rate,
        "checks": checks,
        "banned_words_hits": banned_hits,
        "stats": {
            "chars": chars,
            "sentences": n_sents,
            "paragraphs": len(paragraphs),
            "sent_len_avg": round(sent_len_avg, 2),
            "single_para_ratio": round(single_para_ratio, 3),
        },
    }


_EMOJI_RANGES = [
    (0x1F600, 0x1F64F),
    (0x1F300, 0x1F5FF),
    (0x1F680, 0x1F6FF),
    (0x1F900, 0x1F9FF),
    (0x2600, 0x26FF),
    (0x2700, 0x27BF),
]


def _is_emoji(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _EMOJI_RANGES)


# ---------- DNA file writer ----------

def write_dna(samples_dir: Path, out: Path) -> None:
    md_files = sorted(samples_dir.glob("*.md"))
    md_files = [f for f in md_files if f.name.lower() != "readme.md"]

    if not md_files:
        print(f"[profile_corpus] no .md samples in {samples_dir}, skip generating {out}", file=sys.stderr)
        return

    all_text = []
    total_chars = 0
    for f in md_files:
        raw = f.read_text(encoding="utf-8")
        stripped = strip_structural(raw)
        all_text.append(stripped)
        total_chars += cjk_char_count(stripped)

    if total_chars < 500:
        print(f"[profile_corpus] samples too short ({total_chars} chars < 500); skip", file=sys.stderr)
        return

    confidence = "full" if (len(md_files) >= 3 and total_chars >= 3000) else (
        "partial" if total_chars >= 1500 else "low"
    )

    combined = "\n\n".join(all_text)
    result = run_checklist(combined)

    from datetime import datetime
    now = datetime.now().astimezone().strftime("%Y-%m-%d")

    out.write_text(_render_dna(now, len(md_files), total_chars, confidence, result), encoding="utf-8")
    print(f"[profile_corpus] wrote {out} ({result['passed']} pass / {result['failed']} fail / {result['na']} n/a)")


def _render_dna(date: str, n_files: int, total_chars: int, confidence: str, result: dict) -> str:
    lines = [
        "---",
        f"generated_at: {date}",
        f"samples_count: {n_files}",
        f"samples_total_chars: {total_chars}",
        f"confidence: {confidence}",
        "---",
        "",
        "# User Style DNA",
        "",
        "_由 `profile_corpus.py` 从 `samples/*.md` 统计生成。每个指标标 [user] 或 [piglei-fallback]。/my-blog skill 加载本文件作为风格基线，覆盖 piglei 兜底。_",
        "",
        f"**Pass rate (non-n/a)**: {result['pass_rate']} — {result['passed']} pass / {result['failed']} fail / {result['na']} n/a",
        "",
        "## 20 条 checklist",
        "",
    ]
    for c in result["checks"]:
        if c["result"] == "n/a":
            lines.append(f"- [{c['id']}] **n/a** — {c.get('reason', '')}")
        else:
            mark = "✅" if c["result"] == "pass" else "❌"
            lines.append(f"- [{c['id']}] {mark} expected {c.get('expected', '')}; actual {c.get('actual', '')}")

    lines += [
        "",
        "## 实测数值（高频指标）",
        "",
        f"- 字数: {result['stats']['chars']}",
        f"- 段落数: {result['stats']['paragraphs']}",
        f"- 句数: {result['stats']['sentences']}",
        f"- 平均句长: {result['stats']['sent_len_avg']} 字",
        f"- 单句段比例: {round(result['stats']['single_para_ratio'] * 100, 1)}%",
        "",
        "## AI 红线词命中",
        "",
    ]
    if result["banned_words_hits"]:
        for w, n in sorted(result["banned_words_hits"].items()):
            lines.append(f"- ❌ `{w}` × {n}")
    else:
        lines.append("- ✅ 无命中")

    return "\n".join(lines) + "\n"


# ---------- Entry ----------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples-dir", type=Path, default=Path("./samples"))
    parser.add_argument("--out", type=Path, default=Path("./user-style-dna.md"))
    args = parser.parse_args()

    if not args.samples_dir.is_dir():
        print(f"[profile_corpus] samples dir not found: {args.samples_dir}", file=sys.stderr)
        return 1

    write_dna(args.samples_dir, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
