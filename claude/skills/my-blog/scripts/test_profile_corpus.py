"""Tests for profile_corpus.py.

Run: cd ~/.claude/skills/my-blog/scripts && python -m unittest test_profile_corpus.py -v
"""
import unittest
from pathlib import Path

import profile_corpus as pc

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class TestStripStructural(unittest.TestCase):
    def test_strip_frontmatter(self):
        text = "---\ntitle: x\n---\n\n正文。"
        self.assertEqual(pc.strip_structural(text).strip(), "正文。")

    def test_strip_code_block(self):
        text = "正文一。\n\n```python\ncode\n```\n\n正文二。"
        result = pc.strip_structural(text)
        self.assertNotIn("code", result)
        self.assertIn("正文一", result)
        self.assertIn("正文二", result)

    def test_strip_blockquote(self):
        text = "正文。\n\n> 引用\n\n续。"
        result = pc.strip_structural(text)
        self.assertNotIn("引用", result)

    def test_strip_list_items(self):
        text = "正文。\n\n- 列表 1\n- 列表 2\n\n续。"
        result = pc.strip_structural(text)
        self.assertNotIn("列表 1", result)


class TestParagraphSplit(unittest.TestCase):
    def test_count_paragraphs(self):
        sample = (FIXTURE_DIR / "sample_post.md").read_text()
        stripped = pc.strip_structural(sample)
        paragraphs = pc.split_paragraphs(stripped)
        self.assertEqual(len(paragraphs), 4)


class TestSentenceSplit(unittest.TestCase):
    def test_split_chinese_sentences(self):
        text = "第一句。第二句！第三句？"
        self.assertEqual(pc.split_sentences(text), ["第一句", "第二句", "第三句"])

    def test_avg_sentence_length(self):
        sample = (FIXTURE_DIR / "sample_post.md").read_text()
        stripped = pc.strip_structural(sample)
        paragraphs = pc.split_paragraphs(stripped)
        total_sentences = sum(len(pc.split_sentences(p)) for p in paragraphs)
        self.assertEqual(total_sentences, 9)


class TestPunctuationDensity(unittest.TestCase):
    def test_em_dash_count(self):
        text = "前文——插入——后文"
        count = pc.count_punct(text, "——")
        self.assertEqual(count, 2)

    def test_per_thousand_chars(self):
        text = "啊" * 1000 + "。"
        density = pc.density_per_kchars(text, "。")
        self.assertEqual(density, 1.0)


class TestSingleSentenceParagraphRatio(unittest.TestCase):
    def test_single_sentence_ratio(self):
        sample = (FIXTURE_DIR / "sample_post.md").read_text()
        stripped = pc.strip_structural(sample)
        paragraphs = pc.split_paragraphs(stripped)
        single_count = sum(1 for p in paragraphs if len(pc.split_sentences(p)) == 1)
        # fixture 实际：段 1 "这是第一段。只有一句话。" 被 "。" 切成 2 句；
        # 段 2 / 段 3 多句；只有段 4 "第四段又是单句段。" 是真单句段
        self.assertEqual(single_count, 1)


class TestPronounDensity(unittest.TestCase):
    def test_first_person_密度(self):
        text = "我喜欢这个。我们都喜欢。" + "啊" * 980
        density_wo = pc.pronoun_density(text, "我")
        self.assertAlmostEqual(density_wo, 2.0, places=1)


class TestCheckList20(unittest.TestCase):
    """跑 20 条 checklist 判定 ✅/❌；当样本不触发条件时标 n/a"""

    def test_runs_all_20_checks(self):
        sample = (FIXTURE_DIR / "sample_post.md").read_text()
        stripped = pc.strip_structural(sample)
        result = pc.run_checklist(stripped)
        # 应该有 20 个 check items，每个 result 是 pass/fail/n/a
        self.assertEqual(len(result["checks"]), 20)
        for check in result["checks"]:
            self.assertIn(check["result"], ["pass", "fail", "n/a"])

    def test_backtick_wrap_na_when_no_code_identifiers(self):
        """fixture 文章正文里没有反引号 → code_backtick_wrap 应为 n/a"""
        sample = (FIXTURE_DIR / "sample_post.md").read_text()
        stripped = pc.strip_structural(sample)
        result = pc.run_checklist(stripped)
        backtick_check = next(c for c in result["checks"] if c["id"] == "code_backtick_wrap")
        self.assertEqual(backtick_check["result"], "n/a")


if __name__ == "__main__":
    unittest.main()
