# -*- coding: utf-8 -*-
"""Step 5 — 到期机械打分 + 看板刷新。

用法:
    python scripts/step5_score.py            # 全部 claim
    python scripts/step5_score.py --due-only # 只看已到期

做三件事：
1. 对已到期的 claim，把机械口径成绩写回 `<!-- AUTO:SCORE -->` 区块（价格/超额/目标价达成）
2. 未到期的写「距到期还有 N 个交易日」
3. 重新生成 论据库/_看板.md

不做的事：判断论据成立与否 —— 那需要读原文 + 证伪条件，属于人和模型的活。
"""
import argparse
import bisect
import glob
import json
import os
import statistics
import sys
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yamlite  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS = os.path.join(ROOT, "论据库", "claims")
PXD = os.path.join(ROOT, "数据", "02_行情")
BENCH = "沪深300"
TD_PER_MONTH = 21
START = "<!-- AUTO:SCORE -->"
END = "<!-- /AUTO:SCORE -->"


def load_jsonl(p):
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_series(path):
    rows = load_jsonl(path)
    return [r["d"] for r in rows], [r["c"] for r in rows]


def at_or_before(dates, closes, d):
    i = bisect.bisect_right(dates, d) - 1
    return (dates[i], closes[i]) if i >= 0 else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default=BENCH)
    ap.add_argument("--due-only", action="store_true")
    args = ap.parse_args()

    bdates, bcloses = load_series(os.path.join(PXD, f"_index_{args.bench}.jsonl"))
    today = date.today().isoformat()

    files = sorted(glob.glob(os.path.join(CLAIMS, "*.md")))
    if not files:
        print("论据库/claims/ 下没有 claim 文件")
        return

    board = []
    for p in files:
        text = open(p, encoding="utf-8").read()
        fm, body = yamlite.split_front_matter(text)
        code = str(fm.get("code") or "")
        pdate = str(fm.get("publish_date") or "")[:10]
        months = int(fm.get("horizon_months") or 12)
        need = months * TD_PER_MONTH

        px_path = os.path.join(PXD, f"{code}.jsonl")
        if not (code and pdate and os.path.exists(px_path)):
            board.append((fm, "缺行情", None, None, None))
            continue
        sdates, scloses = load_series(px_path)

        # 建仓：报告日之后第一个交易日
        i0 = bisect.bisect_right(sdates, pdate)
        if i0 >= len(sdates):
            board.append((fm, "建仓期未到", None, None, None))
            continue
        entry_date, entry_px = sdates[i0], scloses[i0]

        # 到期日：从基准日历里取 N 个交易日
        j0 = bisect.bisect_right(bdates, entry_date) - 1
        if j0 < 0:
            board.append((fm, "基准对齐失败", None, None, None))
            continue
        jt = j0 + need
        due_date = bdates[jt] if jt < len(bdates) else None

        if due_date is None or due_date > today:
            left = (jt - (len(bdates) - 1)) if jt >= len(bdates) else None
            block = (f"未到期。建仓日 {entry_date}（{entry_px}），"
                     f"预计到期 {due_date or '数据未生成'}，"
                     f"{('还需要 ' + str(left) + ' 个交易日') if left else '尚在期限内'}")
            new_body = _replace_block(body, block)
            _write(p, fm, new_body)
            board.append((fm, "未到期", None, None, None))
            continue

        exit_date, exit_px = at_or_before(sdates, scloses, due_date)
        if exit_px is None:
            board.append((fm, "缺到期价", None, None, None))
            continue
        ret = (exit_px / entry_px - 1) * 100
        _, b_exit = at_or_before(bdates, bcloses, due_date)
        _, b_entry = at_or_before(bdates, bcloses, entry_date)
        bret = (b_exit / b_entry - 1) * 100 if (b_entry and b_exit) else float("nan")
        excess = ret - bret

        # 目标价达成：期内最高价是否触及
        window = scloses[i0:i0 + need]
        peak = max(window) if window else exit_px
        tp = fm.get("target_price")
        tp_note = "未披露目标价"
        tp_hit = None
        if tp:
            tp_hit = peak >= float(tp)
            tp_note = f"目标价 {tp}：期内最高 {peak:.2f} → {'已触及' if tp_hit else '未触及'}"

        lines = [
            f"**机械口径成绩**（{entry_date} 建仓 → {due_date} 到期，基准 {args.bench}）",
            "",
            "| 项目 | 数值 |",
            "|---|---|",
            f"| 建仓价 / 到期价 | {entry_px} → {exit_px} |",
            f"| 区间收益 | {ret:+.2f}% |",
            f"| 同期{args.bench} | {bret:+.2f}% |",
            f"| **超额** | **{excess:+.2f}%** |",
            f"| 目标价 | {tp_note} |",
            f"| EPS 预测（当年 {fm.get('eps_this_year')} / 次年 {fm.get('eps_next_year')}） | 需人工核对实际值 |",
        ]
        new_body = _replace_block(body, "\n".join(lines))
        _write(p, fm, new_body)
        board.append((fm, "已到期", ret, excess, tp_hit))

    # ---------- 看板
    out = ["---", "title: 论据库看板", "type: dashboard", "---", "",
           "# 论据库看板", "",
           f"> 自动生成于 {datetime.now().astimezone():%Y-%m-%d %H:%M}　"
           f"共 {len(board)} 条　规则见 [[_规则]]", "",
           "| 股票 | 机构 | 发布日 | 评级 | 状态 | 区间收益 | 超额 | 目标价 |",
           "|---|---|---|---|---|---|---|---|"]
    for fm, st, ret, excess, tphit in board:
        r = f"{ret:+.1f}%" if ret is not None else "–"
        e = f"{excess:+.1f}%" if excess is not None else "–"
        t = "✅" if tphit is True else ("❌" if tphit is False else "–")
        out.append(f"| [[{fm['claim_id']}\\|{fm.get('stock','')}]] | {fm.get('org','')} | "
                   f"{fm.get('publish_date','')} | {fm.get('rating','')} | {st} | {r} | {e} | {t} |")

    due = [b for b in board if b[1] == "已到期" and b[3] is not None]
    if due:
        ex = [b[3] for b in due]
        hit = sum(1 for x in ex if x > 0)
        out += ["", f"## 汇总（已到期 {len(due)} 条）", "",
                f"- 超额中位数 {statistics.median(ex):+.2f}%",
                f"- 平均超额 {statistics.mean(ex):+.2f}%",
                f"- 跑赢基准 {hit}/{len(due)} = {hit/len(due)*100:.0f}%"]

    with open(os.path.join(ROOT, "论据库", "_看板.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"看板 -> 论据库/_看板.md（{len(board)} 条）")
    for fm, st, ret, excess, _ in board:
        print(f"  {fm.get('stock',''):<8} {fm.get('org',''):<8} {st:<8}"
              f"超额 {('%.2f%%' % excess) if excess is not None else '–'}")


def _replace_block(body, new_inner):
    if START in body and END in body:
        a = body.index(START) + len(START)
        b = body.index(END)
        return body[:a] + "\n" + new_inner + "\n" + body[b:]
    return body + f"\n{START}\n{new_inner}\n{END}\n"


def _write(path, fm, body):
    with open(path, "w", encoding="utf-8") as f:
        f.write(yamlite.join_front_matter(fm, body))


if __name__ == "__main__":
    main()
