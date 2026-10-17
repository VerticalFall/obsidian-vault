# -*- coding: utf-8 -*-
"""Recon: 拉取东财研报元数据，统计评级分布 / 机构产出量。

仅用标准库。用法:
    python scripts/recon_ratings.py 2025-01-01 2025-12-31
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

BASE = "https://reportapi.eastmoney.com/report/list"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def fetch_json(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            if i == retries - 1:
                raise
            print(f"  retry {i+1}: {e}", file=sys.stderr)
            time.sleep(1.5 * (i + 1))


def pull(begin, end, q_type=0, page_size=100, max_pages=200):
    rows, page = [], 1
    while page <= max_pages:
        qs = urllib.parse.urlencode({
            "industryCode": "*", "pageSize": page_size, "industry": "*",
            "rating": "", "ratingChange": "", "beginTime": begin, "endTime": end,
            "pageNo": page, "fields": "", "qType": q_type, "orgCode": "",
            "code": "*", "rcode": "", "p": page, "pageNum": page, "pageNumber": page,
        })
        js = fetch_json(f"{BASE}?{qs}")
        data = js.get("data") or []
        if not data:
            break
        rows.extend(data)
        total_page = js.get("TotalPage", 1)
        print(f"  page {page}/{total_page} (+{len(data)})", file=sys.stderr)
        if page >= total_page:
            break
        page += 1
        time.sleep(0.25)
    return rows


def main():
    begin = sys.argv[1] if len(sys.argv) > 1 else "2025-01-01"
    end = sys.argv[2] if len(sys.argv) > 2 else "2025-12-31"

    rows = pull(begin, end)
    print(f"\n=== 区间 {begin} ~ {end} 个股研报 {len(rows)} 篇 ===")

    ratings = Counter(r.get("emRatingName") or "(空)" for r in rows)
    total = sum(ratings.values())
    print("\n-- 评级分布 --")
    for name, n in ratings.most_common():
        print(f"  {name:<8} {n:>6}  {n/total*100:5.1f}%")

    orgs = Counter(r.get("orgSName") or "(空)" for r in rows)
    print(f"\n-- 机构产出 TOP15 (共 {len(orgs)} 家) --")
    for name, n in orgs.most_common(15):
        print(f"  {name:<14} {n:>5}")

    ratings_by_org = defaultdict(Counter)
    for r in rows:
        ratings_by_org[r.get("orgSName") or "(空)"][r.get("emRatingName") or "(空)"] += 1
    print("\n-- 头部机构评级结构 --")
    for name, _ in orgs.most_common(10):
        c = ratings_by_org[name]
        tot = sum(c.values())
        bull = sum(v for k, v in c.items() if k in ("买入", "增持", "强烈推荐", "推荐", "优于大市", "跑赢行业", "强推"))
        print(f"  {name:<14} n={tot:<4} 偏多占比 {bull/tot*100:5.1f}%  " + " ".join(f"{k}:{v}" for k, v in c.most_common(4)))

    # 目标价 / EPS 覆盖情况
    has_tp = sum(1 for r in rows if str(r.get("indvAimPriceT") or "").strip())
    has_eps = sum(1 for r in rows if str(r.get("predictThisYearEps") or "").strip())
    print(f"\n-- 结构化字段覆盖率 --\n  有目标价 {has_tp}/{len(rows)} ({has_tp/len(rows)*100:.1f}%)")
    print(f"  有当年EPS预测 {has_eps}/{len(rows)} ({has_eps/len(rows)*100:.1f}%)")

    rc = Counter(str(r.get("ratingChange")) for r in rows)
    print(f"\n-- ratingChange 分布 (2首次/0上调/1下调/3维持等) -- {dict(rc)}")


if __name__ == "__main__":
    main()
