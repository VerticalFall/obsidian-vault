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
4. **FollowBuilders** — 从 [follow-builders](https://github.com/zarazhangrui/follow-builders) 公共 feed 拉取 26 位 AI builder 推文、官方博客和播客转录，播客自动用 DeepSeek 生成中文摘要，渲染成 `FollowBuilders/YYYY-MM-DD.md`
5. **日报路由** — 用 DeepSeek V4 Pro 自动跑 daily-router 三层漏斗：读四源报告 → 筛选选题 → 输出路由日志（`_路由/`）+ 更新选题池（`_选题池.md`）。成本 ~$0.018/天
6. **L1 系统健康检查** — 纯标准库零 LLM 零成本，检查四源产出 / 推文计数 / 路由日志 / 选题池存量 / 翻译成功率，输出 `_系统健康/` 日报 + 滚动告警摘要
7. 用内置 `GITHUB_TOKEN` 提交回本仓库

本地只需每天 `git pull` 即可拿到最新报告。

## 目录结构

```
每日报告/
├── .github/
│   ├── workflows/sync-reports.yml    # 定时同步 Action（6 步管道）
│   └── scripts/                      # 纯 Python 标准库（+ translate 库）
│       ├── render_aihot.py           # AI HOT 日报渲染
│       ├── render_xtweets.py         # X 博主动态拉取 + 翻译
│       ├── render_trendradar.py      # TrendRadar 热点渲染
│       ├── render_followbuilders.py  # FollowBuilders AI builder 动态渲染
│       ├── run_daily_router.py       # daily-router 自动路由（DeepSeek V4 Pro）
│       └── check_health.py           # L1 系统健康检查（零 LLM，零成本）
├── AI-HOT/YYYY-MM-DD.md              # AI 日报
├── X-Tweets/
│   ├── following.json                # 追踪博主列表（增删改即可）
│   └── YYYY-MM-DD.md                 # 博主动态日报（含中英对照 + 翻译）
├── TrendRadar/YYYY-MM-DD.md          # 全网热点榜
├── FollowBuilders/YYYY-MM-DD.md      # AI builder 动态（推文+博客+播客摘要）
├── _路由/YYYY-MM-DD.md               # 每日路由日志（选题 + 26 本书框架 + 传播分）
├── _选题池.md                        # 选题看板（🔥新进 / 🌿发酵 / 💤等待）
└── _系统健康/
    ├── YYYY-MM-DD.md                 # 每日健康报告（5 项检查）
    ├── _告警摘要.md                  # 滚动告警摘要（仅 🔴 / 🟡）
    └── _待追加_待验证问题.md         # 待人工验证的问题清单
```

## 上游信息源

| 信息源 | 类型 | 更新频率 | 稳定性 |
|--------|------|---------|:---:|
| AI HOT | AI 日报（24 条/天） | 北京时间 08:00 | 🟢 稳定（公开 API） |
| X Tweets | 指定博主推文 | 实时 → 12:20 汇聚 | 🟡 依赖 SocialData.tools + DeepSeek |
| TrendRadar | 全网热点（36-50 条/天） | 北京时间 08:00 | 🟡 依赖上游爬虫持续运行 |
| FollowBuilders | AI builder 动态（~38 推文 + 博客 + 播客） | 每天更新 | 🟢 公开 GitHub raw JSON |

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

## 自动路由与健康监控

每日 Action 在采集完四源后，额外跑两步「大脑」处理，产物同样回写本仓库：

- **`_路由/YYYY-MM-DD.md`** — DeepSeek V4 Pro 读当日四源报告，用 26 本书的框架做三层漏斗筛选，输出高优先级选题（含锚点 / 框架 / 传播分 / merge 建议）+ 普通选题表 + 对既有选题的更新。
- **`_选题池.md`** — 路由结果沉淀成的看板，分 🔥 新进 / 🌿 持续发酵 / 💤 等待更多信号三区，是本地写作的入口。
- **`_系统健康/`** — L1 健康检查（`check_health.py`，纯标准库、零成本）每天体检 5 项：四源产出、X 推文计数、路由日志、选题池存量、翻译成功率。异常写入 `_告警摘要.md`（仅记 🔴/🟡），需人工核实的写入 `_待追加_待验证问题.md`。

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
- **日报路由源**依赖 `DEEPSEEK_API_KEY`（约 $0.018/天）。Key 失效或余额不足时该 step 静默跳过，`_路由/` 与 `_选题池.md` 当日不更新，L1 健康检查会在 `_告警摘要.md` 里报 🔴。
- 想调整：改 `sync-reports.yml` 里的 `cron`（调度），或各渲染脚本里的参数。
- 本地 `.scripts/` 下有测试脚本：`test-xtweets.ps1`、`pull-reports.ps1`。

---

> 📌 最后更新：2026-07-13 — 新增自动日报路由（DeepSeek V4 Pro）+ 选题池看板 + L1 系统健康监控
