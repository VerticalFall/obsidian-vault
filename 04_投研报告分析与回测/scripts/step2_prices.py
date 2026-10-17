# -*- coding: utf-8 -*-
"""Step 2 — 行情缓存：为元数据里出现的每只股票拉全量日线（前复权），并拉基准指数。

用法:
    python scripts/step2_prices.py --meta 数据/01_研报元数据/个股_2025.jsonl

产物:
    数据/02_行情/{股票代码}.jsonl        每行 {"d": "2025-03-03", "c": 12.34}
    数据/02_行情/_index_{指数名}.jsonl
"""
import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import em  # noqa: E402

BEG, END = "2024-11-01", "2026-12-31"
NBARS = 800


def save(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for d, c in rows:
            f.write(json.dumps({"d": d, "c": round(c, 4)}) + "\n")


def fetch_one(code):
    path = os.path.join(em.data_dir("02_行情"), f"{code}.jsonl")
    if os.path.exists(path) and os.path.getsize(path) > 50:
        return code, "cached"
    try:
        rows = em.kline(code, n=NBARS)
        if not rows:
            return code, "empty"
        save(path, rows)
        return code, f"ok:{len(rows)}"
    except Exception as e:  # noqa: BLE001
        return code, f"err:{type(e).__name__}"
    finally:
        time.sleep(0.02)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", action="append", required=True)
    args = ap.parse_args()

    codes = set()
    for m in args.meta:
        with open(m, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                c = str(r.get("stockCode") or "").strip()
                if c.isdigit() and len(c) == 6:
                    codes.add(c)
    codes = sorted(codes)
    print(f"待取行情股票数: {len(codes)}")

    # 指数
    for name, sid in em.INDEX.items():
        path = os.path.join(em.data_dir("02_行情"), f"_index_{name}.jsonl")
        if not (os.path.exists(path) and os.path.getsize(path) > 50):
            save(path, em.index_kline(sid, n=NBARS))
            print(f"  指数 {name} ok")

    stats = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(fetch_one, c): c for c in codes}
        for i, fut in enumerate(as_completed(futs), 1):
            code, status = fut.result()
            key = status.split(":")[0]
            stats[key] = stats.get(key, 0) + 1
            if i % 500 == 0:
                print(f"  {i}/{len(codes)}  {stats}", file=sys.stderr)
    print(f"完成: {stats}")


if __name__ == "__main__":
    main()
