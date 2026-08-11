#!/usr/bin/env python3
"""周一管家 — 周度蒸馏 Phase 1-2 (Auto-draft)

每周一 12:20 GitHub Action 自动运行：
  1. 检测是否为周一（非周一 → 跳过）
  2. 读取过去 7 天路由日志 + 选题池 + 观点文件
  3. 调用 DeepSeek 做信号聚类 + 冷却判断
  4. 产出蒸馏草稿 (_蒸馏/YYYY-WXX-draft.md)
  5. 更新选题池（归档上周 🔥 区条目、追加 📦 归档索引）

环境变量:
  DEEPSEEK_API_KEY   — API Key（必需）
  ROUTER_MODEL        — 模型（默认 deepseek-v4-flash）
  TODAY_OVERRIDE      — 指定日期 YYYY-MM-DD（默认北京时间今天）
  DRY_RUN             — 若设为 "1" 则只写草稿不修改选题池
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

BEIJING = timezone(timedelta(hours=8))
MODEL = os.environ.get("ROUTER_MODEL", "deepseek-v4-flash")
API_BASE = "https://api.deepseek.com/v1/chat/completions"
ROUTE_DIR = os.environ.get("ROUTE_OUT_DIR", "_路由")
TOPIC_FILE = os.environ.get("TOPIC_FILE", "_选题池.md")
VIEWPOINT_FILE = os.environ.get("VIEWPOINT_FILE", "_观点.md")
DISTILL_DIR = "_蒸馏"
DRY_RUN = os.environ.get("DRY_RUN", "") == "1"

# ── DeepSeek System Prompt（从 weekly-distill SKILL.md 精简）────────────────

DISTILL_SYSTEM_PROMPT = """你是「AI×金融」内容系统的周度蒸馏分析师。你的任务是对过去 7 天的日报路由日志做三件事：

## 任务一：信号聚类（Phase 1）

遍历 7 天路由日志中所有 ⭐ 高优先级选题和普通选题，按以下维度聚类为信号群：

| 聚类维度 | 示例 |
|---------|------|
| 同一叙事线 | 「AI 投资回报遭质疑」：多个选题从不同侧面讨论同一件事 |
| 同一因果链 | 「中国制造出海 → 遭遇贸易壁垒」：前后相连的因果事件 |
| 同一切面 | 「资源焦虑的三种表现」：不同领域但同一种结构性力量 |
| 反向对冲 | 同一件事的多空双方同时在发酵 → 标注「分裂叙事」 |

每个信号群标注成熟度：
- 🍂 **消退中**：最后一条信号距今 >5 天，且无新信号
- 🌱 **早期**：2-3 条信号，时间跨度 <3 天
- 🌿 **发酵中**：3-5 条信号，持续有新信号加入
- 🌳 **可写**：5+ 条信号，来自多个独立信源，有正反论证

## 任务二：冷却判断（Phase 2）

### 2.1 回顾 7 天前的高优选题
如果路由日志里有 ⭐ 选题但未被写作：
- 🔥 **还在燃烧**：本周有 ≥2 条新信号强化 → 建议保留或升级
- 💤 **等待**：本周有 0-1 条新信号 → 建议降级
- 🧊 **已冷却**：本周 0 条新信号，且当初判断偏乐观 → 建议移除

### 2.2 选题池健康度
- 🔥 + 🌿 区合计 <5 条 → 标注「选题池库存偏低」

## 任务三：选题池操作建议

对选题池 🔥 区中属于上周（非本周一）的条目，逐条给出操作建议：

- `promote`：有跨天信号累积（≥2 天出现相关信号），建议升入 🌿
- `archive`：无跨天信号，建议归档
- `keep_as_new`：信号仍在活跃期，虽然日期旧但建议保留在 🔥 区

---

## 输出格式

请严格按以下格式输出，用 `===SECTION===` 分隔三个部分：

