---
name: tavily-search
description: 快速联网搜索，用于获取实时招聘信息、市场动态、薪资数据和面试经验。多个查询优先使用批量搜索。
allowed-tools:
  - tavily_search_tool
  - batch_tavily_search_tool
---

# 联网搜索 (Tavily Search)

## 可用工具

### `tavily_search_tool` — 快速单一搜索
- `query`（必填）：搜索关键词
- `max_results`（默认 5）：返回结果数
- `topic`：general 或 news
- `time_range`：空=不限，day/week/month
- `include_domains` / `exclude_domains`：可选域名过滤

### `batch_tavily_search_tool` — 批量并发搜索（优先使用）
- `queries`（必填）：多个关键词用 `|||` 分隔，例：`"数据分析师 薪资|||数据分析师 技能要求"`
- `max_results_per_query`（默认 3）
- `time_range`：同上

## 使用规范

- 多个查询优先用 `batch_tavily_search_tool`，一次提交效率最高
- 回答时标注信息来自哪个 URL
- 工具返回 `TAVILY_SEARCH_UNAVAILABLE` 时必须明确告知用户，不能假装成功
- 除非用户明确说不要上网搜，否则优先联网查真实信息
