# -*- coding: utf-8 -*-
"""Step 3 — 回测：把研报的"立场"与后续真实收益对齐。
"""
import argparse
import bisect
import glob
import json
import os
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import em  # noqa: E402

HORIZONS = {"1个月": 21, "3个月": 63, "6个月": 126, "12个月": 252}
BULL = {"买入", "增持", "强烈推荐", "推荐", "优于大市", "跑赢行业", "强推", "审慎增持"}
NEUTRAL = {"中性", "持有", "同步大市", "中性评级"}
BEAR = {"卖出", "减持", "回避", "弱于大市", "跑输行业"}


def load_jsonl(p):
    rows = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:  # noqa: BLE001
                    pass
    return rows


def load_prices(d):
    px = {}
    for p in glob.glob(os.path.join(d, "*.jsonl")):
        code = os.path.basename(p)[:-6]
        if code.startswith("_index_"):
            continue
        seq = load_jsonl(p)
        if seq:
            px[code] = [(r["d"], r["c"]) for r in seq]
    return px


def load_index(d, name="沪深300"):
    p = os.path.join(d, f"_index_{name}.jsonl")
    seq = load_jsonl(p)
    return [(r["d"], r["c"]) for r in seq]


class Series:
    __slots__ = ("dates", "closes", "_dv")

    def __init__(self, seq):
        self.dates = [d for d, _ in seq]
        self.closes = [c for _, c in seq]
        self._dv = dict(seq)

    def at_or_after(self, date):
        i = bisect.bisect_left(self.dates, date)
        return self.closes[i] if i < len(self.closes) else None

    def at_or_before(self, date):
        i = bisect.bisect_right(self.dates, date) - 1
        return self.closes[i] if i >= 0 else None


def stance(r):
    name = r.get("emRatingName") or ""
    if name in BULL:
        return "偏多"
    if name in BEAR:
        return "偏空"
    if name in NEUTRAL:
        return "中性"
    return "未评级"


def pct(xs, q):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def fmt(x, nd=2):
    if x != x:
        return "n/a"
    return f"{x:+.{nd}f}%"


def _shift(date_str, days):
    y, m, dd = (int(x) for x in date_str.split("-"))
    return (datetime(y, m, dd) + timedelta(days=days)).strftime("%Y-%m-%d")