===SIGNAL_GROUPS===
```markdown
## 一、信号群

### 🌳 可写级

#### 信号群: <名称>
- 信号数: X 条 (跨 Y 天)
- 方向: {趋同 / 分裂 / 升级中}
- 信号链:

| 日期 | 信号 |
|------|------|
- 核心叙事: <一段话>
- 选题建议: {新选题 / 合并进现有选题 / 等更多信号}
- 如果写: <角度建议，约 100 字>

### 🌿 发酵中
(同上格式)

### 🌱 早期信号
(同上格式)

### 🍂 消退中
(同上格式)
```

===COOLDOWN===
```markdown
## 二、冷却判断

### 🔥 仍在燃烧
| 原选题 | 日期 | 本周新信号 | 处理 |

### 💤 等待更多信号
| 原选题 | 日期 | 理由 |

### 🧊 已冷却
| 原选题 | 日期 | 冷却原因 |

### 📝 回溯已写文章
> ⚠️ 审核时手动补充。
```

===TOPIC_OPS===
```
## promote
| 原选题关键词 | 🔥区日期 | 理由 |

## archive
| 原选题关键词 | 🔥区日期 | 理由 |

## keep_as_new
| 原选题关键词 | 🔥区日期 | 理由 |
```

(无对应操作则写「无」)

---

约束：
- 信号群命名用叙事语言，不是分类标签（「AI 投资回报遭市场检验」比「AI 板块」有用）
- 冷却判断要诚实——不要因为「选题当时选得很对」就不舍得归档
- TOPIC_OPS 中「原选题关键词」用选题标题中的 3-6 个关键汉字，确保脚本能精准匹配到选题池中的行
- 如果被蒸馏的 7 天里路由日志 < 2 篇，照常执行但标注「本周数据偏薄」

现在开始对以下路由日志执行蒸馏。"""


# ── helpers ────────────────────────────────────────────────────

def bao_date() -> str:
    ov = os.environ.get("TODAY_OVERRIDE", "").strip()
    return ov if ov else datetime.now(BEIJING).strftime("%Y-%m-%d")


def is_monday(date_str: str = "") -> bool:
    """判断是否为周一。Beijing timezone. Python weekday(): 0=Mon, 6=Sun."""
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").weekday() == 0
        except ValueError:
            return False
    return datetime.now(BEIJING).weekday() == 0


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def is_table_sep(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and "-" in s and set(s) <= set("|-: ")


def is_data_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and not set(s) <= set("|-: ") and "---" not in s


def iso_week(date_str: str) -> str:
    """返回 ISO 周次，如 W30。"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        iso = dt.isocalendar()
        return f"W{iso.week:02d}"
    except ValueError:
        return "W??"


def date_range_for_distill(today_str: str):
    """返回蒸馏覆盖的日期范围：上周一到上周日。"""
    try:
        today = datetime.strptime(today_str, "%Y-%m-%d")
    except ValueError:
        today = datetime.now(BEIJING)
    # 上周一 = 今天 - 7 天（如果今天是周一）
    # 上周日 = 今天 - 1 天
    last_sunday = today - timedelta(days=1)
    last_monday = today - timedelta(days=7)
    return (last_monday.strftime("%Y-%m-%d"),
            last_sunday.strftime("%Y-%m-%d"))


