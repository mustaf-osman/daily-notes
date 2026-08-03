1|# 📅 2026年07月22日 加更 — GitHub Trending 三件套深度解析 + 安装记录
2|
3|## 🔥 今天 GitHub 上最火的三个 AI Agent 项目
4|
5|今天 GitHub Trending 被 AI Agent 工具链霸榜了。挑了最值得关注的三个，一个个拆开看。
6|
7|---
8|
9|## 1. 📖 `bojieli/ai-agent-book` — 《深入理解 AI Agent》
10|
11|> ⭐ 16.5k | 今日 +4,624 | 李博杰 著
12|
13|**这是什么？** 第一本系统性地把 AI Agent 从原理讲到工程实战的开源书。10 章 + 88 个配套实验。
14|
15|**核心公式：Agent = LLM + 上下文 + 工具**
16|
17|一句话解释：别把大模型当聊天机器人，把它当成一个**能调用工具的智能员工**。它的能力 = 模型本身 + 你给它的背景信息 + 它能用的外部工具。
18|
19|### 10 章内容速览
20|
21|| 章 | 标题 | 大白话 |
22||:--:|------|--------|
23|| 1 | Agent 基础知识 | "别把模型当聊天机器人，把它当员工" |
24|| 2 | 上下文工程 | 你怎么跟 AI 说话、塞什么资料，决定它的上限 |
25|| 3 | 记忆和知识库 | AI 怎么记住你是谁，RAG、知识图谱怎么做 |
26|| 4 | 工具（Tool） | **MCP 协议详解**——AI 的手，能调 API、读文件、发邮件 |
27|| 5 | Coding Agent | AI 怎么写代码、做 Code Review |
28|| 6 | 评估 | 怎么科学判断一个 Agent 好不好用 |
29|| 7 | 模型后训练 | SFT vs RL——什么时候精调，什么时候强化学习 |
30|| 8 | Agent 自我进化 | 不改模型权重也能越用越聪明 |
31|| 9 | 多模态与实时 | 语音、屏幕操控、机器人 |
32|| 10 | 多 Agent 协作 | 一群 AI 分工合作 |
33|
34|**为什么值得关注？** 全网关于 AI Agent 的博客都是碎片，这本书是**第一个从原理到代码全开源的体系化作品**。已经被翻译成英文、越南语、泰米尔语、繁体中文。
35|
36|> 📥 免费下载：[PDF](https://github.com/bojieli/ai-agent-book/releases)
37|
38|---
39|
40|## 2. 🔍 `tirth8205/code-review-graph` — AI 看代码的"索引引擎"
41|
42|> ⭐ 24.9k | 今日 +1,925 | v2.3.7 | pip install 即用
43|
44|**解决什么痛点？** AI 编程工具最大的浪费——每次 review 代码，AI 会把整个项目文件全读一遍，哪怕改动只涉及 3 个文件。
45|
46|### 工作原理
47|
48|```
49|你的代码 → Tree-sitter 解析 AST → SQLite 图数据库
50|                                      ↓
51|                        （函数调用关系、类继承、测试覆盖）
52|                                      ↓
53|               你改了一个文件 → 自动追踪"爆炸半径"
54|                                      ↓
55|              AI 只看 15 个相关文件，而不是 2000 个
56|```
57|
58|### 效果
59|
60|- **Token 消耗降低 38 ～ 528 倍**
61|- 500 文件项目首次构建 ~10 秒
62|- 2900 文件项目增量更新 < 2 秒
63|- 支持 40+ 语言
64|- 兼容 14 个 AI 编程工具：Claude Code / Codex / Cursor / Copilot / Gemini CLI / Windsurf / Zed...
65|
66|### 核心概念：爆炸半径（Blast Radius）
67|
68|改了一个函数 → 图追踪所有调用方、依赖方、测试 → 只把受影响的文件喂给 AI。
69|
70|这就是 AI 编程时代的**代码智能中间件**——在「代码」和「AI」之间加了一个索引层。
71|
72|### ✅ 安装记录
73|
74|```bash
75|uv pip install code-review-graph  # v2.3.7 安装成功
76|```
77|
78|---
79|
80|## 3. 😂 `ayghri/i-have-adhd` — 强制 AI 闭嘴说重点
81|
82|> ⭐ 7.4k | 今日 +1,866 | Claude Code / Codex / Cursor 插件
83|
84|**这是什么？** 一个 Skill 文件，只有 10 条规则，装到你的 AI 编程助手后——它就再也不敢啰嗦了。
85|
86|### Before vs After
87|
88|| Before | After |
89||--------|-------|
90|| "Great question! Let me think about this. Your auth flow has a few moving pieces: the middleware, the token verification, and the cookie handling. Looking at `src/auth.ts`, the `verifyToken` function seems to be using an older `jsonwebtoken` API. One approach would be to update the package and rewrite that function. After making the change, you'd want to run the auth tests to confirm nothing breaks. By the way, you might also want to look at your dependency versions overall. Hope this helps! Let me know if you want to dig deeper." | 1. 运行 `npm install jsonwebtoken@latest`<br>2. 编辑 `src/auth.ts:42`<br>3. 替换 `verifyToken` (第42-58行)<br>4. 运行 `npm test -- auth.spec.ts`<br><br>Next: 把第一个失败的报错贴过来 |
91|
92|### 10 条铁律
93|
94|1. **第一句就是行动指令**——不要开场白
95|2. **多步骤编号**——人脑喜欢 list
96|3. **结尾给一个"下一步"**——让人知道接下来干嘛
97|4. **禁止跑题**——只说跟当前任务相关的
98|5. **每轮重述当前状态**——不用翻聊天记录
99|6. **给具体时间**——"3 分钟"不是"稍等"
100|7. **让进展可见**——每完成一步都说
101|8. **报错就事论事**——别说"sorry"
102|9. **列表最多 5 条**——长 list = 没 list
103|10. **禁止"Hope this helps!"、"Let me know if..."**——这些全是废话
104|
105|### ✅ 安装记录
106|
107|| 平台 | 状态 |
108||------|------|
109|| Claude Code | ✅ `claude plugin install i-have-adhd@i-have-adhd` |
110|| Codex | ✅ `codex plugin add i-have-adhd@i-have-adhd` |
111|| Cursor | ✅ 可用（Skill 文件在 `.cursor/skills/`） |
112|
113|> 💡 Claude Code 使用方法：输入 `/i-have-adhd` 激活
114|> 💡 Codex 使用方法：输入 `$i-have-adhd` 激活
115|
116|---
117|
118|## 🧠 三个项目串起来看
119|
120|```
121|ai-agent-book        → 理论：Agent 怎么造
122|code-review-graph    → 基础设施：让 AI 干活省 Token
123|i-have-adhd          → 交互体验：让 AI 学会说人话
124|```
125|
126|这三个项目同时上 Trending 不是偶然。它说明一件事：
127|
128|> **开发者社区正在从"玩 AI"过渡到"用 AI 正经干活"。**
129|> 
130|> 不是比谁的模型更强，而是比谁的 Agent 工具链更好用。
131|
132|---
133|
134|## 📌 今天学到的
135|
136|- `code-review-graph build` 可以在任何项目里跑，构建代码关系图
137|- `/i-have-adhd` 以后问 Claude Code 问题它会直接给答案，不回废话
138|- 《深入理解 AI Agent》第 4 章（工具/MCP）和第 10 章（多 Agent）跟 Hermes 直接相关
139|
140|---
141|
142|*— mustaf-osman · 每天更新*
143|