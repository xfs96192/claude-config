---
name: skills-index-update
description: 更新或重新生成 Skills 分类索引文档。当用户说"更新skills介绍"、"更新skill索引"、"刷新skills文档"、"生成skills分类"、"更新我的skills文档"等指令时立即触发。会读取当前会话中所有可见的 skills，按既定分类体系重写到 Obsidian 知识库。
---

# Skills 分类索引自动更新

## 触发指令

- "更新skills介绍"
- "更新skill索引" / "刷新skills文档"
- "生成skills分类" / "重新生成skills文档"
- "更新我的skills" / "我的skills变了"

## 输出文件

**唯一目标文件**（绝对路径，必须双引号）：

```
/Users/fanshengxia/Library/Mobile Documents/iCloud~md~obsidian/Documents/工作/工作/AI/Skills分类索引.md
```

## 执行步骤

### Step 1：读取当前 skills 列表

**数据源（按优先级）：**

1. **首选**：当前会话 system prompt 中的 `<system-reminder>` 块里 "The following skills are available for use with the Skill tool" 列表。该列表是权威的当下可见 skills。
2. **备选**：扫描 `~/.claude/skills/` 子目录，每个子目录读取 `SKILL.md` 的 frontmatter（`name` + `description`）。

**注意：** 系统列表会随会话上下文变化（用户可能新装/删除 skills），必须以本次会话的列表为准，不要凭记忆。

### Step 2：读取现有索引文档

```bash
读取目标文件，识别现有分类结构（10 大类）
```

如果文件不存在，按 Step 3 的分类骨架新建。

### Step 3：分类映射（保持稳定）

按以下 10 大类组织 skills，**类目名称固定不变**，新 skills 按规则归入相应类别：

| 编号 | 类目 | 归入规则 |
|---|---|---|
| 一 | 投资经理日常工作流 | 头寸/交易/周报/月报/季报/持仓归因（兴银理财业务相关） |
| 二 | 市场复盘与观点 | 市场复盘、市场情绪、流动性监控、个股分析 |
| 三 | 数据查询与资讯 | 金融数据接口（mx_/ichoice/rqdata/alphapai）、资讯/研报搜索 |
| 四 | 阅读/写作/思考 | ljg-* 全系列、视角人物、内容创作发布（baoyu/post-to-xhs/twitter-daily-digest） |
| 五 | 文档处理 | docx/pdf/pptx/obsidian-*/json-canvas/defuddle/contract-review |
| 六 | 开发工具与 QA | browse/qa/ship/review/plan-*/design-*/superpowers/autoresearch |
| 七 | 金融专业模板 | financial-analysis/investment-banking/equity-research/private-equity/wealth-management |
| 八 | AI 工程 | claude-api/mcp-builder/skill-creator/darwin-skill/self-improving-agent |
| 九 | 跨渠道与外部能力 | last30days/agent-reach/opentwitter-mcp/opennews-mcp |
| 十 | 系统配置与会话工具 | update-config/loop/schedule/freeze/checkpoint/learn/init/codex 等 |

**特殊归类规则：**
- `ljg-*` 全部进类目四
- `baoyu-*` 全部进类目四（内容创作子表）
- `superpowers:*` 进类目六（工作流自动化子表）
- `autoresearch:*` 进类目六（工作流自动化子表）
- 带前缀冒号的 namespace skill（如 `financial-analysis:lbo`）按命名空间归类
- 无法归入既有类目的新 skill：归入"十、系统配置与会话工具"末尾，并在文档末尾"附录·新增未分类"提示一行待人工归类

### Step 4：每条 skill 的描述写法

保持简洁中文（10-25字），从 skill 的 description 字段提炼核心用途，**不照搬英文原文**。命名一律保留原始 skill 名（不要翻译）。

示例：
```
| `position-management` | "生成交易日志"/"安排头寸" | 生成次日交易日志、回购计划、产品申赎安排 |
```

带触发指令的（投资经理高频类目一、二），用三列表（skill / 触发指令 / 用途）；
其余类目用两列表（skill / 用途）即可。

### Step 5：保留文档骨架与附录

**必须保留的固定段落：**

- 文档头 frontmatter（更新 `date` 字段为当前日期）
- 顶部说明：用法、范围、排序逻辑
- 文末"附录：常用指令映射"（来自 CLAUDE.md，固定 7 条）
- 文末时间戳：`*生成时间：YYYY-MM-DD*`

### Step 6：写前备份

写入前判断：
- 若目标文件存在，且文件修改时间 > frontmatter 里 `date` 字段对应日期，说明可能有人工编辑：
  ```bash
  cp "目标文件" "目标文件_backup_YYYYMMDD.md"
  ```
- 然后用 Write 工具覆写。

### Step 7：写后汇报

向用户报告：
- 写入路径
- 本次新增 / 移除的 skills 数量
- 新增 skills 的归类位置（让用户复核）
- 是否有未分类项需要人工处理

## 文档模板（骨架不变）

```markdown
---
title: Claude Code Skills 分类索引
date: YYYY-MM-DD
owner: 夏凡盛
purpose: 按使用场景分类的全部可用 Skills 速查表
---

# Skills 分类索引

> 用法：调用方式为 `/<skill-name>`，或直接对 Claude 说映射到 skill 的自然语言指令。
> 范围：本文档仅覆盖当前会话可见的 skills，按"投资经理日常工作 → 研究 → 创作 → 工程 → 系统"由近到远排序。

---

## 一、投资经理日常工作流（最高频）
[三个子类：头寸交易 / 报告生成 / 持仓归因]

## 二、市场复盘与观点
[两个子类：市场复盘 / 情绪流动性监控]

## 三、数据查询与资讯
[两个子类：金融数据接口 / 资讯研报]

## 四、阅读 / 写作 / 思考（ljg 系列 + 写作）
[三个子类：ljg 思考体系 / 视角人物 / 内容创作]

## 五、文档处理

## 六、开发工具与 QA
[四个子类：浏览测试 / 评审发布 / 调试计划 / 工作流自动化]

## 七、金融专业模板（机构级）
[五个子类：财务建模 / IB / ER / PE / WM]

## 八、AI 工程

## 九、跨渠道与外部能力

## 十、系统配置与会话工具
[两个子类：配置 / 会话状态]

---

## 附录：常用指令映射（来自 CLAUDE.md）
[固定 7 条映射]

---

*生成时间：YYYY-MM-DD*
*生成来源：当前会话可见 skills 列表*
```

## 边界与禁忌

- **不要**调用任何外部 API 或运行 Python 脚本，纯文档生成任务
- **不要**主动添加非 skills 内容（如教程、最佳实践）
- **不要**翻译 skill 名（保留英文原名）
- **不要**移除附录中的指令映射表
- 当 skills 列表与上次相比变化超过 30 条时，先告诉用户变化摘要再写入
