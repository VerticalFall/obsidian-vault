# -*- coding: utf-8 -*-
"""东方财富数据源封装：研报元数据 / 研报全文 / 日线行情。

只用标准库。所有请求带 UA，失败重试。
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "数据")


def http(url, retries=4, timeout=30, encoding="utf-8"):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Referer": "https://data.eastmoney.com/",
                "Accept": "*/*",
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode(encoding, "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.2 * (i + 1))
    raise last or RuntimeError("http failed")


def http_json(url, **kw):
    txt = http(url, **kw)
    txt = txt.strip()
    if txt.startswith("("):          # jsonp
        txt = txt[1:-1]
    return json.loads(txt)


# ---------------------------------------------------------------- 研报元数据
REPORT_LIST = "https://reportapi.eastmoney.com/report/list"


def report_page(begin, end, page, page_size=100, q_type=0):
    qs = urllib.parse.urlencode({
        "industryCode": "*", "pageSize": page_size, "industry": "*",
        "rating": "", "ratingChange": "", "beginTime": begin, "endTime": end,
        "pageNo": page, "fields": "", "qType": q_type, "orgCode": "",
        "code": "*", "rcode": "", "p": page, "pageNum": page, "pageNumber": page,
    })
    return http_json(f"{REPORT_LIST}?{qs}")


def iter_reports(begin, end, q_type=0, page_size=100, sleep=0.25):
    page, total_page = 1, 1
    while page <= total_page:
        js = report_page(begin, end, page, page_size, q_type)
        data = js.get("data") or []
        total_page = js.get("TotalPage") or 1
        if not data:
            return
        for row in data:
            yield row
        page += 1
        if page <= total_page:
            time.sleep(sleep)


# ---------------------------------------------------------------- 研报全文
def report_fulltext(encode_url, q_type=0):
    """返回 (标题, 正文纯文本)。q_type: 0 个股 / 1 行业 / 3 宏观策略"""
    page = {0: "zw_stock", 1: "zw_industry", 3: "zw_macresearch"}.get(q_type, "zw_stock")
    url = ("https://data.eastmoney.com/report/%s.jshtml?encodeUrl=%s"
           % (page, urllib.parse.quote(encode_url, safe="")))
    html = http(url)
    return _extract_body(html)


def _strip_tags(s):
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<br\s*/?>", "\n", s)
    s = re.sub(r"(?s)</p>", "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<")
          .replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'"))
    s = re.sub(r"[ \t\u3000]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()


def _extract_body(html):
    title = ""
    m = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", html)
    if m:
        title = _strip_tags(m.group(1))

    # 正文区：从 id="ctx-content" 开标签之后，切到免责声明/声明块之前
    body = ""
    start = html.find('id="ctx-content"')
    if start > 0:
        gt = html.find(">", start)
        seg = html[gt + 1:] if gt > 0 else html[start:]
        ends = [seg.find(mk) for mk in ("郑重声明", "免责声明", "点击查看全部", "数据来源")
                if seg.find(mk) > 0]
        body = _strip_tags(seg[:min(ends)] if ends else seg[:60000])

    if not body or len(body) < 80:          # 兜底：整页抽文本
        body = _strip_tags(html)
        for mk in ("主要观点", "投资要点", "事件点评", "核心观点"):
            i = body.find(mk)
            if i > 0:
                body = body[i:]
                break
    return title, body


# ---------------------------------------------------------------- 行情
# 说明：东财 push2his 对本机出口 IP 直接断连（web_fetch 侧可通），故行情改用腾讯。
# 腾讯返回前复权（qfq）日线，数组格式 [日期, 开, 收, 高, 低, 量]。
TENCENT = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"


def tq_symbol(stock_code):
    c = str(stock_code).strip()
    if c.startswith(("6", "9")):
        return "sh" + c
    if c.startswith(("4", "8")) or c.startswith("92"):
        return "bj" + c
    return "sz" + c


def _tq_pull(symbol, n=800, adjust="qfq"):
    url = f"{TENCENT}?param={symbol},day,,,{n},{adjust}"
    js = http_json(url)
    d = (js.get("data") or {}).get(symbol) or {}
    rows = d.get("qfqday") or d.get("day") or []
    out = []
    for r in rows:
        if len(r) >= 3:
            try:
                out.append((str(r[0]), float(r[2])))   # r[2] = 收盘
            except (ValueError, TypeError):
                continue
    return out


def kline(stock_code, n=800):
    """返回 [(date, close), ...] 前复权"""
    return _tq_pull(tq_symbol(stock_code), n=n, adjust="qfq")


INDEX = {"沪深300": "sh000300", "中证500": "sh000905", "中证1000": "sh000852"}


def index_kline(symbol, n=800):
    """指数不除权，取 day 序列"""
    seq = _tq_pull(symbol, n=n, adjust="qfq")
    if not seq:
        seq = _tq_pull(symbol, n=n, adjust="")
    return seq


# ---------------------------------------------------------------- 缓存
def ensure_dir(p):
    os.makedirs(p, exist_ok=True)
    return p


def data_dir(*parts):
    return ensure_dir(os.path.join(DATA, *parts))
