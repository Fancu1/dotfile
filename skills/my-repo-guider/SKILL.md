---
name: my-repo-guider
description: Use whenever the user asks you to explain, walk through, or deep-dive a specific piece of existing code — a function, class, method, file, flow, or module they've opened or selected. Covers explanations in any project and any language. Key behaviors it enforces: (1) every code reference gets a clickable `[filename:N](path#LN)` link, (2) explain concepts (what it represents / why it exists / what happens without it) BEFORE translating code, (3) target a ~1-year-experience developer with plain language, (4) end with a concrete business scenario that walks the code through with specific values, (5) NEVER open with analogies like "想象一家餐厅" / "就像快递单号". Use this skill aggressively — invoke it for phrases like "讲一下这个函数", "这段代码在干嘛", "深入这个方法", "解释这段实现", "讲讲 XXX", "walk me through this", "explain this code", and for ANY follow-up that says "继续深入" / "再讲讲" on an active explanation thread. Use it even when the user doesn't explicitly say "explain" — if they selected code and asked about it, this skill applies.
---

# My Repo Guider

## 定位

用户指着一段**已有代码**问"这在干嘛"、"深入讲讲"。这个 skill 规定**怎么讲**，不规定讲什么——讲什么由用户指定的代码决定。

和 `my-repo-teacher` 的区别：
- **my-repo-teacher**：老师带学生从零读项目，一问一答验证理解
- **my-repo-guilder**：用户已经有具体目标，想单向听懂某段代码；你讲清楚就行，不需要反问

## 核心原则

### 原则 1：每个代码论断带可点击行号链接

VSCode 的 markdown 格式 `[filename:N](path#LN)` 让用户直接点击跳转。**每个涉及代码的论断都要配行号**。

- 单行：`[app_generator.py:173](api/.../app_generator.py#L173)`
- 范围：`[app_generator.py:150-200](api/.../app_generator.py#L150-L200)`

**行号先读文件再写**。凭记忆的行号错了比不给行号更糟——用户点过去看到无关的代码，会直接失去信任。

### 原则 2：讲"是什么/为什么/用来干嘛"，不要翻译代码

用户工作经验大约 1 年。**堆术语 ≈ 没讲**。对每个关键变量/字段/参数/概念，先回答三件事：

1. **它代表什么业务概念？**（不是类型，是含义）
2. **为什么需要它？**（它解决什么问题）
3. **有/没有它分别会怎样？**（给对比感）

**反例（翻译代码）**：
> `if conversation_id: conversation = ConversationService.get_conversation(...)` —— 有 conversation_id 就加载对应会话记录

**正例（讲概念）**：
> `conversation_id` 是判断新老对话用的。传了 = 用户在继续之前的对话，从数据库把那条会话查出来（里面有历史消息、当时用的模型配置）。没传 = 新对话，后面会新建一条记录。
>
> 为啥要分新老？因为"我刚才叫什么来着"只有在**同一条对话**里才有意义。

"正例" 讲清楚了 `conversation_id` 在**业务上**是什么、为什么需要它、两种分支分别意味着什么。用户即使不看代码也知道这块在干嘛。

### 原则 3：禁止开场类比

以下开场句式**禁用**：

- "想象一下…"
- "就像…一样"
- "把它当作…"
- "好比一家餐厅/快递/门禁/前台…"

先**正常讲代码本身是干嘛**。需要小比方解释某个抽象概念时可以在**中段**用一下，但**不要以此开头**。

**为什么禁止**：开场类比会让讲解显得不自然，而且类比越生动越容易偏离代码本身（用户反馈过"太跳跃"）。

### 原则 4：结尾用一个真实业务场景串一遍

讲完所有细节后，用 **"某个用户在某个页面做了某个具体操作 → 这段代码怎么走 → 最终看到什么"** 把整条链路串一遍。

场景要**具体**：
- 带具体参数值，不是"用户发消息"，而是"用户发了 `query='订单状态？'`, `conversation_id='conv-abc'`"
- 带时间轴或步骤编号
- 带预期结果（前端/数据库/日志里看到什么）