def list_routes_in_range(start_date: str, end_date: str) -> list[str]:
    """列出日期范围内的路由日志路径，按日期升序排列。"""
    import glob as g
    files = sorted(g.glob(f"{ROUTE_DIR}/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
    result = []
    for f in files:
        basename = os.path.basename(f).replace(".md", "")
        if start_date <= basename <= end_date:
            result.append(f)
    return sorted(result)


def call_deepseek(system: str, user: str, max_tokens: int = 12000) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY 环境变量未设置")
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }).encode("utf-8")
    req = urllib.request.Request(
        API_BASE, data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.loads(r.read().decode("utf-8"))
    content = data["choices"][0]["message"]["content"]
    if not content or not content.strip():
        raise RuntimeError("DeepSeek 返回了空内容")
    return content


def parse_sections(output: str) -> dict[str, str]:
    sections = {}
    current = ""
    for line in output.split("\n"):
        m = re.match(r'^===(\w+)===$', line.strip())
        if m:
            current = m.group(1)
            sections[current] = ""
        elif current:
            sections[current] += line + "\n"
    return {k: v.strip() for k, v in sections.items()}


def mmdd(date_str: str) -> str:
    return date_str[-5:] if len(date_str) >= 10 else date_str


def build_distill_context(today_str: str, start: str, end: str) -> str:
    """构建传给 DeepSeek 的蒸馏上下文。"""
    parts = []
    parts.append(f"蒸馏日期: {today_str}")
    parts.append(f"覆盖范围: {start} ~ {end}")
    parts.append("")

    # 路由日志
    route_files = list_routes_in_range(start, end)
    parts.append(f"=== 路由日志: {len(route_files)} 篇 ===")
    parts.append("")
    if not route_files:
        parts.append("(本周无路由日志)")
    for f in route_files:
        content = read_file(f)
        if content:
            # 去除 frontmatter
            lines = content.split("\n")
            body_start = 0
            for i, l in enumerate(lines):
                if l.startswith("# ") and "路由" in l:
                    body_start = i
                    break
            parts.append("\n".join(lines[body_start:]))
            parts.append("\n---\n")

    # 选题池
    topic_pool = read_file(TOPIC_FILE)
    if topic_pool:
        parts.append("=== 当前选题池 ===")
        parts.append(topic_pool)
        parts.append("")

    # 观点文件（仅判断表，供 DeepSeek 参考）
    viewpoints = read_file(VIEWPOINT_FILE)
    if viewpoints:
        m = re.search(r'^## 二、当前核心判断.*?\n(.*?)(?=^## |\Z)',
                      viewpoints, re.M | re.S)
        if m:
            parts.append("=== 我的既有判断 ===")
            parts.append(m.group(0).strip())
            parts.append("")

    return "\n".join(parts)


def clean_markdown_fence(text: str) -> str:
    """去掉 LLM 输出的 markdown 代码围栏。"""
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r'^```\w*\n?', '', t, count=1)
        t = re.sub(r'\n?```\s*$', '', t)
        t = t.strip()
    return t


# ── 选题池操作 ─────────────────────────────────────────────────

def parse_topic_ops(topic_ops_text: str) -> dict[str, list[str]]:
    """解析 TOPIC_OPS section。

    返回: {"promote": [keyword, ...], "archive": [keyword, ...],
            "keep_as_new": [keyword, ...]}
    """
    result = {"promote": [], "archive": [], "keep_as_new": []}
    if not topic_ops_text or topic_ops_text.strip() == "无":
        return result

    current_section = ""
    for line in topic_ops_text.split("\n"):
        s = line.strip()
        m = re.match(r'^##\s+(\w+)', s)
        if m:
            current_section = m.group(1).lower()
            continue
        if current_section in result and s.startswith("|") and is_data_row(s):
            cols = [c.strip() for c in s.split("|")]
            if len(cols) >= 2:
                keyword = cols[1]  # 第一列：原选题关键词
                if keyword:
                    result[current_section].append(keyword)
    return result


def count_pool_stats(text: str) -> dict[str, int]:
    """统计选题池各分区条目数。"""
    hot = 0
    evergreen = 0
    dormant = 0
    in_section = ""
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("## 🔥"):
            in_section = "hot"
        elif s.startswith("## 🌿"):
            in_section = "evergreen"
        elif s.startswith("## 💤"):
            in_section = "dormant"
        elif s.startswith("## ") and "归档" not in s and "已发布" not in s:
            in_section = ""
        if in_section == "hot" and is_data_row(s):
            hot += 1
        elif in_section == "evergreen" and is_data_row(s):
            evergreen += 1
        elif in_section == "dormant" and is_data_row(s):
            dormant += 1
    return {"hot": hot, "evergreen": evergreen, "dormant": dormant}


