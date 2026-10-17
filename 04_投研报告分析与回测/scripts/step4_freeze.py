# -*- coding: utf-8 -*-
"""Step 4 — 冻结研报全文 + 生成论据拆解骨架（claim）。

用法:
    # 从回测明细里自动挑多样样本（扎堆/下调/上调/独家/头部机构）
    python scripts/step4_freeze.py --detail "数据/03_回测结果/backtest_沪深300_20261017_样本明细.jsonl" --n 5

    # 指定 infoCode 冻结
    python scripts/step4_freeze.py --info AP202506301700516120 AP202503281700123456

产物:
    数据/04_全文档案/{infoCode}.md   原文冻结（含 sha256、抓取时点）
    论据库/claims/{claim_id}.md      待拆解骨架（front matter 已填好机器事实）
"""
import argparse
import glob
import hashlib
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import em  # noqa: E402
import yamlite  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE = os.path.join(ROOT, "数据", "04_全文档案")
CLAIMS = os.path.join(ROOT, "论据库", "claims")
PXD = os.path.join(ROOT, "数据", "02_行情")


def load_jsonl(p):
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def px_on(code, date):
    p = os.path.join(PXD, f"{code}.jsonl")
    if not os.path.exists(p):
        return None
    rows = load_jsonl(p)
    best = None
    for r in rows:
        if r["d"] <= date:
            best = r["c"]
        else:
            break
    return best


def pick_samples(detail_path, n, max_publish="9999-12-31"):
    """按情境维度抽样本，尽量避免全落在同一类。max_publish 用于保证已到期。"""
    rows = [r for r in load_jsonl(detail_path)
            if "6个月" in r and r.get("date", "9999") <= max_publish]
    picks, used = [], set()

    def take(pred, tag):
        for r in rows:
            if r["infoCode"] in used:
                continue
            if pred(r):
                picks.append((tag, r))
                used.add(r["infoCode"])
                return True
        return False

    take(lambda r: r.get("cluster", 0) >= 10, "扎堆覆盖(≥10篇/30天)")
    take(lambda r: r.get("rc") == "1", "评级下调")
    take(lambda r: r.get("rc") == "0", "评级上调")
    take(lambda r: r.get("cluster", 9) == 1 and r["6个月"][0] > 0, "独家覆盖且跑赢")
    take(lambda r: r["org"] in ("中金公司", "中信证券", "国泰君安", "华泰证券", "招商证券"), "头部机构")
    for r in rows:
        if len(picks) >= n:
            break
        if r["infoCode"] not in used:
            picks.append(("补充", r))
            used.add(r["infoCode"])
    return picks[:max(n, len(picks))]


