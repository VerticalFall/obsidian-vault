#!/usr/bin/env python3
"""模型名守卫 — 防止再出现「用了已停用的模型名」这类静默失效。

为什么需要这个测试
    `deepseek-chat` 别名于 **2026-07-24** 停用（DeepSeek V4 公告：deepseek-chat /
    deepseek-reasoner 三个月后停止使用）。但渲染脚本一直用它，导致：
      - `render_xtweets.py` 翻译全挂 → 🔴「翻译成功率 0/N」从 2026-07-25 起断续出现
        两个月，无人定位到根因；
      - `render_followbuilders.py` 的播客摘要同样失效；
      - 我新写的 `render_daily_digest.py` 初版默认值也写成 deepseek-chat —— 等于
        一上线就是坏的。
    这类 bug **不会报错、只会静默降级**，所以必须有一道机械的守卫。

本测试不联网：只检查源码里不出现已停用/已弃用的模型名，并把当前应使用的模型名固定下来。

用法（在 每日日报/ 目录下）：
    python _test_model_names.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# 已停用 / 已被取代的模型名 —— 出现即失败
#   deepseek-chat / deepseek-reasoner : 2026-07-24 停用
#   deepseek-v4-flash                 : 2026-09-10 起被 V4.1 Flash 取代（旧名仅兼容路由）
#   deepseek-v4-pro                   : 2026-09-14 起被路由到 V4.1 Flash（计划下线）
RETIRED = {
    "deepseek-chat": "2026-07-24 停用",
    "deepseek-reasoner": "2026-07-24 停用",
    "deepseek-v4-flash": "2026-09-10 起被 V4.1 Flash 取代，旧名仅兼容路由",
    "deepseek-v4-pro": "2026-09-14 起被路由到 V4.1 Flash，计划下线",
}

# 当前应使用的模型名（DeepSeek V4.1 Flash，2026-09-10 上线）
CURRENT = "deepseek-flash"

FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(label)


def scan_files() -> list[Path]:
    """要扫描的源码与配置。

    跳过测试文件：本测试自身必须在 RETIRED 表里列出这些名字才能做守卫，
    那是守卫的"数据"而非"用法"。
    """
    out: list[Path] = []
    for pat in ("*.py", "*.yml", "*.yaml"):
        out.extend(HERE.glob(f".github/scripts/{pat}"))
        out.extend(HERE.glob(f".github/workflows/{pat}"))
        out.extend(HERE.glob(pat))
    return sorted({
        p for p in out
        if "__pycache__" not in str(p) and not p.name.startswith("_test_")
    })


def main() -> int:
    files = scan_files()
    check("扫描到脚本与 workflow", len(files) >= 10, f"{len(files)} 个文件")

    hits: list[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            # 注释行里提到停用模型名是允许的（我们正是这么记录教训的），
            # 只禁止出现在**可执行代码/配置**里。
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for name, why in RETIRED.items():
                if re.search(rf'["\']?{re.escape(name)}["\']?', line):
                    hits.append(f"{path.relative_to(HERE)}:{i} 用了 {name}（{why}）")
    check("源码/配置中无已停用模型名", not hits, "; ".join(hits[:5]))

    # 当前模型名确实被用起来了（避免"全删了"这种假通过）
    used = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            if CURRENT in line:
                used.append(f"{path.relative_to(HERE)}:{i}")
    check(f"当前模型名 {CURRENT} 已在使用", len(used) >= 3, f"{len(used)} 处: {used[:4]}")

    # 渲染脚本里的模型常量必须是当前名
    xt = (HERE / ".github/scripts/render_xtweets.py").read_text(encoding="utf-8")
    check("render_xtweets 翻译模型为当前名",
          re.search(rf'DEEPSEEK_TRANSLATE_MODEL\s*=\s*"{CURRENT}"', xt) is not None)
    fb = (HERE / ".github/scripts/render_followbuilders.py").read_text(encoding="utf-8")
    check("render_followbuilders 模型为当前名",
          re.search(rf'DEEPSEEK_MODEL\s*=\s*"{CURRENT}"', fb) is not None
          and re.search(rf'DEEPSEEK_FLASH_MODEL\s*=\s*"{CURRENT}"', fb) is not None)
    dg = (HERE / ".github/scripts/render_daily_digest.py").read_text(encoding="utf-8")
    check("render_daily_digest 默认模型为当前名",
          re.search(rf'DIGEST_MODEL",\s*"{CURRENT}"', dg) is not None)

    # ── 思考模式守卫 ──
    # 官方文档：「思考模式默认打开，且 effort 默认为 high」。思维链与正文共用
    # max_tokens，因此**每个 LLM 调用点都必须显式声明 thinking**，否则短预算调用
    # 会被思维链占满而拿不到正文（翻译脚本 100/300 token 的调用即属此列）。
    llm_files = [
        ".github/scripts/run_daily_router.py",
        ".github/scripts/run_weekly_distill.py",
        ".github/scripts/render_daily_digest.py",
        ".github/scripts/render_xtweets.py",
        ".github/scripts/render_followbuilders.py",
    ]
    for rel in llm_files:
        text = (HERE / rel).read_text(encoding="utf-8")
        # 统计"请求体"数量（每个 "max_tokens" 出现处即一个调用点）
        call_sites = len(re.findall(r'"max_tokens"\s*:', text))
        declared = len(re.findall(r'"thinking"\s*:\s*\{\s*"type"\s*:\s*"(?:disabled|enabled)"\s*\}', text))
        check(f"{rel} 每个 LLM 调用点都显式声明 thinking",
              call_sites > 0 and declared >= call_sites,
              f"{declared}/{call_sites} 个调用点已声明")

    print()
    if FAILURES:
        print(f"✗ {len(FAILURES)} 项未通过: {FAILURES}")
        return 1
    print("✓ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
