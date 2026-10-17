# -*- coding: utf-8 -*-
"""交叉检验：扎堆度与追涨度是否互相混淆（6个月口径）。"""
import json
import statistics
from collections import defaultdict

SRC = "数据/03_回测结果/backtest_沪深300_20261017_样本明细.jsonl"

rows = []
with open(SRC, encoding="utf-8") as f:
    for line in f:
        r = json.loads(line)
        if "6个月" in r and "cluster" in r and "pre60" in r:
            rows.append(r)

print(f"样本 {len(rows)}")


def cbucket(c):
    return "1" if c == 1 else "2-3" if c <= 3 else "4-9" if c <= 9 else "10+"


def pbucket(x):
    if x < -20:
        return "跌>20%"
    if x < 0:
        return "跌0-20%"
    if x < 20:
        return "涨0-20%"
    if x < 50:
        return "涨20-50%"
    return "涨>50%"


print("\n=== 交叉样本数（行=扎堆度, 列=报告前60日涨幅）===")
cross = defaultdict(int)
for r in rows:
    cross[(cbucket(r["cluster"]), pbucket(r["pre60"]))] += 1
cols = ["跌>20%", "跌0-20%", "涨0-20%", "涨20-50%", "涨>50%"]
print(f"{'':10}" + "".join(f"{c:>10}" for c in cols))
for rb in ["1", "2-3", "4-9", "10+"]:
    print(f"{rb:10}" + "".join(f"{cross[(rb,c)]:>10}" for c in cols))
    tot = sum(cross[(rb, c)] for c in cols)
    share = cross[(rb, "涨>50%")] + cross[(rb, "涨20-50%")]
    print(f"{'  其中涨超20%占比':10}{share/tot*100:>9.1f}%")

print("\n=== 双向中位超额（找同质条件下的扎堆效应）===")
print(f"{'':10}" + "".join(f"{c:>10}" for c in cols))
for rb in ["1", "2-3", "4-9", "10+"]:
    cells = []
    for c in cols:
        v = [r["6个月"][0] for r in rows if cbucket(r["cluster"]) == rb and pbucket(r["pre60"]) == c]
        cells.append(f"{statistics.median(v):+.1f}%/{len(v)}" if len(v) >= 20 else "—")
    print(f"{rb:10}" + "".join(f"{x:>10}" for x in cells))

print("\n=== 同质对比：仅取『涨0-20%』区间，按扎堆度分 ===")
for rb in ["1", "2-3", "4-9", "10+"]:
    v = [r["6个月"][0] for r in rows if cbucket(r["cluster"]) == rb and pbucket(r["pre60"]) == "涨0-20%"]
    if len(v) >= 20:
        hit = sum(1 for x in v if x > 0) / len(v) * 100
        print(f"  {rb:>5}  n={len(v):<5} 中位 {statistics.median(v):+.2f}%  跑赢率 {hit:.1f}%")
