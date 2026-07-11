---
description: 把中文/英文 epub 改写成 B2 英文 epub —— 每章派一个 Task subagent
---

把 `$ARGUMENTS` 指向的 epub 改写成 B2 英文 epub。

**支持两种源**：
- 中文 epub → 翻译 + B2 简化（保留情节、人名、对话）
- 英文 epub → 只做 B2 简化（保持原作者笔触，把 C1+ 词汇/复杂句替换成 B2 表达）

源语言由主 agent 在第 3 步按 master-src.md 的 CJK 占比判别：> 30% 走中文源、< 5% 走英文源、5%–30% 含义不清时询问用户。

## 项目根目录

`/Users/peixian/wpx/my/epub-en`

所有脚本路径都基于这个根，绝对路径写死，不依赖 cwd。

## 流程

### 第 1 步：参数校验

- `$ARGUMENTS` 是 epub 文件路径（绝对或相对于当前 cwd）
- 校验：文件存在、扩展名 `.epub`
- 不存在 → 直接报错并停

### 第 2 步：unpack

```bash
cd /Users/peixian/wpx/my/epub-en
bash scripts/unpack.sh <epub_path>
```

捕获 stdout 末行的 8 位 sha1。失败 → 报错并停。

定义：
- `BOOK_DIR=/Users/peixian/wpx/my/epub-en/.cache/<sha1>`
- 中文章节目录 = `$BOOK_DIR/chapters/src/`
- 英文章节目录 = `$BOOK_DIR/chapters/en/`

### 第 3 步：判别源语言 + 生成术语表（你自己做，不派 subagent）

**先判源（按 CJK 占比，不是 0/1 判定）**：

1. 校验 `$BOOK_DIR/master-src.md` 存在且 size > 0；缺失或空 → abort 并提示人工检查（**不要静默回退**）。
2. 计算正文 CJK 占比（**字符数，不是字节数**——UTF-8 下 CJK 占 3 字节，用 `wc -c` 会把占比压低约 3 倍）：
   ```bash
   total=$(wc -m < "$BOOK_DIR/master-src.md" | xargs)
   cjk=$(rg -o '[一-鿿]' "$BOOK_DIR/master-src.md" | wc -l | xargs)
   # 占比 = cjk / total，阈值 30%
   ```
3. 占比 > 30% → **中文源**（`SOURCE_LANG=zh`）
4. 占比 < 5% → **英文源**（`SOURCE_LANG=en`）—— 容许英文书里有少量 CJK 引用 / 版权信息
5. 5%–30% 之间 → 含义不清（双语 / 翻译稿），**不要自动选**，列出占比让用户确认走哪条路

记下 `SOURCE_LANG`，后续流程据此分支。

#### 中文源：抽中→英术语表

1. `rg -o '[一-鿿]{2,4}' $BOOK_DIR/chapters/src/*.md | sort | uniq -c | sort -rn | head -200` 抓高频候选
2. 过滤通用词停用列表（的/了/在/是/我/你/他/她/这/那/和/也/就/都/还/不/没/有/会/能/要/想/到/上/下/中/里/外/前/后/左/右/给/被/把/让/作/做/来/去/对/着/过/又/再/也/还/才/最/很/真/太/挺/特别/比较/可能/也许/或许 等）
3. 对剩下的候选（人名 / 地名 / 独有概念）决定英文写法：
   - 人名 → pinyin（首字母大写，姓在前）：`林黛玉` → `Lin Daiyu`
   - 地名 → pinyin 或意译，看是否家喻户晓：`大观园` → `Grand View Garden`，`北京` → `Beijing`
   - 独有概念 → pinyin + 英文同位语，或纯意译：`阴阳` → `yin and yang`
4. 写到 `$BOOK_DIR/glossary.json`：

```json
{"林黛玉": "Lin Daiyu", "贾宝玉": "Jia Baoyu", "大观园": "Grand View Garden"}
```

#### 英文源：抽专有名词锁定表

英文源的 glossary 用途**不是翻译查找**，而是**锁定专有名词全书一致**（防止 subagent 把人名 / 地名 / 独有概念也"简化"成普通名词）。

⚠️ **宁缺毋滥**：glossary 里的词 subagent 会按"必须保留的专有名词"处理。如果误收普通词（如 "The"、"Chapter"、章节标题词），subagent 不会再简化这些词，与 B2 化目标冲突。

1. 抓连续大写词组：
   ```bash
   rg -oN '\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b' $BOOK_DIR/chapters/src/*.md \
     | sort | uniq -c | sort -rn | head -200
   ```
2. **严格过滤** —— 以下情况一律不写入 glossary：
   - markdown heading 行里出现的（章节标题往往含大写词）
   - 仅在句首出现的常见词（"The"、"And"、"But"、"When"、"After" 等）
   - Title Case 普通词或代词（"He"、"She"、"It"、"They" 在某些标点后）
   - 拿不准是不是专有名词 → 不写
