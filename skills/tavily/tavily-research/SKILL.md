---
name: tavily-research
description: 多来源深度研究与网页抽取，适合趋势分析、对比总结和深入阅读特定页面内容。
allowed-tools:
  - tavily_research_tool
  - tavily_extract_tool
---

# 深度研究 (Tavily Research)

## 可用工具

### `tavily_research_tool` — 多来源深度研究
- `query`（必填）：用自然语言描述研究主题
- `max_results`（默认 5）
- `include_domains` / `exclude_domains`：可选域名过滤
- 返回综合多来源的研究总结 + 来源列表

### `tavily_extract_tool` — 网页内容抽取
- `urls`（必填）：多个 URL 用逗号分隔
- 返回每个 URL 的正文内容（自动截断）

## 使用规范

- 需要综合、对比、趋势分析时用 `tavily_research_tool`
- 拿到优质链接后用 `tavily_extract_tool` 深入阅读
- 工具返回 `TAVILY_RESEARCH_UNAVAILABLE` 或 `TAVILY_EXTRACT_UNAVAILABLE` 时必须明确告知用户
- 重要结论引用多个来源相互印证
