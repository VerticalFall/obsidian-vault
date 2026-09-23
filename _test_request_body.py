#!/usr/bin/env python3
"""请求体守卫 — 抓取真实出站 JSON，验证 thinking 关闭与参数正确。

为什么需要这个测试
    上一版守卫只正则匹配源码文本（"每个调用点都写了 thinking"），但那证明不了
    出站 JSON 真的正确：字段可能拼错位置、JSON 可能不合法、可能被 SDK 忽略。
    本测试**拦截 urlopen**、解析真实请求体，断言：
      - JSON 合法且含 model / messages / max_tokens
      - thinking.type 为 disabled（否则思维链会挤占 max_tokens，短预算调用必挂）
      - 短预算调用（翻译/语种判断/播客摘要）确实关闭了思考

全部离线：urlopen 被替换为假实现，不发起任何网络请求。

用法（在 每日日报/ 目录下）：
    python _test_request_body.py
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".github" / "scripts"))

import render_daily_digest as DG  # noqa: E402
import render_followbuilders as FB  # noqa: E402
import render_xtweets as XT  # noqa: E402
import run_daily_router as RT  # noqa: E402

FAILURES: list[str] = []
CAPTURED: list[dict] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


class FakeResponse:
    """最小可用的 urlopen 返回值。"""

    def __init__(self, payload: dict) -> None:
        self._buf = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def read(self) -> bytes:
        return self._buf.read()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def make_fake_urlopen(content: str = "译文内容"):
    """返回一个假 urlopen，记录请求体并回一个正常响应。"""

    def _fake(req, timeout=None):
        body = json.loads(req.data.decode("utf-8"))
        body["__url__"] = req.full_url
        CAPTURED.append(body)
        return FakeResponse({"choices": [{"message": {"content": content}}]})

    return _fake


def last_body() -> dict:
    return CAPTURED[-1] if CAPTURED else {}


def main() -> int:
    import os

    os.environ.setdefault("DEEPSEEK_API_KEY", "test-key-not-real")
    # render_xtweets / render_followbuilders 把 API Key 读进**模块级常量**
    # （import 时就定型了），所以必须直接改常量，光设环境变量无效。
    XT.DEEPSEEK_API_KEY = "test-key-not-real"
    FB.DEEPSEEK_API_KEY = "test-key-not-real"

    all_seen: list[dict] = []

    def scenario(label: str, fn, content: str = "内容"):
        """跑一个场景并在最后统一收集其请求体（供跨场景汇总断言）。"""
        CAPTURED.clear()
        with mock.patch("urllib.request.urlopen", make_fake_urlopen(content)):
            fn()
        all_seen.extend(CAPTURED)
        return last_body()

    # ── 1. 路由 ──
    b = scenario("路由", lambda: RT.call_deepseek("系统提示", "用户输入"),
                 "===ROUTE_LOG===\n内容")
    check("路由：请求体为合法 JSON 且含必需字段",
          all(k in b for k in ("model", "messages", "max_tokens")), f"keys={sorted(k for k in b if k != '__url__')}")
    check("路由：thinking 已关闭", b.get("thinking", {}).get("type") == "disabled", str(b.get("thinking")))
    check("路由：model 为当前模型名", b.get("model") == "deepseek-flash", str(b.get("model")))

    # ── 2. 精选 ──
    b = scenario("精选", lambda: DG.call_deepseek("系统提示", "用户输入"),
                 "===DIGEST===\n内容\n===END===")
    check("精选：thinking 已关闭", b.get("thinking", {}).get("type") == "disabled", str(b.get("thinking")))
    check("精选：model 为当前模型名", b.get("model") == "deepseek-flash", str(b.get("model")))

    # ── 3. X-Tweets 翻译（短预算调用，最关键）──
    b = scenario("X-Tweets 翻译",
                 lambda: XT.translate_to_chinese("This is an English sentence about DRAM supply."),
                 "中文译文")
    check("X-Tweets 翻译：thinking 已关闭（否则 2000 token 内拿不到正文）",
          b.get("thinking", {}).get("type") == "disabled", str(b.get("thinking")))
    check("X-Tweets 翻译：model 为当前模型名", b.get("model") == "deepseek-flash", str(b.get("model")))

    # ── 3b. X-Tweets 语种判断（100 token，预算最短）──
    CAPTURED.clear()
    with mock.patch("urllib.request.urlopen", make_fake_urlopen("en")):
        XT.translate_text("Some english text")
    all_seen.extend(CAPTURED)
    if CAPTURED:
        b = last_body()
        check("X-Tweets 短调用（100 token）：thinking 已关闭",
              b.get("thinking", {}).get("type") == "disabled", str(b.get("thinking")))

    # ── 4. FollowBuilders 播客摘要（300 token，最短预算）──
    b = scenario("FB 播客摘要",
                 lambda: FB.summarize_podcast("Podcast", "Title", "transcript text " * 20),
                 "中文摘要")
    check("FB 播客摘要：thinking 已关闭（300 token 预算）",
          b.get("thinking", {}).get("type") == "disabled", str(b.get("thinking")))
    check("FB 播客摘要：model 为当前模型名", b.get("model") == "deepseek-flash", str(b.get("model")))

    # ── 4b. FollowBuilders 翻译 ──
    b = scenario("FB 翻译", lambda: FB.translate_to_chinese("English text about GPU supply."),
                 "中文译文")
    check("FB 翻译：thinking 已关闭", b.get("thinking", {}).get("type") == "disabled", str(b.get("thinking")))

    # ── 5. 汇总：跨全部场景的每个请求体都必须关闭思考 ──
    check("跨全部场景的请求体都关闭了 thinking",
          len(all_seen) >= 5 and all(x.get("thinking", {}).get("type") == "disabled" for x in all_seen),
          f"共 {len(all_seen)} 个请求体")
    models = {x.get("model") for x in all_seen}
    check("跨全部场景的模型名都正确", models == {"deepseek-flash"}, str(models))

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} 项未通过: {FAILURES}")
        return 1
    print("✓ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
