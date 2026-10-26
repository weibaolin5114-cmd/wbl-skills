#!/usr/bin/env python3
"""PPTX 可编辑性检查。

用途：确认交付的 .pptx 是「原生可编辑」的——文字是文本框、图形是形状/图表/表格，
而不是把整页版式渲染成图片贴进去。

判定规则：
  ERROR  单张图片占页面面积 >= 阈值（默认 60%）——几乎必然是整页/整块截图
  ERROR  页面无任何文字，但有图片占页面面积 >= 30%
  ERROR  全文总字数低于 total-char-min（默认 20）且存在图片——疑似整册图片化
  WARN   页面无文字（空版式页可忽略）
  WARN   图片面积占比超过 pic-area-warn（默认 35%）

用法：
  python scripts/pptx_editability_check.py <file.pptx>
  python scripts/pptx_editability_check.py <file.pptx> --json

退出码：0 通过（可含 warning）；1 存在 error。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
except ImportError:
    print('缺少依赖：pip install python-pptx')
    sys.exit(2)

try:
    from console_encoding import configure_utf8_stdio
    configure_utf8_stdio()
except Exception:
    pass

PIC = MSO_SHAPE_TYPE.PICTURE
GROUP = MSO_SHAPE_TYPE.GROUP


def _walk(shapes):
    """递归展开组合形状，产出叶子形状。"""
    for sh in shapes:
        if sh.shape_type == GROUP:
            yield from _walk(sh.shapes)
        else:
            yield sh


def _area(sh) -> float:
    try:
        return float(sh.width) * float(sh.height)
    except Exception:
        return 0.0


def check(path: Path, full_bleed: float, pic_area_warn: float, total_char_min: int,
          pic_warn: float):
    prs = Presentation(str(path))
    slide_area = float(prs.slide_width) * float(prs.slide_height)
    rows, errors, warnings = [], [], []
    total_chars = 0

    for idx, slide in enumerate(prs.slides, start=1):
        text_boxes = charts = tables = pics = 0
        chars = 0
        pic_area = 0.0
        biggest = 0.0
        for sh in _walk(slide.shapes):
            if getattr(sh, 'has_chart', False):
                charts += 1
            if getattr(sh, 'has_table', False):
                tables += 1
            if sh.shape_type == PIC:
                pics += 1
                a = _area(sh)
                pic_area += a
                biggest = max(biggest, a / slide_area if slide_area else 0)
            if getattr(sh, 'has_text_frame', False) and sh.text_frame.text.strip():
                text_boxes += 1
                chars += len(sh.text_frame.text.strip())

        total_chars += chars
        pic_ratio = pic_area / slide_area if slide_area else 0.0
        verdict = 'OK'

        if biggest >= full_bleed:
            verdict = 'ERROR'
            errors.append(f'第 {idx} 页存在占页面 {biggest:.0%} 的图片，疑似整页截图')
        elif pics and chars == 0 and pic_ratio >= 0.30:
            verdict = 'ERROR'
            errors.append(f'第 {idx} 页无文字，图片占页面 {pic_ratio:.0%}，文字已被图片化')
        elif chars == 0:
            verdict = 'WARN'
            warnings.append(f'第 {idx} 页无文字')
        elif pic_ratio > pic_area_warn:
            verdict = 'WARN'
            warnings.append(f'第 {idx} 页图片面积占比 {pic_ratio:.0%}')
        elif biggest >= pic_warn:
            verdict = 'WARN'
            warnings.append(f'第 {idx} 页单张图片占页面 {biggest:.0%}，确认它只是素材图而非表格/图表/正文')

        rows.append({
            'page': idx, 'text_boxes': text_boxes, 'chars': chars,
            'charts': charts, 'tables': tables, 'pics': pics,
            'pic_ratio': round(pic_ratio, 3), 'biggest_pic': round(biggest, 3),
            'verdict': verdict,
        })

    if total_chars < total_char_min and len(rows) > 0:
        errors.append(f'全文可提取文字仅 {total_chars} 字，整册疑似图片化')

    return rows, errors, warnings, total_chars


def main() -> int:
    ap = argparse.ArgumentParser(description='检查 PPTX 是否全原生可编辑')
    ap.add_argument('pptx')
    ap.add_argument('--full-bleed', type=float, default=0.60, help='单图面积占比 ERROR 阈值')
    ap.add_argument('--pic-area-warn', type=float, default=0.35, help='页面图片面积占比 WARN 阈值')
    ap.add_argument('--pic-warn', type=float, default=0.25, help='单张图片面积占比 WARN 阈值')
    ap.add_argument('--total-char-min', type=int, default=20, help='全文最少字数')
    ap.add_argument('--json', action='store_true', help='输出 JSON')
    args = ap.parse_args()

    path = Path(args.pptx)
    if not path.exists():
        print(f'文件不存在：{path}')
        return 2

    rows, errors, warnings, total_chars = check(
        path, args.full_bleed, args.pic_area_warn, args.total_char_min, args.pic_warn)

    if args.json:
        print(json.dumps({'file': str(path), 'pages': rows, 'errors': errors,
                          'warnings': warnings, 'total_chars': total_chars},
                         ensure_ascii=False, indent=2))
    else:
        print(f'文件：{path.name}   页数：{len(rows)}   可提取文字：{total_chars} 字')
        print('页码  文本框  字数  图表  表格  图片  图片占比  结论')
        for r in rows:
            print(f"{r['page']:>4}  {r['text_boxes']:>6}  {r['chars']:>4}  "
                  f"{r['charts']:>4}  {r['tables']:>4}  {r['pics']:>4}  "
                  f"{r['pic_ratio']:>7.0%}  {r['verdict']}")
        for w in warnings:
            print(f'WARN  {w}')
        for e in errors:
            print(f'ERROR {e}')
        print('结论：' + ('不通过，存在图片化页面' if errors else '通过，全原生可编辑'))

    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
