"""
MD to JSON 解析器
将 Markdown 文件解析为结构化 JSON（机器中间态）
"""

import argparse
import json
import re
import sys

import yaml
from markdown_it import MarkdownIt


def parse_front_matter(text: str) -> tuple[dict, str]:
    """解析 YAML front matter，返回 (metadata, body_text)"""
    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = pattern.match(text)
    if match:
        try:
            metadata = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            metadata = {}
        body = text[match.end():]
    else:
        metadata = {}
        body = text
    return metadata, body


def slugify(text: str) -> str:
    """生成 URL 友好的锚点 ID"""
    text = text.strip().lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def convert_inline_tokens(tokens: list) -> list:
    """将 markdown-it 行内 token 转换为 JSON 行内元素"""
    elements = []
    for token in tokens:
        if token.type == "text":
            content = token.content
            if not content:
                continue
            # 检查子 token（如 softbreak）
            if token.children:
                elements.extend(convert_inline_tokens(token.children))
            else:
                elements.append({"type": "text", "content": content})

        elif token.type == "softbreak":
            elements.append({"type": "softbreak"})

        elif token.type == "hardbreak":
            elements.append({"type": "hardbreak"})

        elif token.type == "strong_open":
            pass  # 闭合标记，由子节点处理

        elif token.type == "strong_close":
            pass

        elif token.type == "em_open":
            pass

        elif token.type == "em_close":
            pass

        elif token.type == "s_open":
            pass

        elif token.type == "s_close":
            pass

        elif token.type == "code_inline":
            elements.append({"type": "code_inline", "content": token.content})

        elif token.type == "link_open":
            href = token.attrGet("href") or ""
            title = token.attrGet("title") or ""
            # 收集 link_open 到 link_close 之间的内容
            # 这里由父级处理

        elif token.type == "image":
            src = token.attrGet("src") or ""
            alt = token.content or ""
            title = token.attrGet("title") or ""
            elements.append({"type": "image", "src": src, "alt": alt, "title": title})

        elif token.type == "html_inline":
            # 数学公式 $...$ 可能被解析为 html_inline
            content = token.content.strip()
            if content.startswith("$") and content.endswith("$") and len(content) > 1:
                formula = content[1:-1]
                elements.append({"type": "math_inline", "content": formula})
            else:
                elements.append({"type": "raw_html", "content": content})

        else:
            # 递归处理子节点
            if token.children:
                elements.extend(convert_inline_tokens(token.children))
    return elements


def convert_inline_with_marks(tokens: list) -> list:
    """将行内 token 转换为带标记的元素（处理 strong/em/strikethrough 嵌套）"""
    stack = []  # 标记栈: [(type, elements), ...]
    result = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token.type == "strong_open":
            stack.append(("strong", []))
            i += 1
        elif token.type == "strong_close":
            if stack and stack[-1][0] == "strong":
                _, children = stack.pop()
                element = {"type": "strong", "content": children}
                if stack:
                    stack[-1][1].append(element)
                else:
                    result.append(element)
            i += 1
        elif token.type == "em_open":
            stack.append(("em", []))
            i += 1
        elif token.type == "em_close":
            if stack and stack[-1][0] == "em":
                _, children = stack.pop()
                element = {"type": "em", "content": children}
                if stack:
                    stack[-1][1].append(element)
                else:
                    result.append(element)
            i += 1
        elif token.type == "s_open":
            stack.append(("strikethrough", []))
            i += 1
        elif token.type == "s_close":
            if stack and stack[-1][0] == "strikethrough":
                _, children = stack.pop()
                element = {"type": "strikethrough", "content": children}
                if stack:
                    stack[-1][1].append(element)
                else:
                    result.append(element)
            i += 1
        elif token.type == "link_open":
            href = token.attrGet("href") or ""
            title = token.attrGet("title") or ""
            stack.append(("link", [], href, title))
            i += 1
        elif token.type == "link_close":
            if stack and stack[-1][0] == "link":
                _, children, href, title = stack.pop()
                element = {"type": "link", "href": href, "title": title, "content": children}
                if stack:
                    stack[-1][1].append(element)
                else:
                    result.append(element)
            i += 1
        elif token.type == "text":
            content = token.content
            if token.children:
                child_elements = convert_inline_with_marks(token.children)
                if content:
                    result_or_stack = child_elements
                else:
                    result_or_stack = child_elements
                for elem in result_or_stack:
                    if stack:
                        stack[-1][1].append(elem)
                    else:
                        result.append(elem)
            else:
                if content:
                    element = {"type": "text", "content": content}
                    if stack:
                        stack[-1][1].append(element)
                    else:
                        result.append(element)
            i += 1
        elif token.type == "softbreak":
            element = {"type": "softbreak"}
            if stack:
                stack[-1][1].append(element)
            else:
                result.append(element)
            i += 1
        elif token.type == "hardbreak":
            element = {"type": "hardbreak"}
            if stack:
                stack[-1][1].append(element)
            else:
                result.append(element)
            i += 1
        elif token.type == "code_inline":
            element = {"type": "code_inline", "content": token.content}
            if stack:
                stack[-1][1].append(element)
            else:
                result.append(element)
            i += 1
        elif token.type == "image":
            src = token.attrGet("src") or ""
            alt = token.content or ""
            title = token.attrGet("title") or ""
            element = {"type": "image", "src": src, "alt": alt, "title": title}
            if stack:
                stack[-1][1].append(element)
            else:
                result.append(element)
            i += 1
        elif token.type == "html_inline":
            content = token.content.strip()
            if content.startswith("$") and content.endswith("$") and len(content) > 1:
                formula = content[1:-1]
                element = {"type": "math_inline", "content": formula}
                if stack:
                    stack[-1][1].append(element)
                else:
                    result.append(element)
            i += 1
        else:
            i += 1

    return result


