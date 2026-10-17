# -*- coding: utf-8 -*-
"""yamlite —— 只服务于本项目的 YAML 子集读写（无第三方依赖）。

支持范围（够用即可，超范围直接报错，不做静默降级）：
    key: value               标量
    key:                     嵌套块（下一层 2 空格缩进）
      sub: value
    key:
      - sub: value           列表套字典
      - sub: value
    标量：双引号字符串 / 裸字符串 / null / true / false / 整数 / 浮点 / 行内 [a, b]

不做的事：多行字符串、锚点、标签、缩进超过 2 空格、注释嵌入值内。
"""
import math


class YamliteError(ValueError):
    pass


def _scalar(tok):
    tok = tok.strip()
    if not tok:
        return ""
    if tok.startswith('"') and tok.endswith('"') and len(tok) >= 2:
        return tok[1:-1].replace('\\"', '"')
    if tok.startswith("'") and tok.endswith("'") and len(tok) >= 2:
        return tok[1:-1]
    low = tok.lower()
    if low in ("null", "none", "~"):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        return [_scalar(x) for x in inner.split(",")] if inner else []
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        v = float(tok)
        return v if not math.isnan(v) else None
    except ValueError:
        pass
    return tok


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def loads(text):
    """解析 YAML 子集为 dict。"""
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise YamliteError("不要用 tab 缩进")
        lines.append(raw.rstrip())
    if not lines:
        return {}

    pos = 0

    def parse_block(base):
        nonlocal pos
        out = {}
        while pos < len(lines):
            line = lines[pos]
            ind = _indent(line)
            if ind < base:
                return out
            if ind > base:
                raise YamliteError(f"缩进异常(第{pos+1}行): {line!r}")
            body = line.strip()
            if body.startswith("- "):
                raise YamliteError(f"此处不该是列表项(第{pos+1}行): {body!r}")
            if ":" not in body:
                raise YamliteError(f"缺少冒号(第{pos+1}行): {body!r}")
            key, _, rest = body.partition(":")
            key = key.strip()
            pos += 1
            rest = rest.strip()
            if rest:
                out[key] = _scalar(rest)
                continue
            # 空值 → 看下一层是列表还是字典
            if pos >= len(lines) or _indent(lines[pos]) <= ind:
                out[key] = None
                continue
            child_ind = _indent(lines[pos])
            if lines[pos].strip().startswith("- "):
                out[key] = parse_list(child_ind)
            else:
                out[key] = parse_block(child_ind)
        return out

    def parse_list(ind):
        nonlocal pos
        items = []
        while pos < len(lines):
            line = lines[pos]
            if _indent(line) != ind or not line.strip().startswith("- "):
                break
            body = line.strip()[2:].strip()
            pos += 1
            if ":" in body:
                k, _, v = body.partition(":")
                item = {}
                if v.strip():
                    item[k.strip()] = _scalar(v)
                else:
                    item[k.strip()] = None
                # 该列表项下继续的键
                while pos < len(lines) and _indent(lines[pos]) > ind:
                    sub = lines[pos].strip()
                    if not sub.startswith("- ") and ":" in sub:
                        sk, _, sv = sub.partition(":")
                        item[sk.strip()] = _scalar(sv) if sv.strip() else None
                        pos += 1
                    else:
                        raise YamliteError(f"列表项内不支持的结构(第{pos+1}行): {sub!r}")
                items.append(item)
            else:
                items.append(_scalar(body))
        return items

    result = parse_block(0)
    if pos != len(lines):
        raise YamliteError(f"未解析完的内容(第{pos+1}行): {lines[pos]!r}")
    return result


def _dump_scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v) if isinstance(v, float) else str(v)
    s = str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{s}"'


def dumps(obj, indent=0):
    """把 dict/list 写成 YAML 子集。"""
    pad = " " * indent
    out = []
    for k, v in obj.items():
        if isinstance(v, dict):
            if not v:
                out.append(f"{pad}{k}: {{}}")
            else:
                out.append(f"{pad}{k}:")
                out.append(dumps(v, indent + 2))
        elif isinstance(v, list):
            if not v:
                out.append(f"{pad}{k}: []")
                continue
            out.append(f"{pad}{k}:")
            for item in v:
                if isinstance(item, dict):
                    first = True
                    for ik, iv in item.items():
                        if isinstance(iv, (dict, list)):
                            raise YamliteError("列表项内不支持嵌套")
                        prefix = f"{pad}  - " if first else f"{pad}    "
                        out.append(f"{prefix}{ik}: {_dump_scalar(iv)}")
                        first = False
                else:
                    out.append(f"{pad}  - {_dump_scalar(item)}")
        else:
            out.append(f"{pad}{k}: {_dump_scalar(v)}")
    return "\n".join(out)


def split_front_matter(text):
    """返回 (front_matter_dict, body_str)。缺 front matter 返回 ({}, text)。"""
    t = text.lstrip("\ufeff")
    if not t.startswith("---"):
        return {}, text
    lines = t.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            end = i
            break
    if end is None:
        raise YamliteError("front matter 没有闭合的 ---")
    fm = loads("\n".join(lines[1:end]))
    body = "\n".join(lines[end + 1:])
    return fm, body


def join_front_matter(fm, body):
    return "---\n" + dumps(fm) + "\n---\n\n" + body.lstrip("\n")


if __name__ == "__main__":
    sample = {
        "claim_id": "20250630-测试-688591-A1",
        "target_price": None,
        "eps_this_year": 1.35,
        "is_head": True,
        "tags": ["半导体", "扎堆"],
        "arguments": [
            {"id": "A1", "type": "需求", "falsify": "2026年报营收增速<20%"},
            {"id": "A2", "type": "价格", "falsify": None},
        ],
        "score": {"reviewed_at": None, "excess": None},
    }
    text = dumps(sample)
    print(text)
    back = loads(text)
    print("\n往返一致:", back == sample)
    if back != sample:
        print("原:", sample)
        print("回:", back)
