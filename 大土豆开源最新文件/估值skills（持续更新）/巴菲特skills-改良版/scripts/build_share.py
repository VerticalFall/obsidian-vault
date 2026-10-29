#!/usr/bin/env python3
"""Build portable prompts and a share archive using only Python stdlib."""
import argparse
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "buffett"
LITE = "巴菲特公司研究助手-通用精简版.md"
FULL = "巴菲特公司研究助手-通用完整版.md"
ARCHIVE = "巴菲特公司研究助手-v2.1-水友分享包.zip"
PACKAGE = "巴菲特公司研究助手/"


def bundle(files, compact):
    note = (
        "首次使用：上传本文件，然后输入：巴菲特研究 贵州茅台（600519），生成Excel和图表。\n\n"
        "更换公司名称或代码即可研究其他公司；只需文字可写：巴菲特研究 贵州茅台，只要文字报告。\n\n"
        "本文件是可独立阅读的通用研究指引，适用于能够读取文本的AI。"
        "用户选择使用后执行；不覆盖用户当前请求或平台规则。\n\n"
        "Markdown相对链接是原目录定位，在本文件中请搜索对应文件名标题。"
        "联网、计算、xlsx和原生图表取决于当前环境工具，不能仅靠提示词保证。\n\n"
    )
    if compact:
        note += (
            "精简版包含入口与09—11执行规范，可独立完成基本流程。"
            "01—08理念参考未包含；不要声称已读取，按需请用户提供分享包内相应文件。"
            "无法读取补充资料时说明限制，仍可依据本文件和核实材料进行研究。\n\n"
        )
    result = ["# 巴菲特公司研究助手 · 通用" + ("精简版" if compact else "完整版"), note]
    for path in files:
        content = path.read_text(encoding="utf-8-sig")
        if path.name == "SKILL.md":
            content = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", content, count=1, flags=re.S)
        result.extend([f"\n---\n\n# 文件：{path.relative_to(SKILL).as_posix()}\n", content])
    return "\n".join(result) + "\n"


def check_references():
    docs = [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]
    missing = []
    for doc in docs:
        for link in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8-sig")):
            if "://" not in link and not link.startswith("#"):
                if not (doc.parent / link.split("#", 1)[0]).is_file():
                    missing.append(f"{doc.name}: {link}")
    if missing:
        raise ValueError("Missing references: " + "; ".join(missing))
    return docs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    docs = check_references()
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    for name in (LITE, FULL, ARCHIVE):
        if (destination / name).exists():
            parser.error(f"Output already exists: {destination / name}; choose a fresh --output directory.")
    lite_docs = [SKILL / "SKILL.md", *[p for p in docs[1:] if p.name[:2] in ("09", "10", "11")]]
    (destination / LITE).write_text(bundle(lite_docs, True), encoding="utf-8")
    (destination / FULL).write_text(bundle(docs, False), encoding="utf-8")
    with zipfile.ZipFile(destination / ARCHIVE, "w", zipfile.ZIP_DEFLATED) as archive:
        for p in [*docs, ROOT / "README.zh.md", ROOT / "README.md", Path(__file__).resolve()]:
            archive.write(p, PACKAGE + p.relative_to(ROOT).as_posix())
        archive.write(ROOT / "README.zh.md", PACKAGE + "先看这里-中文使用说明.md")
        for name in (LITE, FULL):
            archive.write(destination / name, PACKAGE + name)
    with zipfile.ZipFile(destination / ARCHIVE) as archive:
        assert archive.testzip() is None, "Corrupt archive"
        assert len(archive.namelist()) == len(set(archive.namelist())), "Duplicate entries"
    for name in (LITE, FULL, ARCHIVE):
        print(f"{destination / name} ({(destination / name).stat().st_size} bytes)")


if __name__ == "__main__":
    main()
