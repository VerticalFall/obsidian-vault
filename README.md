# 每日报告（自动同步）

这个文件夹是一个独立的 Git 仓库，与 GitHub 上的 [`VerticalFall/obsidian-vault`](https://github.com/VerticalFall/obsidian-vault) 关联，用来每天自动汇聚多个信息源的报告到本地 Obsidian。

## 工作方式

```
公开信息源 ──[GitHub Action 每日渲染 md]──► obsidian-vault 仓库 ──[本地 git pull]──► 这个文件夹
```

GitHub 上的定时 Action（`.github/workflows/sync-reports.yml`，北京时间每天 12:20 运行）会：

1. **AI HOT** — 调用公开 API `aihot.virxact.com/api/public/daily`，渲染成 `AI-HOT/YYYY-MM-DD.md`
2. **X 博主动态** — 通过 SocialData.tools API（$0.0002/条）拉取指定博主的当日推文，自动翻译英文内容为中文，渲染成 `X-Tweets/YYYY-MM-DD.md`
3. **TrendRadar** — 下载当天成品报告，解析成「AI 热点分析 + 热榜 + RSS」的 `TrendRadar/YYYY-MM-DD.md`
4. **日报路由（NEW）** — 用 DeepSeek V4 Pro 自动跑 daily-router 三层漏斗：读三源报告 → 筛选选题 → 输出路由日志 + 更新选题池。成本 ~$0.018/天
5. 用内置 `GITHUB_TOKEN` 提交回本仓库

本地只需每天 `git pull` 即可拿到最新报告。

## 目录结构

```
每日报告/
├── .github/
│   ├── workflows/sync-reports.yml    # 定时同步 Action
│   └── scripts/                      # 渲染脚本（纯 Python 标准库 + translate 库）
│       ├── render_aihot.py           # AI HOT 日报渲染
│       ├── render_xtweets.py         # X 博主动态拉取 + 翻译
│       └── render_trendradar.py      # TrendRadar 热点渲染
├── AI-HOT/YYYY-MM-DD.md              # AI 日报
├── X-Tweets/
│   ├── following.json                # 追踪博主列表（增删改即可）
│   └── YYYY-MM-DD.md                 # 博主动态日报（含中英对照 + 翻译）
└── TrendRadar/YYYY-MM-DD.md          # 全网热点榜
```

## 上游信息源

| 信息源 | 类型 | 更新频率 | 稳定性 |
|--------|------|---------|:---:|
| AI HOT | AI 日报（24 条/天） | 北京时间 08:00 | 🟢 稳定（公开 API） |
| X Tweets | 指定博主推文 | 实时 → 12:20 汇聚 | 🟡 依赖 SocialData.tools + translate 库 |
| TrendRadar | 全网热点（36-50 条/天） | 北京时间 08:00 | 🟡 依赖上游爬虫持续运行 |

## 添加 / 修改追踪的 X 博主

编辑 `X-Tweets/following.json`，添加或删除 screen_name：

```json
{
  "users": [
    "aleabitoreddit",
    "sunyuchentron",
    "Morris_LT"
  ]
}
```

commit → push → 次日 12:20 生效。不需要改代码。

## 本地管道：从采集到写作

本仓库是上游采集层。在本地 Obsidian Vault 中，这些报告会进入完整的内容生产线：

```
AI HOT + X Tweets + TrendRadar（采集层，本仓库）
        │
        ▼
  daily-router [DeepSeek V4 Pro 自动] ──[三层漏斗]──► 选题池 + 路由日志
        │
        ▼
  weekly-distill ──[信号群合并 + 冷却判断 + 沉淀框架]──► 周度蒸馏报告（本地手动）
        │
        ▼
  公众号写作 ──[两步调研 + 去 AI 味 + 四层自检]（本地手动）
        │
  配图理念 ──[GPT Image 封面 + 原文截图正文]
        │
        ▼
  输出库 / 公众号（已发归档）
```

详细架构见本地 Vault 中的 [[思维链条]]。

## 注意事项

- ⚠️ **不要手动编辑 Action 生成的报告**，否则下次 `git pull` 可能冲突。
- 本文件夹与 vault 里的个人笔记（英硕课程、投资理念等）**完全隔离**，那些内容不在 git 管辖内，不会被上传。
- **TrendRadar 源**依赖上游仓库每天产出 `.db`；若上游停跑（试用到期 / GitHub 60 天不活动自动停用定时任务），`TrendRadar/` 就不会更新——Action 会优雅跳过，不报错。**AI HOT 走 API，稳定不受此影响。**
- **X Tweets 源**依赖 SocialData.tools API（付费，$0.0002/条，约 $0.30/月）和 `translate` Python 库。若 API Key 失效或余额不足，该 step 会静默跳过（`continue-on-error: true`）。
- 想调整：改 `sync-reports.yml` 里的 `cron`（调度），或各渲染脚本里的参数。
- 本地 `.scripts/` 下有测试脚本：`test-xtweets.ps1`、`pull-reports.ps1`。

---

> 📌 最后更新：2026-07-08 — 新增 X-Tweets 采集管道 + 翻译功能
