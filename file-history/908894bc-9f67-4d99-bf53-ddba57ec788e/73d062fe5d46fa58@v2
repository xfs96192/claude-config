#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_word.py
更新季报 Word 文档：删除到期产品段落、新增产品段落、更新季度市场描述。

用法：
    python update_word.py <src_docx> <dst_docx> \
        --delete "增盈优选27号" "合享122号" "悦动42号" \
        --add-after-anchor "合享142号：" "合享148号：债券部分采用衰竭式久期..." \
        --quarter-from "四季度" --quarter-to "一季度" \
        --year-from "2025年四季度" --year-to "2026年一季度"

大多数情况下，直接在 Python 中 import 并调用 update_doc() 函数更方便。
"""
import sys
import os
import re
import html
import shutil
import argparse
import subprocess
import tempfile
from pathlib import Path


# ── 编码辅助函数 ─────────────────────────────────────────────────────────────

def decode_xml(raw: str) -> str:
    """将 ASCII 实体编码的 XML 解码为 Unicode 字符串"""
    return html.unescape(raw)


def encode_xml(text: str) -> str:
    """将 Unicode 字符串重新编码为 ASCII 实体（保留 XML 特殊字符）"""
    result = []
    for ch in text:
        if ord(ch) > 127:
            result.append(f'&#{ord(ch)};')
        else:
            result.append(ch)
    return ''.join(result)


def make_para(text: str, indent: str = "420") -> str:
    """生成简单的 Word 段落 XML（Unicode，后续统一编码）"""
    safe = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return (f'\n    <w:p>\n      '
            f'<w:pPr><w:ind w:firstLineChars="200" w:firstLine="{indent}"/></w:pPr>\n      '
            f'<w:r><w:t>{safe}</w:t></w:r>\n    </w:p>')


def make_para_with_font(text: str, font: str = "宋体", size: int = 24,
                        indent: str = "480") -> str:
    """生成带宋体字号的段落（用于 ESG 混合类产品的权益描述）"""
    safe = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    rpr = (f'<w:rPr>'
           f'<w:rFonts w:ascii="{font}" w:eastAsia="{font}" w:hAnsi="{font}" w:cs="{font}"/>'
           f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
           f'</w:rPr>')
    ppr_rpr = rpr
    return (f'\n    <w:p>\n      '
            f'<w:pPr><w:ind w:firstLineChars="200" w:firstLine="{indent}"/>{ppr_rpr}</w:pPr>\n      '
            f'<w:r>{rpr}<w:t>{safe}</w:t></w:r>\n    </w:p>')


# ── 核心操作 ─────────────────────────────────────────────────────────────────

def delete_paragraphs(decoded: str, product_names: list[str]) -> str:
    """删除包含指定产品名的整个 <w:p>...</w:p> 段落"""
    for name in product_names:
        pattern = (r'\n\s*<w:p[^>]*>(?:[^<]|<(?!/?w:p[>\s]))*'
                   + re.escape(name)
                   + r'(?:[^<]|<(?!/?w:p[>\s]))*</w:p>')
        new, count = re.subn(pattern, '', decoded, flags=re.DOTALL)
        if count > 0:
            decoded = new
            print(f"  ✓ 已删除：{name}（{count} 段）")
        else:
            print(f"  ⚠ 未找到：{name}")
    return decoded


def insert_after_para_id(decoded: str, para_id: str, new_paragraphs: list[str]) -> str:
    """在指定 paraId 的段落 </w:p> 后插入新段落（Unicode 文本，最后统一编码）"""
    pos = decoded.find(f'paraId="{para_id}"')
    if pos == -1:
        print(f"  ⚠ 未找到 paraId={para_id}")
        return decoded
    close_pos = decoded.find('</w:p>', pos)
    insert_pt = close_pos + len('</w:p>')
    new_xml = ''.join(make_para(t) for t in new_paragraphs)
    return decoded[:insert_pt] + new_xml + decoded[insert_pt:]


def insert_after_text(decoded: str, anchor_text: str,
                      new_paragraphs: list[str]) -> str:
    """在包含 anchor_text 的段落 </w:p> 后插入新段落"""
    pos = decoded.find(anchor_text)
    if pos == -1:
        print(f"  ⚠ 未找到锚点文本：{anchor_text[:30]}")
        return decoded
    close_pos = decoded.find('</w:p>', pos)
    insert_pt = close_pos + len('</w:p>')
    new_xml = ''.join(make_para(t) for t in new_paragraphs)
    return decoded[:insert_pt] + new_xml + decoded[insert_pt:]


def replace_text(decoded: str, old: str, new: str, count: int = 0) -> str:
    """替换文本（count=0 表示全部替换）"""
    if count:
        result = decoded.replace(old, new, count)
    else:
        result = decoded.replace(old, new)
    n = decoded.count(old)
    if n:
        print(f"  ✓ 替换 {n} 处：{old[:30]!r} → {new[:30]!r}")
    else:
        print(f"  ⚠ 未找到：{old[:40]!r}")
    return result


# ── 主函数 ───────────────────────────────────────────────────────────────────

def update_doc(
    src_docx: str,
    dst_docx: str,
    *,
    # 要删除的产品短名称列表（会匹配段落中的文本）
    delete_products: list[str] = None,
    # 插入：{锚点文本: [新段落文本, ...]} 在锚点后插入
    insert_after: dict[str, list[str]] = None,
    # 插入：{paraId: [新段落文本, ...]} 按 paraId 插入
    insert_after_id: dict[str, list[str]] = None,
    # 全局文本替换列表：[(old, new), ...]
    text_replacements: list[tuple[str, str]] = None,
) -> None:
    """
    更新 Word 季报文档的主函数。
    - 使用 ooxml/scripts/unpack.py 解包
    - 在 decoded XML 上做字符串操作
    - 重新打包为新文件
    """
    # 找到 docx skill 的 unpack/pack 脚本
    skill_root = Path(__file__).parent.parent.parent / 'docx'
    unpack_script = skill_root / 'ooxml/scripts/unpack.py'
    pack_script = skill_root / 'ooxml/scripts/pack.py'

    if not unpack_script.exists():
        raise FileNotFoundError(f"未找到 unpack.py，请确认 docx skill 已安装：{unpack_script}")

    tmp_dir = tempfile.mkdtemp(prefix='quarterly_word_')
    unpacked = os.path.join(tmp_dir, 'unpacked')
    xml_path = os.path.join(tmp_dir, 'unpacked', 'word', 'document.xml')

    try:
        # 解包
        shutil.copy2(src_docx, os.path.join(tmp_dir, 'src.docx'))
        subprocess.run([sys.executable, str(unpack_script),
                        os.path.join(tmp_dir, 'src.docx'), unpacked],
                       check=True, capture_output=True)

        with open(xml_path, 'r', encoding='ascii') as f:
            raw = f.read()

        decoded = decode_xml(raw)

        # 1. 删除产品段落
        if delete_products:
            print("\n[删除产品]")
            decoded = delete_paragraphs(decoded, delete_products)

        # 2. 全局文本替换
        if text_replacements:
            print("\n[文本替换]")
            for old, new in text_replacements:
                decoded = replace_text(decoded, old, new)

        # 3. 在锚点文本后插入
        if insert_after:
            print("\n[插入段落-文本锚点]")
            for anchor, paras in insert_after.items():
                decoded = insert_after_text(decoded, anchor, paras)

        # 4. 在 paraId 后插入
        if insert_after_id:
            print("\n[插入段落-paraId]")
            for pid, paras in insert_after_id.items():
                decoded = insert_after_para_id(decoded, pid, paras)

        # 写回
        with open(xml_path, 'w', encoding='ascii') as f:
            f.write(encode_xml(decoded))

        # 打包
        subprocess.run([sys.executable, str(pack_script), unpacked, dst_docx],
                       check=True, capture_output=True)
        print(f"\n✓ 已生成：{dst_docx}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    # 简单命令行接口（完整用法建议在主脚本中直接调用 update_doc()）
    parser = argparse.ArgumentParser()
    parser.add_argument('src_docx')
    parser.add_argument('dst_docx')
    parser.add_argument('--delete', nargs='*', default=[])
    parser.add_argument('--year-from', default='2025年四季度')
    parser.add_argument('--year-to', default='2026年一季度')
    args = parser.parse_args()

    update_doc(
        args.src_docx,
        args.dst_docx,
        delete_products=args.delete,
        text_replacements=[
            (args.year_from, args.year_to),
        ],
    )