def archive_topic_pool(topic_ops: dict[str, list[str]],
                       last_sunday: str,
                       today_str: str) -> list[dict]:
    """归档选题池。

    1. 🔥 区：移除上周（≤ last_sunday）的条目
       - 按 TOPIC_OPS 分类：promote → 移入 🌿；archive → 归档；keep_as_new → 保留
       - 未匹配到 TOPIC_OPS 的默认 archive
    2. 💤 区：移除 TOPIC_OPS 中标记为 remove 的条目
    3. 选题池底部 ## 📦 归档 索引追加本周归档条目

    返回归档条目列表，供 distill draft 使用。

    注意：如果 DRY_RUN，只返回归档列表，不写回选题池。
    """
    existing = read_file(TOPIC_FILE)
    if not existing:
        print("WARNING: _选题池.md 不存在，跳过归档")
        return []

    lines = existing.split("\n")
    week_label = iso_week(today_str)

    # ── 操作入口 ──
    # 构建关键词 → 操作 的快速查表
    keyword_op = {}  # keyword -> "promote" | "archive" | "keep_as_new"
    for op_type in ("promote", "archive", "keep_as_new"):
        for kw in topic_ops.get(op_type, []):
            keyword_op[kw] = op_type

    # ── 第 0 步：统计清理前 ──
    before_stats = count_pool_stats(existing)

    # ── 第 1 步：扫描全部行，标记要处理的条目 ──

    archive_entries = []  # [{title, date, op}]
    promote_entries = []  # [{title, date, op}]
    keep_entries = []     # [{title, date, op}]
    remove_from_dormant = []  # [{title}]

    # 扫描 🔥 区
    in_hot = False
    current_date = ""
    lines_to_remove = set()  # 要删除的行索引
    date_subs_to_remove = set()  # 要删除的日期子标题行索引（如果该日期下所有条目都被移除）

    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("## 🔥"):
            in_hot = True
            continue
        elif in_hot and (s.startswith("## ") and not s.startswith("## 🔥")):
            in_hot = False
            continue

        if not in_hot:
            # 同时扫描 💤 区
            if s.startswith("## 💤"):
                in_hot = False  # just to be safe
            continue

        # 跟踪日期子标题
        if s.startswith("### "):
            current_date = re.sub(r'^###\s+(\d{2}-\d{2}).*', r'\1', s)
            continue

        if not is_data_row(s):
            continue

        # 解析数据行
        cols = [c.strip() for c in s.split("|")]
        if len(cols) < 2:
            continue
        title = cols[1]

        # 跳过脏数据：纯占位符行（如 "选题"、空标题等）
        if not title or re.match(r'^[⭐·/ ]*选题$', title):
            continue

        # 判断该条目是否属于上周
        full_date = f"2026-{current_date}" if current_date else ""
        if not full_date or full_date > last_sunday:
            # 本周一或之后的条目，保留
            continue

        # 匹配 TOPIC_OPS
        matched_op = None
        for kw, op in keyword_op.items():
            if kw in title:
                matched_op = op
                break

        if not matched_op:
            matched_op = "archive"  # 默认归档

        entry = {"title": title, "date": full_date, "op": matched_op}
        if matched_op == "promote":
            promote_entries.append(entry)
        elif matched_op == "keep_as_new":
            keep_entries.append(entry)
        else:
            archive_entries.append(entry)

        lines_to_remove.add(i)

    # 扫描 💤 区中的移除项（TOPIC_OPS 指定移除的）
    # — 当前 TOPIC_OPS 暂不单独输出 remove_from_dormant，
    #   但保留代码结构方便后续扩展
    in_dormant = False
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("## 💤"):
            in_dormant = True
            continue
        elif in_dormant and s.startswith("## "):
            in_dormant = False
            continue
        if not in_dormant or not is_data_row(s):
            continue
        cols = [c.strip() for c in s.split("|")]
        if len(cols) < 2:
            continue
        title = cols[1]
        if not title or re.match(r'^[⭐·/ ]*选题$', title):
            continue
        for kw, op in keyword_op.items():
            if kw in title and op == "archive":
                remove_from_dormant.append({"title": title})
                lines_to_remove.add(i)
                break

    # ── 第 2 步：移除标记行 + 清理空日期子标题 ──

    # 反向删除（从后往前，避免索引偏移）
    new_lines = []
    for i, line in enumerate(lines):
        if i in lines_to_remove:
            continue
        new_lines.append(line)

    # 清理空日期子标题（在 🔥 区范围内）
    # 找到 🔥 区位置，检查每个 ### MM-DD 下面是否还有数据行
    cleaned_lines = []
    skip_until_next_section = False
    pending_blank = False  # 上一个空行是否保留

    for i, line in enumerate(new_lines):
        s = line.strip()

        # 跟踪是否在 🔥 区内
        if s.startswith("## 🔥"):
            skip_until_next_section = False
            cleaned_lines.append(line)
            continue
        if s.startswith("## ") and not s.startswith("## 🔥"):
            # 过了 🔥 区，正常保留
            cleaned_lines.append(line)
            continue

        # 在 🔥 区内
        if s.startswith("### "):
            # 检查这个日期子标题下是否还有数据行（向前看）
            has_data = False
            for j in range(i + 1, len(new_lines)):
                ns = new_lines[j].strip()
                if ns.startswith("### ") or ns.startswith("## "):
                    break
                if is_data_row(ns):
                    has_data = True
                    break
            if has_data:
                cleaned_lines.append(line)
                # 更新计数 — 粗略，不做精确替换
            else:
                # 空日期组，跳过 + 跳过后续空行直到下一个 ### 或 ##
                skip_until_next_section = True
            continue

        if skip_until_next_section:
            if s.startswith("### ") or s.startswith("## "):
                skip_until_next_section = False
                cleaned_lines.append(line)
            # else: 跳过空行、表头、分隔行等
            continue

        cleaned_lines.append(line)

    # ── 第 3 步：promote 到 🌿 区 ──
    if promote_entries:
        # 找到 🌿 区最后一个数据行之后，插入 promote 条目
        evergreen_section_idx = -1
        evergreen_data_end = -1
        in_evergreen = False
        for i, line in enumerate(cleaned_lines):
            s = line.strip()
            if s.startswith("## 🌿"):
                in_evergreen = True
                evergreen_section_idx = i
            elif in_evergreen and s.startswith("## ") and not s.startswith("## 🌿"):
                evergreen_data_end = i
                break
            if in_evergreen and is_data_row(s):
                evergreen_data_end = i

        if evergreen_data_end >= 0:
            # 在最后一个数据行之后、下一个 ## 之前插入
            insert_idx = evergreen_data_end + 1
            for entry in promote_entries:
                new_row = f"| {entry['title']} | 🔥区升入 ({entry['date']}) | 见原 🔥 区角度 | 独立 |"
                cleaned_lines.insert(insert_idx, new_row)
                insert_idx += 1
            if promote_entries:
                print(f"OK: 🌿 区升入 {len(promote_entries)} 条")

    # ── 第 4 步：更新或追加 ## 📦 归档 索引 ──
    # 查找已有归档区
    archive_section_idx = -1
    archive_table_start = -1
    for i, line in enumerate(cleaned_lines):
        s = line.strip()
        if s.startswith("## 📦 归档"):
            archive_section_idx = i
        if archive_section_idx >= 0 and is_data_row(s) and i > archive_section_idx:
            archive_table_start = i
            break

    all_archived = archive_entries + [
        {"title": e["title"], "date": e["date"], "op": "移除"}
        for e in remove_from_dormant
    ]

    if all_archived:
        archive_rows = []
        for entry in all_archived:
            archive_rows.append(
                f"| {week_label} | {entry['title']} | {entry['op']} |"
            )

        if archive_section_idx >= 0:
            # 已有归档区 — 追加到表格末尾
            if archive_table_start >= 0:
                # 找到最后的归档数据行
                last_archive_row = archive_table_start
                for j in range(archive_table_start, len(cleaned_lines)):
                    if is_data_row(cleaned_lines[j].strip()):
                        last_archive_row = j
                    elif cleaned_lines[j].strip().startswith("## "):
                        break
                insert_at = last_archive_row + 1
                for row in archive_rows:
                    cleaned_lines.insert(insert_at, row)
                    insert_at += 1
            else:
                # 有标题无表格 → 补表头
                header = "| 周次 | 选题 | 去向 |"
                sep = "|------|------|------|"
                insert_at = archive_section_idx + 1
                cleaned_lines.insert(insert_at, "")
                cleaned_lines.insert(insert_at + 1, header)
                cleaned_lines.insert(insert_at + 2, sep)
                for j, row in enumerate(archive_rows):
                    cleaned_lines.insert(insert_at + 3 + j, row)
        else:
            # 首次创建归档区
            cleaned_lines.append("")
            cleaned_lines.append("## 📦 归档")
            cleaned_lines.append("")
            cleaned_lines.append("| 周次 | 选题 | 去向 |")
            cleaned_lines.append("|------|------|------|")
            for row in archive_rows:
                cleaned_lines.append(row)

    # ── 第 5 步：写回（DRY_RUN 除外）──
    if not DRY_RUN:
        write_file(TOPIC_FILE, "\n".join(cleaned_lines) + "\n")
        after_stats = count_pool_stats("\n".join(cleaned_lines))
        print(f"选题池归档: 🔥 {before_stats['hot']}→{after_stats['hot']}, "
              f"🌿 {before_stats['evergreen']}→{after_stats['evergreen']}, "
              f"💤 {before_stats['dormant']}→{after_stats['dormant']}")
    else:
        print("DRY_RUN: 选题池未修改")
        # 仍输出归档条目到 stderr/tmp 供审查
        tmp_path = "_distill_archive_preview.md"
        write_file(tmp_path, "\n".join(cleaned_lines) + "\n")
        print(f"DRY_RUN: 预览写入 {tmp_path}")

    # 返回归档条目列表（供 distill draft 的「本周选题归档」节使用）
    return archive_entries + promote_entries + [
        {"title": e["title"], "date": "", "op": e["op"]}
        for e in remove_from_dormant
    ]