def build_claim(info_code, meta, body, frozen_at):
    code = str(meta.get("stockCode") or "").strip()
    date = (meta.get("publishDate") or "")[:10]
    org = meta.get("orgSName") or ""
    px = px_on(code, date) if code else None
    rating = meta.get("emRatingName") or ""
    rc = str(meta.get("ratingChange"))
    rc_name = {"0": "上调", "1": "下调", "2": "首次覆盖", "3": "维持"}.get(rc, "未知")
    tp = meta.get("indvAimPriceT") or None

    def fnum(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    fm = {
        "claim_id": f"{date}_{code}_{org}_{info_code[-6:]}",
        "info_code": info_code,
        "frozen_at": frozen_at,
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "org": org,
        "analyst": meta.get("researcher") or "",
        "stock": meta.get("stockName") or "",
        "code": code,
        "industry": meta.get("indvInduName") or "",
        "publish_date": date,
        "rating": rating,
        "rating_change": rc_name,
        "target_price": fnum(tp),
        "eps_this_year": fnum(meta.get("predictThisYearEps")),
        "eps_next_year": fnum(meta.get("predictNextYearEps")),
        "px_at_publish": px,
        "direction": "看多" if rating in ("买入", "增持") else ("看空" if rating in ("卖出", "减持") else "中性"),
        "horizon_months": 12,
        "title": meta.get("title") or "",
        "status": "待拆解",
    }

    tpl = f"""# {fm['stock']}（{code}）· {org} · {date}

> 原标题：{fm['title']}
> 原文冻结：`数据/04_全文档案/{info_code}.md`　sha256 前12位 `{fm['body_sha256'][:12]}`
> 发布时股价：{px if px is not None else '（缺）'}　评级：{rating}（{rc_name}）　目标价：{tp if tp else '未披露'}
> **拆解只能使用 {date} 当天及之前已知的信息。** 违反这条，整个回测就废了。

## 一、一句话论点

（待填：这家机构认为这家公司在未来 {fm['horizon_months']} 个月会发生什么，凭什么）

## 二、论据池

| # | 论据（因为 X，所以 Y） | 类型 | 可证伪 | 证伪判据（到期时用哪个数字判死） | 数据源 |
|---|---|---|---|---|---|
| A1 |  |  |  |  |  |

> 类型可选：需求 / 价格 / 产能 / 份额 / 政策 / 成本 / 新品 / 并购 / 财务质量 / 估值
> 「可证伪」= 能落成某个可观测指标的具体阈值；写不出阈值就填「不可证伪」，这本身就是发现。

## 三、逻辑缺口

（待填：从论据到结论之间，作者跳过了哪一步？最常缺的是「产能落地 → 卖得掉 → 价格不塌」这三跳里的后两跳）

## 四、到期复盘

<!-- AUTO:SCORE -->
（系统在到期后自动填入机械口径成绩）
<!-- /AUTO:SCORE -->

### 定性判定

（待填：每条论据 成立 / 部分成立 / 不成立，以及不成立的机制是哪一类——需求没来、价格崩了、竞争提前、自己算错了、还是就是个故事）
"""
    return fm, tpl


def write_claim(fm, tpl):
    os.makedirs(CLAIMS, exist_ok=True)
    path = os.path.join(CLAIMS, fm["claim_id"] + ".md")
    if os.path.exists(path):
        return path, "exists"
    with open(path, "w", encoding="utf-8") as f:
        f.write(yamlite.join_front_matter(fm, tpl))
    return path, "new"


def write_archive(info_code, title, body, meta, frozen_at):
    os.makedirs(ARCHIVE, exist_ok=True)
    path = os.path.join(ARCHIVE, f"{info_code}.md")
    if os.path.exists(path):
        return path, "exists"
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    fm = {
        "info_code": info_code,
        "title": title or (meta.get("title") or ""),
        "org": meta.get("orgSName") or "",
        "stock": meta.get("stockName") or "",
        "code": str(meta.get("stockCode") or ""),
        "publish_date": (meta.get("publishDate") or "")[:10],
        "source_url": ("https://data.eastmoney.com/report/zw_stock.jshtml?encodeUrl="
                       + (meta.get("encodeUrl") or "")),
        "pdf_url": f"https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf",
        "fetched_at": frozen_at,
        "chars": len(body),
        "sha256": sha,
    }
    with open(path, "w", encoding="utf-8") as f:
        f.write(yamlite.join_front_matter(fm, "# 原文（东财公开正文，未删改）\n\n" + body))
    return path, "new"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--detail")
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--max-publish", default="9999-12-31",
                    help="只选该日期及之前发布的报告（保证 12 个月已到期）")
    ap.add_argument("--info", nargs="*")
    args = ap.parse_args()

    meta_index = {}
    for p in glob.glob(os.path.join(ROOT, "数据", "01_研报元数据", "*.jsonl")):
        for r in load_jsonl(p):
            meta_index[r.get("infoCode")] = r
    print(f"元数据索引 {len(meta_index)} 条")

    if args.info:
        targets = [(None, {"infoCode": c}) for c in args.info]
    elif args.detail:
        targets = pick_samples(args.detail, args.n, args.max_publish)
    else:
        ap.error("要么给 --detail，要么给 --info")

    frozen_at = datetime.now().astimezone().isoformat(timespec="seconds")
    for tag, r in targets:
        ic = r["infoCode"]
        meta = meta_index.get(ic) or r
        if not meta.get("encodeUrl"):
            print(f"  ✗ {ic} 缺 encodeUrl，跳过")
            continue
        try:
            title, body = em.report_fulltext(meta["encodeUrl"], q_type=0)
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {ic} 正文抓取失败 {type(e).__name__}: {e}")
            continue
        if len(body) < 200:
            print(f"  ✗ {ic} 正文过短({len(body)})，跳过")
            continue
        apath, st = write_archive(ic, title, body, meta, frozen_at)
        fm, tpl = build_claim(ic, meta, body, frozen_at)
        cpath, cst = write_claim(fm, tpl)
        print(f"  [{tag or '指定'}] {fm['stock']:<8} {fm['org']:<8} {fm['publish_date']}  "
              f"正文{len(body):>5}字  原文:{st}  骨架:{cst}")
        print(f"        -> 论据库/claims/{os.path.basename(cpath)}")


if __name__ == "__main__":
    main()