def convert_block_tokens(tokens: list) -> tuple[list, list]:
    """将 markdown-it 块级 token 转换为 JSON blocks 和 toc"""
    blocks = []
    toc = []
    i = 0

    while i < len(tokens):
        token = tokens[i]
        nesting = token.nesting

        # 跳过打开/关闭标记（在 block 级别大部分不需要）
        if token.type == "heading_open":
            level = int(token.tag[1])  # h1 -> 1
            # 收集到 heading_close 之间的内容
            heading_tokens = []
            i += 1
            while i < len(tokens) and tokens[i].type != "heading_close":
                heading_tokens.append(tokens[i])
                i += 1
            # 提取文本：优先从 inline token 的 children 中取，否则直接取 content
            text_parts = []
            for t in heading_tokens:
                if t.type == "inline" and t.children:
                    for c in t.children:
                        if c.content:
                            text_parts.append(c.content)
                elif t.type == "text" and t.content:
                    text_parts.append(t.content)
            text = "".join(text_parts)
            # 生成 ID
            section_id = slugify(text)
            # 检查是否有自定义 id
            if token.attrGet("id"):
                section_id = token.attrGet("id")
            blocks.append({
                "type": "heading",
                "level": level,
                "text": text,
                "id": section_id
            })
            toc.append({
                "id": section_id,
                "level": level,
                "text": text
            })
            i += 1  # 跳过 heading_close

        elif token.type == "paragraph_open":
            # 收集段落内容
            inline_tokens = []
            i += 1
            while i < len(tokens) and tokens[i].type != "paragraph_close":
                if tokens[i].children:
                    inline_tokens.extend(tokens[i].children)
                elif tokens[i].content:
                    inline_tokens.append(tokens[i])
                i += 1
            content = convert_inline_with_marks(inline_tokens)
            if content:
                blocks.append({
                    "type": "paragraph",
                    "content": content
                })
            i += 1  # 跳过 paragraph_close

        elif token.type == "code_block" or token.type == "fence":
            lang = token.info.strip() if token.info else ""
            content = token.content
            blocks.append({
                "type": "code_block",
                "lang": lang,
                "content": content
            })
            i += 1

        elif token.type == "bullet_list_open":
            # 解析无序列表
            items = []
            i += 1
            i = parse_list_items(tokens, i, items, ordered=False)
            blocks.append({
                "type": "list",
                "ordered": False,
                "items": items
            })

        elif token.type == "ordered_list_open":
            start = token.attrGet("start") or 1
            items = []
            i += 1
            i = parse_list_items(tokens, i, items, ordered=True)
            blocks.append({
                "type": "list",
                "ordered": True,
                "start": int(start) if start else 1,
                "items": items
            })

        elif token.type == "blockquote_open":
            # 解析引用块
            inner_tokens = []
            depth = 1
            i += 1
            while i < len(tokens) and depth > 0:
                if tokens[i].type == "blockquote_open":
                    depth += 1
                elif tokens[i].type == "blockquote_close":
                    depth -= 1
                    if depth == 0:
                        break
                inner_tokens.append(tokens[i])
                i += 1
            inner_blocks, _ = convert_block_tokens(inner_tokens)
            blocks.append({
                "type": "blockquote",
                "content": inner_blocks
            })
            i += 1

        elif token.type == "table_open":
            # 解析表格
            header = []
            rows = []
            align = []
            i += 1
            while i < len(tokens) and tokens[i].type != "table_close":
                if tokens[i].type == "thead_open":
                    i += 1
                    while i < len(tokens) and tokens[i].type != "thead_close":
                        if tokens[i].type == "tr_open":
                            i += 1
                            while i < len(tokens) and tokens[i].type != "tr_close":
                                if tokens[i].type == "th_open":
                                    cell_align = tokens[i].attrGet("style")
                                    align_val = "left"
                                    if cell_align:
                                        if "text-align:right" in cell_align:
                                            align_val = "right"
                                        elif "text-align:center" in cell_align:
                                            align_val = "center"
                                    align.append(align_val)
                                    i += 1
                                    cell_text = ""
                                    while i < len(tokens) and tokens[i].type != "th_close":
                                        if tokens[i].type == "text":
                                            cell_text = tokens[i].content
                                        elif tokens[i].type == "inline" and tokens[i].children:
                                            cell_text = "".join(
                                                c.content for c in tokens[i].children if c.type == "text"
                                            )
                                        i += 1
                                    header.append(cell_text.strip())
                                    i += 1
                                else:
                                    i += 1
                            i += 1
                        else:
                            i += 1
                    i += 1

                elif tokens[i].type == "tbody_open":
                    i += 1
                    while i < len(tokens) and tokens[i].type != "tbody_close":
                        if tokens[i].type == "tr_open":
                            row = []
                            i += 1
                            while i < len(tokens) and tokens[i].type != "tr_close":
                                if tokens[i].type == "td_open":
                                    i += 1
                                    cell_text = ""
                                    while i < len(tokens) and tokens[i].type != "td_close":
                                        if tokens[i].type == "text":
                                            cell_text = tokens[i].content
                                        elif tokens[i].type == "inline" and tokens[i].children:
                                            cell_text = "".join(
                                                c.content for c in tokens[i].children if c.type == "text"
                                            )
                                        i += 1
                                    row.append(cell_text.strip())
                                    i += 1
                                else:
                                    i += 1
                            rows.append(row)
                            i += 1
                        else:
                            i += 1
                    i += 1
                else:
                    i += 1

            blocks.append({
                "type": "table",
                "header": header,
                "rows": rows,
                "align": align
            })
            i += 1

        elif token.type == "hr":
            blocks.append({"type": "hr"})
            i += 1

        elif token.type == "html_block":
            content = token.content.strip()
            # 检查是否为数学公式块 $$...$$
            if content.startswith("$$") and content.endswith("$$"):
                formula = content[2:-2].strip()
                blocks.append({
                    "type": "math_block",
                    "content": formula
                })
            else:
                blocks.append({
                    "type": "raw_html_block",
                    "content": content
                })
            i += 1

        else:
            i += 1

    return blocks, toc