3. 只留**确定的独有专有名词**：人名（`Sherlock Holmes`）、地名（`London`、`Baker Street`）、机构（`Scotland Yard`）、独有概念（`Pensieve`、`Quidditch`、`Hogwarts`）
4. 写到 `$BOOK_DIR/glossary.json`，**key 与 value 相同**（保留原写法）：

```json
{"Sherlock Holmes": "Sherlock Holmes", "Baker Street": "Baker Street", "Scotland Yard": "Scotland Yard"}
```

5. 一个专有名词都没识别出来 → 写空对象 `{}`，**不要跳过这一步**：

```json
{}
```

候选 > 200 → 截前 100 高频；其余靠 subagent 现场判断。**v1 偏保守，宁可漏收 5 个真专有名词，也不要误收 1 个普通词把 subagent 锁死在不能简化上。**

### 第 4 步：生成风格指南

写 `$BOOK_DIR/style-guide.md`，给所有 chapter agent 共享。**第一段必须显式声明源语言**让 subagent 知道走哪条路。

#### 中文源模板

主 agent 写 style-guide 前，先读 `master-src.md` 前 2000 字符判断体裁，据此填入时态和人称：
- 小说 / 叙事 → simple past + third person（或跟随原文人称）
- 论说文 / 非虚构 / 自传 → simple present + first person
- 格言集 / 语录 / 对话录 → simple present + second person 或无人称
- 拿不准 → 问用户

```markdown
# Style Guide

## Source

Source language: Chinese. Task = convey the meaning naturally in B2 English; prioritize readability over literal fidelity.

## Conventions

- Tense: <主 agent 按体裁填入>
- POV: <主 agent 按体裁填入>
- Dialogue: double quotes, "said" + variants
- Paragraph indent: none
- Chapter heading: "# Chapter N: <Title>"
- Honorifics: keep pinyin (e.g. "Brother Bao")
- Names: pinyin per glossary; surname first
```

#### 英文源模板

```markdown
# Style Guide

## Source

Source language: English. Task = simplify in place to B2; do NOT retranslate or rewrite the narrative.

## Conventions

- Preserve original tense, POV, dialogue style, paragraph structure
- Replace C1+ vocabulary with B2 equivalents (e.g. "ubiquitous" → "common", "elucidate" → "explain")
- Break overly long / nested sentences into 2-3 short B2 sentences
- Keep the author's voice: tone, pacing, idiom choices stay close to source
- All proper nouns from glossary must appear unchanged (don't "simplify" character / place names)
- Don't drop scenes, dialogue, or plot points
```

如有其他适配（对话体标点、特殊术语处理等）写在 `## Conventions` 下。

### 第 5 步：派 Task subagent 改章

扫 `$BOOK_DIR/chapters/src/ch-*.md`，对每个**未缓存**的章节（即 `chapters/en/<basename>-en.md` 不存在或 size = 0）派一个 Task。

**并发控制**：每批最多 8 个 Task；批与批之间串行。

**Task 调用**：

- subagent_type: general-purpose
- model: sonnet  ← 翻译/改写任务 sonnet 够用，不必上 opus
- description: 改写章节 <ch-NN>
- prompt: 见下方 Subagent Prompt 模板

#### Subagent Prompt 模板

