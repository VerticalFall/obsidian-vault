# 每日报告(自动同步)

这个文件夹是一个独立的 Git 仓库,与 GitHub 上的 [`VerticalFall/obsidian-vault`](https://github.com/VerticalFall/obsidian-vault) 关联,用来每天自动汇聚多个信息源的报告到本地 Obsidian。

## 工作方式

```
公开信息源 ──[GitHub Action 每日渲染 md]──► obsidian-vault 仓库 ──[本地 git pull]──► 这个文件夹
```

GitHub 上的定时 Action(`.github/workflows/sync-reports.yml`,北京时间每天 12:20 运行)会:

1. **AI HOT** — 调用公开 API `aihot.virxact.com/api/public/daily`,渲染成 `AI-HOT/YYYY-MM-DD.md`
2. **TrendRadar** — 下载当天 `output/news/YYYY-MM-DD.db`(SQLite),渲染成 `TrendRadar/YYYY-MM-DD.md`
3. 用内置 `GITHUB_TOKEN` 提交回本仓库

本地只需每天 `git pull` 即可拿到最新报告。

## 目录结构

```
每日报告/
├── .github/
│   ├── workflows/sync-reports.yml   # 定时同步 Action
│   └── scripts/                     # 渲染脚本(纯 Python 标准库,零依赖)
│       ├── render_aihot.py
│       └── render_trendradar.py
├── AI-HOT/YYYY-MM-DD.md             # AI 日报
└── TrendRadar/YYYY-MM-DD.md         # 全网热点榜
```

## 注意事项

- ⚠️ **不要手动编辑 Action 生成的报告**,否则下次 `git pull` 可能冲突。
- 本文件夹与 vault 里的个人笔记(英硕课程、投资理念等)**完全隔离**,那些内容不在 git 管辖内,不会被上传。
- **TrendRadar 源**依赖上游仓库每天产出 `.db`;若上游停跑(试用到期 / GitHub 60 天不活动自动停用定时任务),`TrendRadar/` 就不会更新——Action 会优雅跳过,不报错。**AI HOT 走 API,稳定不受此影响。**
- 想调整:改 `sync-reports.yml` 里的 `cron`(调度),或 `render_trendradar.py` 里的 `TR_TOP_PER_PLATFORM`(每平台展示条数)。