def parse_list_items(tokens: list, i: int, items: list, ordered: bool) -> int:
    """递归解析列表项"""
    while i < len(tokens):
        token = tokens[i]

        if (ordered and token.type == "ordered_list_close") or \
           (not ordered and token.type == "bullet_list_close"):
            i += 1
            break

        if token.type == "list_item_open":
            item = {"content": [], "items": []}
            # 检查是否为任务列表项
            is_task = False
            checked = False
            i += 1

            # 收集 inline 内容
            while i < len(tokens) and tokens[i].type != "list_item_close":
                # 检查是否有 checkbox
                if tokens[i].type == "html_inline":
                    check_match = re.match(
                        r'<input\s+type="checkbox"\s+disabled\s+(checked)?\s*/?>',
                        tokens[i].content.strip()
                    )
                    if check_match:
                        is_task = True
                        checked = bool(check_match.group(1))
                        i += 1
                        continue

                if tokens[i].type == "paragraph_open":
                    inline_tokens = []
                    i += 1
                    while i < len(tokens) and tokens[i].type != "paragraph_close":
                        if tokens[i].children:
                            inline_tokens.extend(tokens[i].children)
                        i += 1
                    content = convert_inline_with_marks(inline_tokens)
                    item["content"] = content
                    i += 1

                elif tokens[i].type == "bullet_list_open":
                    sub_items = []
                    i += 1
                    i = parse_list_items(tokens, i, sub_items, ordered=False)
                    item["items"] = sub_items

                elif tokens[i].type == "ordered_list_open":
                    sub_items = []
                    i += 1
                    i = parse_list_items(tokens, i, sub_items, ordered=True)
                    item["items"] = sub_items

                else:
                    i += 1

            if is_task:
                items.append({
                    "type": "task_item",
                    "checked": checked,
                    "content": item["content"],
                    "items": item["items"]
                })
            else:
                item["type"] = "list_item"
                items.append(item)
            i += 1  # skip list_item_close
        else:
            i += 1

    return i


def md_to_json(md_path: str, json_path: str) -> dict:
    """将 MD 文件转换为 JSON 并保存"""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 解析 front matter
    metadata, body = parse_front_matter(text)

    # 用 markdown-it 解析
    md = MarkdownIt("commonmark", {"html": True}).enable("table").enable("strikethrough")
    tokens = md.parse(body)

    # 转换为 JSON 结构
    blocks, toc = convert_block_tokens(tokens)

    result = {
        "version": "1.0",
        "metadata": metadata,
        "toc": toc,
        "blocks": blocks
    }

    # 保存 JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def main():
    parser = argparse.ArgumentParser(description="将 Markdown 文件转换为结构化 JSON")
    parser.add_argument("input", help="输入的 .md 文件路径")
    parser.add_argument("-o", "--output", help="输出的 .json 文件路径（默认与输入同名 .json）")
    args = parser.parse_args()

    import os
    md_path = args.input
    if args.output:
        json_path = args.output
    else:
        json_path = os.path.splitext(md_path)[0] + ".json"

    result = md_to_json(md_path, json_path)
    print(f"✓ 已转换: {md_path} → {json_path}")
    print(f"  元数据字段: {len(result['metadata'])} 个")
    print(f"  TOC 条目: {len(result['toc'])} 个")
    print(f"  内容块: {len(result['blocks'])} 个")


if __name__ == "__main__":
    main()
