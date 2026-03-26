---
name: twitter-daily-digest
description: 生成 Twitter/X 日报，抓取 AI 类和投资类 Top 10 账号的最新推文，保存为 Markdown 到 Obsidian。当用户说"生成Twitter日报"、"抓推文"、"Twitter日报"、"X日报"、"抓取今天的推文"、"更新Twitter内容"时立即触发。每次生成一个当日日期命名的文件，包含 AI 动态和投资动态两个板块，每账号最新 5 条推文。
---

# Twitter 日报 Skill

每天自动从 20 个精选账号（AI 类 10 个 + 投资类 10 个）抓取最新推文，生成结构化 Markdown 日报，保存到 Obsidian。

## 触发词

用户说以下任意一种时触发：
- "生成 Twitter 日报" / "生成X日报" / "抓取推文"
- "Twitter 日报" / "今天的推文" / "更新推文"
- "帮我生成今天的 Twitter 内容"

## 执行方式

直接运行脚本，**不要**手动构造 curl 命令或逐一抓取。脚本已内置并发逻辑和所有配置。

```bash
python3 ~/.claude/skills/twitter-daily-digest/scripts/fetch_tweets.py
```

指定日期（可选）：
```bash
python3 ~/.claude/skills/twitter-daily-digest/scripts/fetch_tweets.py --date 2026-03-26
```

## 输出

- **路径**：`/Users/fanshengxia/Library/Mobile Documents/iCloud~md~obsidian/Documents/工作/工作/AI/Twitter日报_YYYY-MM-DD.md`
- **内容**：AI 动态板块 + 投资动态板块，每账号最新 5 条推文（含时间、链接、❤️ 🔁 💬 数据）

## 执行后

脚本运行完毕后，告知用户：
1. 文件已写入路径
2. AI 类成功抓取几个账号 / 投资类成功几个账号
3. 如有失败账号，列出来

## 账号更新

如用户想更改监控的账号，直接编辑脚本文件：
`~/.claude/skills/twitter-daily-digest/scripts/fetch_tweets.py`
修改 `AI_ACCOUNTS` 或 `INVEST_ACCOUNTS` 列表即可。