```
你的任务：把本章改写成自然流畅的 B2 英文。读者是中等英文水平的中文母语者，要能不查词读完，享受故事本身。

输入文件: <BOOK_DIR>/chapters/src/ch-NN.md
输出文件: <BOOK_DIR>/chapters/en/ch-NN-en.md
术语表: <BOOK_DIR>/glossary.json     ← 人名/地名/独有概念的一致性参考
风格指南: <BOOK_DIR>/style-guide.md   ← 必读首段判源语言

## 核心原则

**阅读流畅性 > 原文忠实度**。冲突时永远选流畅。允许删减次要细节、合并描写段、改写句式，只要保留剧情主线、人物情感、对话、氛围。

## 步骤（中文源）

1. 完整读源章节，理解情节和情感
2. 用自然英文重新叙述这段故事——不是逐句翻译，是用英文作家的方式讲
3. 词汇控制在 Oxford 5000（B2）内；遇到无替代的难词用最常见的近义词，不解释、不加括号
4. 中文成语 / 典故 / 网文专属概念（"叶公好龙"、"穿越"、"修仙"、"金手指"、"打脸"）用自然英语**重写**或**替代**，**严禁字面直译**
5. 长复合句拆成 2-3 个短句；不连续堆叠 4+ 个具体名词（一段把桌子上 8 件物品全列出 → 只挑 1-2 件最关键的写）
6. 意识流碎片（"痛！好痛！"、"嘶..."、"赶紧醒！赶紧醒！"）改成完整、节奏自然的句子
7. 专有名词第一次出现通过上下文自然交代身份；**不要**括号、脚注、"[Note: ...]" 注释
8. 用 Write 工具写到输出文件

## 步骤（英文源）

1. 完整读源章节
2. 把 C1+ 词换成 B2 同义词；嵌套长句拆成 2-3 短句
3. 保持原作者笔触（tone、pacing、对话风格、段落结构）；**不重写情节、不改人称时态**
4. 专有名词从 glossary 逐字保留——人名 / 地名 / 独有概念不要"简化"
5. 用 Write 工具写到输出文件

## 一致性（两种源都遵守）

- glossary 里的写法 → **必须用**（最高优先级）
- glossary 没列的，但你识别出本书是知名作品（如《诡秘之主》→ *Lord of the Mysteries*、《三体》→ *The Three-Body Problem*、《红楼梦》→ *Dream of the Red Chamber*、《全职高手》→ *The King's Avatar* 等）→ 跟该作品已有英译的标准译法（次要人名、地名、独有概念、标志性场景）
- 完全陌生的书 → 按通用规则现场判断，保持本章内一致

## 通用约束

- heading（# / ## / ###）层级和数量与原文**严格一致**——即使某个 ### 看起来像 calibre 副标题也必须保留并翻译
- 不写"译者注"或元注释
- 输出只有英文 markdown，不要 wrap 在代码块里
- 不修改输入文件；不碰输出文件之外的任何文件

## 反例对照（不要这样写）

| 中文原文 | ❌ AI 直译 | ✅ 流畅 B2 |
|---|---|---|
| 痛！好痛！头好痛！ | Pain! So much pain! His head was killing him! | The pain woke him up. His head hurt so much that everything else faded away. |
| 一阵又一阵的抽痛让他点滴积累起虚幻的力量 | Wave after wave of pain slowly fed him a thin, unsteady strength. | After a while the pain gave him just enough strength to move. |
| 这大概就是所谓的叶公好龙吧 | being a fan of dragons until you actually meet one | He had read about this kind of thing in stories many times. But now that it was really happening, he could hardly believe it. |
| 笔记本左侧靠桌子边缘有一叠书...右手边的墙上...斜下方一个墨水瓶...笔记本右侧一根钢笔...笔帽搁于左轮手枪旁边 | (照原文空间关系把 8 件物品逐一列出) | On the desk lay an open notebook, an old fountain pen, an inkwell, and—oddly—a brass-colored revolver. |

完成后简短报告：源语言 + 完成 / 失败 + 任何疑问。
```

### 第 6 步：lint 验证

每个 subagent 返回后，跑：

```bash
cd /Users/peixian/wpx/my/epub-en
.venv/bin/python -m scripts.lib.lint_chapter \
    "$BOOK_DIR/chapters/src/ch-NN.md" \
    "$BOOK_DIR/chapters/en/ch-NN-en.md"
```

lint 只兜底两件事：heading 层级数量对齐 + 英文输出不含 CJK。质量靠 prompt 把控，不靠 lint 卡位。

- exit 0 → 通过，进入下一章
- exit ≠ 0 → 把 stderr 的 lint 错误塞进 prompt，重派 1 次（**就 1 次，不无限重试**）：

```
你之前的输出有 lint 失败。错误如下：

<lint stderr 内容>

请重新读输入文件并修正这些问题，再次写到同一输出文件。
```

二次 lint 仍失败 → 把这章记入 `failed_chapters` 列表，继续别的章。

### 第 7 步：repack

如果 `failed_chapters` 非空：报错并列出哪些章失败，**不**调 repack；让用户决定是否手动修。

否则：

```bash
cd /Users/peixian/wpx/my/epub-en
bash scripts/repack.sh <sha1>
```

捕获 stdout 末行的输出 epub 路径。

### 第 8 步：报告

向用户输出：

```
✓ <epub 原标题> → <output 路径>
- 章节总数：N
- 本次新翻译：M
- 缓存命中：N - M
- lint 失败重派：K（成功 K - L，最终失败 L 章 → 列出）
```

如果有失败章，明确告诉用户：

```
失败章节：
  - chapters/en/ch-03-en.md  (lint: heading mismatch: zh=[1,2,2] en=[1,2])
  - chapters/en/ch-07-en.md  (lint: CJK chars in english output: 修仙宗门...)

修法：
  rm <BOOK_DIR>/chapters/en/ch-03-en.md  # 删了让重跑
  /my-epub-en <epub_path>                 # 续跑
```

## 边界

- `$ARGUMENTS` 空 → 反问"epub 路径？"
- 路径不存在 → 直接报错
- 第三章超长被切成 ch-03a / ch-03b → 主流程对每个文件单独派 subagent，repack 时按字典序拼回 reader 看不到拆分痕迹
- 用户中断 → 已写 chapters/en/ 的章节保留；下次跑命中缓存自然续上
- pandoc 不存在 → unpack.sh 报错；提示用户 `brew install pandoc`