这一步让用户把零散的代码片段和真实调用**对应起来**。很多用户会反馈"讲完场景才真的懂"。

## 标准响应结构

这是推荐模板，**不是强制格式**——简单问题可以砍段，复杂问题可以加图。关键是"行号 / 概念先行 / 场景收尾" 这三件事该有就要有。

```markdown
## 这段代码在干嘛（一句话定位 + 行号）
它是 X（在 [file:N](path#LN)），负责 Y。

## 先搞清楚几个核心概念
（对后面反复出现的关键变量/概念，先讲是什么/为什么/用来干嘛；简单问题可以跳过这段）

### 概念 A
...

### 概念 B
...

## 代码流程（分步骤，带行号）

### 第 1 步：做什么
[file:N-M](path#LN-LM)

```code
关键几行代码片段
```

大白话解释：为什么要这步、不做会怎样、这步的输出给谁用。

### 第 2 步：...
...

## 用一个真实场景串起来
**场景**：{谁} 在 {哪个页面} 做了 {什么具体操作}，参数 {具体值}

1. 步骤 1：代码走到哪一行，做了什么，拿到什么
2. 步骤 2：...
...
```

## 写作细节

- **术语第一次出现**：用破折号或括号补一句人话：`RAG（检索增强生成 —— 查资料库 → 结果塞进 prompt 让 LLM 参考）`
- **代码片段**：只引用关键几行，不要把整段函数粘一遍（用户能通过行号跳过去看）
- **加粗**：仅用于"反直觉"或"容易错过"的点，不要滥用
- **表格**：并列场景（多个模式、多个分支）用表格对比
- **ASCII 图**：多线程 / 异步 / 分支合流时画小图帮理解（不要复杂到需要美工审美）
- **顺序**：通常是"概念 → 代码流程 → 场景"。**概念放前面，场景放最后**，中间是带行号的代码分步讲解

## 禁止清单

1. 凭记忆写行号
2. 开场用类比（"想象一下 / 就像…一样 / 把它当作…"）
3. 堆术语不解释（DDD / 依赖注入 / 适配器模式 / Pydantic 校验 直接甩）
4. 顺着代码一行行翻译成中文
5. 讲完不给真实场景
6. 在用户明确说"深入讲"时给摘要式回答
7. 回避复杂性：如果代码确实复杂，分层讲 + 加图，不要简化掉关键机制

## 反馈校正

运行中收到以下反馈时立即调整并重写：

| 用户反馈 | 立即调整 |
|---|---|
| "太硬核了"、"没看懂" | 切换到"概念先行"模式，先讲这段代码**业务上**在干嘛，再讲实现 |
| "你只是在翻译代码" | 回到每个变量/概念问"它代表什么业务概念/为什么需要它" |
| "带上行号"、"我要点击跳转" | 检查每条论断是否都有 markdown 可点击行号 |
| "举个例子"、"具体说说" | 给带具体数值和步骤的真实场景 |
| "不要用餐厅/快递的例子" | 切到正常讲解，需要比方时放中段、且贴近代码本身的场景 |

## 什么时候跳出这个 skill

- 用户明确说"不用讲解风格"、"简短一点就行" → 给简短回答，但**行号还是要带**
- 用户问的是概念题而不是具体代码（如"什么是 RAG？"）→ 可以不带行号，但仍保持"先讲是什么/为什么"的顺序
- 用户在写代码（不是读代码）→ 这个 skill 不适用

## 最终检查（回复前自查）

发送长回复前花 5 秒扫一遍：

- [ ] 所有代码引用都带了可点击行号？
- [ ] 开头是"这段代码在干嘛"，不是"想象一下…"？
- [ ] 关键概念讲了"是什么/为什么"，不是在翻译代码？
- [ ] 末尾有具体场景？（如果是简单问题可以跳过）
- [ ] 术语首次出现都有人话补注？
