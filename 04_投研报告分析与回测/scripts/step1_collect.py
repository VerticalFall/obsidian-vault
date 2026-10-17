# -*- coding: utf-8 -*-
"""Step 1 — 采集研报元数据并冻结入库。

用法:
    python scripts/step1_collect.py --begin 2025-01-01 --end 2025-12-31
    python scripts/step1_collect.py --begin 2026-01-01 --end 2026-12-31 --qtype 1

产物: 数据/01_研报元数据/{个股|行业|策略}_{起始年}.jsonl
每条记录附带 _frozen 元信息（抓取时间 / 来源 / infoCode），入库后不再改写。
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import em  # noqa: E402

QTYPE_NAME = {0: "个股", 1: "行业", 3: "策略"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--begin", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--qtype", type=int, default=0)
    args = ap.parse_args()

    out_dir = em.data_dir("01_研报元数据")
    out = os.path.join(out_dir, f"{QTYPE_NAME.get(args.qtype,'其它')}_{args.begin[:4]}.jsonl")

    seen = set()
    if os.path.exists(out):                      # 允许增量续跑，不覆盖已有记录
        with open(out, encoding="utf-8") as f:
            for line in f:
                try:
                    seen.add(json.loads(line)["infoCode"])
                except Exception:  # noqa: BLE001
                    pass
        print(f"已有 {len(seen)} 条，增量续跑")

    fetched_at = datetime.now().astimezone().isoformat(timespec="seconds")
    n_new = n_dup = 0
    with open(out, "a", encoding="utf-8") as f:
        for row in em.iter_reports(args.begin, args.end, q_type=args.qtype):
            code = row.get("infoCode") or row.get("id")
            if not code or code in seen:
                n_dup += 1
                continue
            seen.add(code)
            rec = dict(row)
            rec["_frozen"] = {
                "fetchedAt": fetched_at,
                "source": "eastmoney/reportapi/report/list",
                "qType": args.qtype,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_new += 1
            if n_new % 500 == 0:
                f.flush()
                print(f"  +{n_new} ...", file=sys.stderr)
                time.sleep(0.2)

    print(f"完成: 新增 {n_new} 条, 跳过重复 {n_dup} 条 -> {out}")


if __name__ == "__main__":
    main()
