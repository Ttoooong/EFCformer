# 智能热点收集助手（免费版）

该项目实现了一个完全免费、无需付费 API 的热点信息收集助手。它支持 RSS/Atom 订阅与 HTML 列表页抓取，进行关键词匹配、去重、排序，并将结果落地到本地 SQLite 数据库。

## 功能特性
- 关键词检索：支持多关键词分词处理。
- 多来源采集：RSS/Atom 与 HTML 站内搜索/列表页。
- 去重与排序：URL 规范化、相似度去重、时间衰减评分。
- 本地落地：SQLite 存储与后续查询。
- 定时刷新：支持定时任务模式。

## 安装
```bash
pip install -r requirements.txt
```

## 配置
配置文件位于 `config/sources.toml`，示例包含 RSS 与 HTML 来源。请根据实际站点补充并遵守其 `robots.txt` 规则。

## 运行
一次性运行：
```bash
python -m hotspot.cli "电动汽车 补贴"
```

定时运行（每 30 分钟刷新）：
```bash
python -m hotspot.cli "电动汽车 补贴" --interval 30
```

## 说明
- 该项目只使用公开免费来源，不包含任何付费 API。
- 输出包含标题、来源、时间、摘要、链接、关键词及评分。
