#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown 格式规范化自检（wbl-note-extract 专用）。

解决的问题（均来自 HTML -> Markdown 抓取环节）：
  1. 成对加粗被反斜杠转义：到\\*\\*"交付可靠"\\*\\*  -> 到"**交付可靠**"
  2. 加粗定界符紧贴标点，markdown-it 不渲染：是**「终点职级」** -> 是「**终点职级**」
  3. 列表标记重复：- • 文字 -> - 文字；1. 1\\. 文字 -> 1. 文字

用法：
  python md_normalize.py <文件或目录> [...]          # 只体检，不写盘
  python md_normalize.py <文件或目录> [...] --fix    # 体检并原地修复
  python md_normalize.py <文件> --quiet              # 只输出有问题的文件名

范围约定：
  - 跳过 YAML frontmatter、代码块（``` / ~~~ 围栏）与行内代码。
  - 加粗是否可渲染按 CommonMark 的 flanking 规则判（与 markdown-it 实测一致）：
    行首 / 空白 / 标点之后的 `**` 接标点仍可渲染，不必外置。
  - 只处理「成对」转义标记；138\\*\\*\\*1234 这类奇数组转义星号不动。
  - 外置会让引号结构打架的（如 "A"，而非"B" 整体加粗），只报 WARN 交人工。
  - 裸 `• 文字` 行不处理：那是原文自带的符号，渲染正常。
退出码：0 = 无 BLOCK 级问题或已修复；1 = 仅体检且存在 BLOCK 级问题。
"""

import argparse
import os
import re
import sys
import unicodedata

FENCE = re.compile(r"^\s*(```|~~~)")
BOLD_ESC = re.compile(r"\\\*\\\*([^*\n]+?)\\\*\\\*")
BOLD = re.compile(r"\*\*([^*\n]+?)\*\*")
OL_DUP = re.compile(r"^(\s*)(\d+)\\?\.\s+(\d+)\\?\.\s+")
OL_ESC = re.compile(r"^(\s*)(\d+)\\\.\s+")
UL_DUP = re.compile(r"^(\s*)([-*+])\s+([\u2022\u00b7\u25aa\u25e6\u25cf])\s+")
UL_ESC = re.compile(r"^(\s*)\\([-*+])\s+")

PAIRS = {
    '"': '"', "\u201c": "\u201d", "'": "'", "\u2018": "\u2019",
    "\u300a": "\u300b", "\u3008": "\u3009", "\u300c": "\u300d", "\u300e": "\u300f",
    "\u3010": "\u3011", "\uff08": "\uff09", "(": ")", "[": "]", "\u3014": "\u3015",
}


def is_punct(ch):
    """CommonMark 口径：Unicode P* 与 S* 均按标点处理。"""
    if not ch:
        return False
    return unicodedata.category(ch)[0] in ("P", "S")


def left_flanking(prev_ch, first_ch):
    """`**` 能否作为开定界符。"""
    if first_ch.isspace():
        return False
    if not is_punct(first_ch):
        return True
    return prev_ch is None or prev_ch.isspace() or is_punct(prev_ch)


def right_flanking(last_ch, next_ch):
    """`**` 能否作为闭定界符。"""
    if last_ch.isspace():
        return False
    if not is_punct(last_ch):
        return True
    return next_ch is None or next_ch.isspace() or is_punct(next_ch)


def punct_wrap(inner):
    """把「整段被成对标点包裹」拆成 (open, core, close)；不满足返回 None。"""
    if len(inner) < 3:
        return None
    o, c = inner[0], inner[-1]
    if PAIRS.get(o) != c:
        return None
    core = inner[1:-1]
    if not core or core[0].isspace() or core[-1].isspace():
        return None
    if o in core or c in core:
        return None  # 内层还夹着同类标点，外置会搅乱结构
    return o, core, c


def fix_bold_segment(seg, prev_char, next_char, issues, lineno):
    """处理一段非行内代码文本里的加粗写法。

    定界符只要有一侧贴着标点就可能不渲染，做法是把该侧标点逐个剥到
    `**` 外面，直到两侧都满足 flanking。剥离只动标点、不动文字，
    视觉上的加粗范围几乎不变。
    """

    def rebuild(m):
        core = m.group(1)
        left = ""
        right = ""
        prev_ch = seg[m.start() - 1] if m.start() > 0 else prev_char
        next_ch = seg[m.end()] if m.end() < len(seg) else next_char

        # 加粗内侧的首尾空格会让定界符失效，先挪到外面
        while len(core) > 1 and core[0] == " ":
            left += " "
            core = core[1:]
        while len(core) > 1 and core[-1] == " ":
            right = " " + right
            core = core[:-1]

        for _ in range(4):
            if len(core) < 3:
                break
            ok_l = left_flanking(left[-1] if left else prev_ch, core[0])
            ok_r = right_flanking(core[-1], right[0] if right else next_ch)
            if ok_l and ok_r:
                break
            changed = False
            # 整段被成对标点包裹时，标点要成对挪出去，否则引号会被截断在加粗内
            if len(core) > 4 and core[0] in PAIRS and core[-1] == PAIRS[core[0]]:
                left += core[0]
                right = core[-1] + right
                core = core[1:-1]
                changed = True
            else:
                if not ok_l and is_punct(core[0]) and len(core) > 3:
                    left += core[0]
                    core = core[1:]
                    changed = True
                if not ok_r and is_punct(core[-1]) and len(core) > 3:
                    right = core[-1] + right
                    core = core[:-1]
                    changed = True
            if not changed:
                break

        if len(core) >= 1 and left_flanking(left[-1] if left else prev_ch, core[0]) \
                and right_flanking(core[-1], right[0] if right else next_ch):
            return "%s**%s**%s" % (left, core, right)

        issues.append((lineno, "warn", m.group(0),
                       "加粗边界贴标点且无法自动外置，需人工改写"))
        return m.group(0)

    if "\\*\\*" in seg:
        seg = BOLD_ESC.sub(rebuild, seg)
    if "**" in seg:
        seg = BOLD.sub(rebuild, seg)
    return seg