# ── main ────────────────────────────────────────────────────────

def main():
    today_str = bao_date()
    print(f"=== 周一管家 · 周度蒸馏 · {today_str} ===")

    # 0. 判断周一
    if not is_monday(today_str):
        print(f"今天({today_str})不是周一，跳过周度蒸馏。")
        return 0

    print("✅ 今天为周一，开始周度蒸馏。")

    # 1. 日期范围
    start, end = date_range_for_distill(today_str)
    week_label = iso_week(today_str)
    print(f"覆盖范围: {start} ~ {end} (ISO {week_label})")

    # 2. 读路由日志
    route_files = list_routes_in_range(start, end)
    print(f"路由日志: {len(route_files)} 篇")
    if len(route_files) < 2:
        print("⚠️  路由日志 < 2 篇，本周数据偏薄，照常执行。")

    # 3. 构建上下文 + 调 DeepSeek
    context = build_distill_context(today_str, start, end)
    print(f"上下文约 {len(context)} 字符")

    print("调用 DeepSeek API …")
    raw = call_deepseek(DISTILL_SYSTEM_PROMPT, context, max_tokens=12000)
    print(f"响应 {len(raw)} 字符")

    # 4. 解析
    sections = parse_sections(raw)
    signal_groups = clean_markdown_fence(sections.get("SIGNAL_GROUPS", ""))
    cooldown = clean_markdown_fence(sections.get("COOLDOWN", ""))
    topic_ops_raw = sections.get("TOPIC_OPS", "")

    if not signal_groups and not cooldown:
        print("ERROR: DeepSeek 未返回有效 SECTION，将原始响应用作草稿。")
        signal_groups = raw
        cooldown = ""

    # 5. 解析 TOPIC_OPS
    topic_ops = parse_topic_ops(topic_ops_raw)
    print(f"TOPIC_OPS: promote={len(topic_ops['promote'])}, "
          f"archive={len(topic_ops['archive'])}, "
          f"keep_as_new={len(topic_ops['keep_as_new'])}")

    # 6. 选题池统计（清理前）
    pool_text = read_file(TOPIC_FILE)
    before_stats = count_pool_stats(pool_text) if pool_text else {"hot": 0, "evergreen": 0, "dormant": 0}

    # 7. 选题池归档
    archived = archive_topic_pool(topic_ops, end, today_str)
    print(f"归档条目: {len(archived)} 条")

    # 8. 选题池统计（清理后）
    pool_text_after = read_file(TOPIC_FILE) if not DRY_RUN else pool_text
    after_stats = (count_pool_stats(pool_text_after)
                   if pool_text_after
                   else {"hot": 0, "evergreen": 0, "dormant": 0})

    # 9. 组装蒸馏草稿
    health_assessment = "健康" if (after_stats["hot"] + after_stats["evergreen"]) >= 5 else "偏低"

    # 选题归档表
    archive_table = ""
    if archived:
        archive_table = "\n| 选题 | 原日期 | 处理 | 去向 |\n|------|--------|------|------|\n"
        for e in archived:
            dest = {"promote": "🌿 持续发酵", "archive": "📦 归档",
                    "keep_as_new": "🔥 保留", "移除": "🗑 移除"}.get(e["op"], e["op"])
            archive_table += f"| {e['title']} | {e.get('date', '')} | {e['op']} | {dest} |\n"

    draft = f"""# 周度蒸馏 · {week_label}（草稿 · 待审核）

> ⚠️ 本报告由 GitHub Action 自动生成（Phase 1-2）。
> Phase 3（框架提取）和 Phase 4（观点回顾）需在 Claude 会话中人工审核后定稿。
> 定稿后移动到: `01_内容系统/系统/蒸馏/{week_label}.md`

范围: {start} ~ {end} (7 天)
路由日志: {len(route_files)} 篇
本周写作: （审核时手动补充）

---

{signal_groups if signal_groups else '（本周无新增信号群）'}

---

{cooldown if cooldown else '（无冷却判断）'}

### 📊 选题池健康度
- 清理前: {before_stats['hot']} 条 (🔥{before_stats['hot']} 🌿{before_stats['evergreen']} 💤{before_stats['dormant']})
- 清理后: {after_stats['hot'] + after_stats['evergreen'] + after_stats['dormant']} 条 (🔥{after_stats['hot']} 🌿{after_stats['evergreen']} 💤{after_stats['dormant']})
- 本周归档: {len(archived)} 条
- 评估: {health_assessment}

### 📦 本周归档

> 以下选题从 🔥 区移除，原因见「处理」列。完整记录保留在选题池底部 `## 📦 归档` 索引。

{archive_table if archive_table else '（上周无待归档选题）'}

---

## 三、可复用框架（待审核）

> ⚠️ Phase 3 — 需人工审核后填写。

### 📖 本周高频标尺
（审核时手动总结）

---

## 四、观点回顾（待审核）

> ⚠️ Phase 4 — 需人工审核后填写。

| V# | 本周信号 | AI 建议 | 用户决定 |
|----|---------|--------|---------|

---

## 五、下周关注

（审核时手动填写）

---

> 📌 状态: 草稿 · 自动生成于 {today_str} (GitHub Action · 周一管家)
> 📌 审核后移动到: `01_内容系统/系统/蒸馏/{week_label}.md`
"""

    # 10. 写草稿
    draft_path = os.path.join(DISTILL_DIR, f"{week_label}-draft.md")
    write_file(draft_path, draft)
    print(f"OK: 蒸馏草稿 → {draft_path}")

    # 11. 总结
    print(f"\n=== 周一管家完成 ===")
    print(f"草稿: {draft_path}")
    print(f"选题池: 归档 {len(archived)} 条, "
          f"🔥{before_stats['hot']}→{after_stats['hot']} "
          f"🌿{before_stats['evergreen']}→{after_stats['evergreen']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