def describe(rows, label):
    """rows: [(excess_pct, ret_pct, bench_pct)]"""
    if not rows:
        return f"| {label} | 0 | – | – | – | – |"
    ex = [r[0] for r in rows]
    hit = sum(1 for v in ex if v > 0) / len(ex) * 100
    return ("| %s | %d | %s | %s | %s | %.1f%% |"
            % (label, len(rows), fmt(statistics.mean(ex)), fmt(statistics.median(ex)),
               fmt(pct(ex, 0.25)), hit))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--bench", default="沪深300")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    d = em.data_dir("02_行情")
    reports = load_jsonl(args.meta)
    px = load_prices(d)
    bseq = Series(load_index(d, args.bench))
    cal, bidx = bseq.dates, {dd: i for i, dd in enumerate(bseq.dates)}
    sers = {c: Series(s) for c, s in px.items()}
    print(f"研报 {len(reports)} 篇, 行情 {len(sers)} 只, 基准 {args.bench} {len(cal)} 交易日")

    # ---------- 逐篇计算各期超额收益
    recs = []
    miss_px = miss_mat = 0
    for r in reports:
        code = str(r.get("stockCode") or "").strip()
        s = sers.get(code)
        pd_ = (r.get("publishDate") or "")[:10]
        if not s or not pd_:
            miss_px += 1
            continue
        bi = bidx.get(pd_)
        if bi is None:                       # 非交易日（周末/节假日）→ 以之前最后一个交易日为基准
            j = bisect.bisect_left(cal, pd_)
            if j <= 0:
                continue
            bi = j - 1
        bi += 1                              # T+1 建仓，保守
        if bi >= len(cal):
            continue
        entry_date = cal[bi]
        entry = s.at_or_after(entry_date)
        if not entry:
            miss_px += 1
            continue
        rec = {
            "code": code, "name": r.get("stockName"), "org": r.get("orgSName"),
            "title": r.get("title"), "date": pd_, "entry": entry_date,
            "rating": r.get("emRatingName") or "", "stance": stance(r),
            "rc": str(r.get("ratingChange") if r.get("ratingChange") is not None else ""),
            "infoCode": r.get("infoCode"),
            "industry": r.get("indvInduName") or "",
        }
        ok = False
        for hname, n in HORIZONS.items():
            ei = bi + n
            if ei >= len(cal):
                continue
            end_date = cal[ei]
            exit_ = s.at_or_before(end_date)
            if not exit_:
                continue
            bench = (bseq.closes[ei] / bseq.closes[bi] - 1) * 100
            ret = (exit_ / entry - 1) * 100
            rec[hname] = (ret - bench, ret, bench)
            ok = True
        if ok:
            recs.append(rec)
        else:
            miss_mat += 1

    print(f"可用样本 {len(recs)} 篇 (缺行情 {miss_px}, 期限未满 {miss_mat})")

    # ---------- 市场状态（发布时点沪深300 近60日涨跌）三等分
    trailing = []
    for r in recs:
        bi = bidx[r["entry"]] - 1
        bi = max(bi, 60)
        if bi - 60 >= 0:
            trailing.append((bseq.closes[bi] / bseq.closes[bi - 60] - 1) * 100)
        else:
            trailing.append(0.0)
    if trailing:
        q1, q2 = pct(trailing, 1 / 3), pct(trailing, 2 / 3)
        for r, t in zip(recs, trailing):
            r["mkt"] = "弱市" if t <= q1 else ("强市" if t >= q2 else "震荡")
            r["mkt_ret60"] = t

    # ---------- 扎堆度：该股近 30 天内被发了几篇研报（含本篇）
    by_stock = defaultdict(list)
    for r in recs:
        by_stock[r["code"]].append(r)
    for code, lst in by_stock.items():
        lst.sort(key=lambda x: x["date"])
        dates = [x["date"] for x in lst]
        for i, r in enumerate(lst):
            j = bisect.bisect_left(dates, _shift(r["date"], -30))
            r["cluster"] = i - j + 1

    # ---------- 发布前 60 日个股涨幅（追涨度）
    for r in recs:
        s = sers.get(r["code"])
        if not s:
            continue
        c0 = s.at_or_before(r["entry"])
        i = bisect.bisect_right(s.dates, r["entry"]) - 1
        if c0 and i - 60 >= 0:
            r["pre60"] = (c0 / s.closes[i - 60] - 1) * 100

    L = []
    L.append(f"# 卖方研报立场回测 — {args.bench} 基准\n")
    L.append(f"生成时间：{datetime.now().astimezone():%Y-%m-%d %H:%M}　"
             f"样本：{len(recs)} 篇　建仓：T+1 收盘　收益：前复权\n")

    for hname in HORIZONS:
        sub = [r for r in recs if hname in r]
        if not sub:
            continue
        L.append(f"\n## {hname}持有期（相对{args.bench}超额）\n")
        L.append("| 分组 | 样本 | 平均超额 | 中位超额 | 25分位 | 跑赢率 |")
        L.append("|---|---|---|---|---|---|")
        for tag in ("偏多", "中性", "偏空", "未评级"):
            rows = [r[hname] for r in sub if r["stance"] == tag]
            L.append(describe(rows, tag))
        rows = [r[hname] for r in sub]
        L.append(describe(rows, "**全部**"))

        L.append(f"\n### {hname} · 按评级变动\n")
        L.append("| 分组 | 样本 | 平均超额 | 中位超额 | 25分位 | 跑赢率 |")
        L.append("|---|---|---|---|---|---|")
        for code, name in (("2", "首次覆盖"), ("0", "上调"), ("1", "下调"), ("3", "维持")):
            rows = [r[hname] for r in sub if r["rc"] == code]
            if rows:
                L.append(describe(rows, name))

        if "mkt" in sub[0]:
            L.append(f"\n### {hname} · 按发布时市场状态（沪深300近60日）\n")
            L.append("| 分组 | 样本 | 平均超额 | 中位超额 | 25分位 | 跑赢率 |")
            L.append("|---|---|---|---|---|---|")
            for tag in ("强市", "震荡", "弱市"):
                rows = [r[hname] for r in sub if r["mkt"] == tag]
                L.append(describe(rows, tag))

    # ---------- 评级分布 × 市场状态（"牛市唱多熊市唱衰"是否成立）
    if recs and "mkt" in recs[0]:
        L.append("\n## 立场分布 × 市场状态（检验「牛市唱多、熊市唱衰」）\n")
        L.append("| 市场状态 | 样本 | 偏多占比 | 中性占比 | 偏空占比 |")
        L.append("|---|---|---|---|---|")
        for tag in ("强市", "震荡", "弱市"):
            sub = [r for r in recs if r["mkt"] == tag]
            if not sub:
                continue
            c = Counter(r["stance"] for r in sub)
            n = len(sub)
            L.append("| %s | %d | %.1f%% | %.1f%% | %.1f%% |"
                     % (tag, n, c["偏多"] / n * 100, c["中性"] / n * 100, c["偏空"] / n * 100))

    # ---------- 扎堆度 / 追涨度（主口径：6个月）
    hname = "6个月"
    sub6 = [r for r in recs if hname in r]
    if sub6 and "cluster" in sub6[0]:
        L.append(f"\n## 覆盖扎堆度 · {hname}超额（检验「集体唱多=抬轿出货」）\n")
        L.append("> 口径：同一只股票在报告日前 30 天内被券商覆盖的篇数（含本篇）\n")
        L.append("| 近30天覆盖篇数 | 样本 | 平均超额 | 中位超额 | 25分位 | 跑赢率 |")
        L.append("|---|---|---|---|---|---|")
        for lo, hi, label in ((1, 1, "1 篇（独家）"), (2, 3, "2–3 篇"),
                              (4, 9, "4–9 篇"), (10, 10**9, "10 篇以上（扎堆）")):
            rows = [r[hname] for r in sub6 if lo <= r["cluster"] <= hi]
            L.append(describe(rows, label))

    if sub6 and "pre60" in sub6[0]:
        L.append(f"\n## 追涨度 · {hname}超额（检验「涨完才出报告」）\n")
        L.append("| 报告前60日个股涨幅 | 样本 | 平均超额 | 中位超额 | 25分位 | 跑赢率 |")
        L.append("|---|---|---|---|---|---|")
        for lo, hi, label in ((-10**9, -20, "跌超 20%"), (-20, 0, "跌 0–20%"),
                              (0, 20, "涨 0–20%"), (20, 50, "涨 20–50%"),
                              (50, 10**9, "涨超 50%")):
            rows = [r[hname] for r in sub6 if "pre60" in r and lo <= r["pre60"] < hi]
            L.append(describe(rows, label))

    # ---------- 机构榜（6个月，按跑赢率排序，规避右偏均值误导）
    hname = "6个月"
    sub = [r for r in recs if hname in r]
    if sub:
        by_org = defaultdict(list)
        for r in sub:
            by_org[r["org"]].append(r[hname][0])
        board = []
        for o, v in by_org.items():
            if len(v) < 60:
                continue
            hit = sum(1 for x in v if x > 0) / len(v) * 100
            board.append((o, len(v), statistics.median(v), hit))
        board.sort(key=lambda x: -x[3])
        L.append(f"\n## 机构榜 · {hname}超额（样本≥60篇，按跑赢率排序）\n")
        L.append("| 机构 | 样本 | 中位超额 | 跑赢率 |")
        L.append("|---|---|---|---|")
        for o, n, m, h in board[:15]:
            L.append(f"| {o} | {n} | {m:+.2f}% | {h:.1f}% |")
        L.append("\n垫底 8 家：\n")
        L.append("| 机构 | 样本 | 中位超额 | 跑赢率 |")
        L.append("|---|---|---|---|")
        for o, n, m, h in board[-8:][::-1]:
            L.append(f"| {o} | {n} | {m:+.2f}% | {h:.1f}% |")

    # ---------- 时间稳定性：按报告季度分组的 6个月前向超额
    if sub:
        by_q = defaultdict(list)
        for r in sub:
            by_q[r["date"][:4] + "Q" + str((int(r["date"][5:7]) - 1) // 3 + 1)].append(r[hname][0])
        L.append(f"\n## 时间稳定性 · 按发布季度看 {hname}超额\n")
        L.append("| 发布季度 | 样本 | 中位超额 | 跑赢率 |")
        L.append("|---|---|---|---|")
        for q in sorted(by_q):
            v = by_q[q]
            hit = sum(1 for x in v if x > 0) / len(v) * 100
            L.append(f"| {q} | {len(v)} | {statistics.median(v):+.2f}% | {hit:.1f}% |")

    # ---------- 基准环境
    L.append("\n## 基准环境（用于解读超额）\n")
    L.append("| 指数 | 区间 | 涨跌 |")
    L.append("|---|---|---|")
    for name in em.INDEX:
        seq = load_index(d, name)
        if not seq:
            continue
        for a, b in (("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-10-17")):
            seg = [c for dd, c in seq if a <= dd <= b]
            if len(seg) > 2:
                L.append(f"| {name} | {a[:7]} ~ {b[:7]} | {(seg[-1]/seg[0]-1)*100:+.1f}% |")

    out = args.out or os.path.join(em.data_dir("03_回测结果"),
                                   f"backtest_{args.bench}_{datetime.now():%Y%m%d}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("报告 ->", out)

    # 附带明细，供后续拆解报告使用
    det = os.path.splitext(out)[0] + "_样本明细.jsonl"
    with open(det, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("样本明细 ->", det)


if __name__ == "__main__":
    main()