def split_inline_code(line):
    """按行内代码切片，返回 [(is_code, text)]。"""
    parts = re.split(r"(`[^`]*`)", line)
    return [(bool(p.startswith("`") and p.endswith("`") and len(p) > 1), p)
            for p in parts if p != ""]


def normalize_line(line, issues, lineno):
    orig = line

    if UL_DUP.match(line):
        line = UL_DUP.sub(r"\1\2 ", line)
    elif UL_ESC.match(line):
        line = UL_ESC.sub(r"\1\2 ", line)

    if OL_DUP.match(line):
        line = OL_DUP.sub(r"\1\3. ", line)
    elif OL_ESC.match(line):
        line = OL_ESC.sub(r"\1\2. ", line)

    pieces = split_inline_code(line)
    # 用不含星号的占位符顶替行内代码，避免两段星号被拼接成假堆叠
    body_txt = "".join("·" if is_code else p for is_code, p in pieces)
    # 3 个以上连续星号是抓取时星号翻倍的畸形产物，动了只会更乱，整行跳过并交人工
    skip_bold = bool(re.search(r"\*{4,}", body_txt))
    if skip_bold:
        issues.append((lineno, "warn", line.rstrip("\r\n"),
                       "4 个以上连续星号，疑似抓取时定界符翻倍，需人工确认"))
    rebuilt = []
    prev_char = None
    for i, (is_code, text) in enumerate(pieces):
        if is_code or skip_bold:
            rebuilt.append(text)
        else:
            nxt = None
            if i + 1 < len(pieces):
                nxt = pieces[i + 1][1][:1] or None
            rebuilt.append(fix_bold_segment(text, prev_char, nxt, issues, lineno))
        prev_char = text[-1] if text else prev_char
    line = "".join(rebuilt)

    if line != orig:
        kind = "list-marker" if (UL_DUP.match(orig) or UL_ESC.match(orig)
                                 or OL_DUP.match(orig) or OL_ESC.match(orig)) else "bold"
        issues.append((lineno, kind, orig.rstrip("\r\n"), line.rstrip("\r\n")))

    # 成对转义标记落单：`\*\*` 出现奇数次，必有一侧没有配对。
    # 这类是抓取时丢了半边定界符，脚本不猜语义，报 WARN 交人工。
    # 先剔除 3 个以上连续转义星（138\*\*\*1234 这类脱敏、遮蔽写法），它是正常内容。
    body = "".join("·" if is_code else p for is_code, p in split_inline_code(line))
    lone = re.sub(r"(?:\\\*){3,}", "", body)
    if len(re.findall(r"\\\*\\\*", lone)) % 2:
        issues.append((lineno, "warn", line.rstrip("\r\n"),
                       "转义加粗标记落单，需人工补全或删除"))

    return line


def normalize_text(text, fname="", quiet=False):
    lines = text.splitlines(keepends=True)
    issues = []
    out = []
    in_fence = False
    in_yaml = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if i == 1 and stripped == "---":
            in_yaml = True
            out.append(line)
            continue
        if in_yaml:
            if stripped == "---":
                in_yaml = False
            out.append(line)
            continue
        if FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        out.append(normalize_line(line, issues, i))

    new_text = "".join(out)
    if issues and not quiet:
        print("\n== %s ==" % (fname or "(stdin)"))
        for lineno, kind, before, after in issues:
            level = "WARN " if kind == "warn" else "BLOCK"
            print("  [%s] L%-5d %-12s %s" % (level, lineno, kind, before.strip()[:80]))
            print("            -> %s" % after.strip()[:80])
    return new_text, issues


def iter_targets(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    if f.lower().endswith(".md"):
                        yield os.path.join(root, f)
        elif p.lower().endswith(".md"):
            yield p


def main():
    ap = argparse.ArgumentParser(description="Markdown 格式规范化自检")
    ap.add_argument("targets", nargs="+", help="文件或目录")
    ap.add_argument("--fix", action="store_true", help="原地修复")
    ap.add_argument("--quiet", action="store_true", help="只输出有问题的文件名")
    args = ap.parse_args()

    total_files = 0
    bad_files = 0
    total_block = 0
    total_warn = 0

    for path in iter_targets(args.targets):
        if not os.path.isfile(path):
            print("跳过（不存在）：%s" % path, file=sys.stderr)
            continue
        total_files += 1
        with open(path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        new_text, issues = normalize_text(text, os.path.basename(path), args.quiet)
        if not issues:
            continue
        bad_files += 1
        n_block = sum(1 for x in issues if x[1] != "warn")
        n_warn = len(issues) - n_block
        total_block += n_block
        total_warn += n_warn
        if args.quiet:
            print("%s  (%d 处需修 / %d 处待人工)" % (path, n_block, n_warn))
        if args.fix and new_text != text:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new_text)
            if not args.quiet:
                print("  已修复并写回：%s" % path)

    print("\n汇总：扫描 %d 个文件，%d 个有问题；可自动修 %d 处，待人工确认 %d 处%s" % (
        total_files, bad_files, total_block, total_warn,
        "（已写盘）" if args.fix else "（未写盘）"))
    return 0 if (args.fix or total_block == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
