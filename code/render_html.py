"""
JSON to HTML 渲染器
读取 JSON 数据，生成自包含的 HTML 文件
"""

import argparse
import json
import os
import sys

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_template(template_name: str) -> str:
    """加载模板文件"""
    template_path = os.path.join(SCRIPT_DIR, template_name)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def generate_html(json_data: dict, embed: bool = False) -> str:
    """生成自包含 HTML"""
    # 加载模板
    css = load_template(os.path.join("templates", "default_theme.css"))
    js = load_template(os.path.join("renderer", "renderer.js"))

    # 构建 HTML
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="zh-CN">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'  <title>{json_data.get("metadata", {}).get("title", "Markdown Document")}</title>',
        '  <style>',
        css,
        '  </style>',
        '</head>',
        '<body>',
    ]

    if embed:
        # 内嵌模式：JSON 嵌入到 HTML 中
        json_str = json.dumps(json_data, ensure_ascii=False)
        html_parts.append(f'  <script type="application/json" id="md-data">{json_str}</script>')
    else:
        # 外链模式：通过 data-json 属性指定路径
        html_parts.append('  <div id="app"></div>')

    html_parts.append('  <script>')
    html_parts.append(js)
    html_parts.append('  </script>')
    html_parts.append('</body>')
    html_parts.append('</html>')

    return "\n".join(html_parts)


def render_html(json_path: str, html_path: str, embed: bool = False) -> str:
    """将 JSON 文件渲染为 HTML"""
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    html = generate_html(json_data, embed=embed)

    os.makedirs(os.path.dirname(os.path.abspath(html_path)), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    return html


def main():
    parser = argparse.ArgumentParser(description="将 JSON 数据渲染为自包含 HTML 文件")
    parser.add_argument("input", help="输入的 .json 文件路径")
    parser.add_argument("-o", "--output", help="输出的 .html 文件路径（默认与输入同名 .html）")
    parser.add_argument("--embed", action="store_true", help="将 JSON 内嵌到 HTML 中（生成单文件）")
    args = parser.parse_args()

    json_path = args.input
    if args.output:
        html_path = args.output
    else:
        html_path = os.path.splitext(json_path)[0] + ".html"

    render_html(json_path, html_path, embed=args.embed)
    mode = "内嵌模式" if args.embed else "外链模式"
    print(f"✓ 已渲染: {json_path} → {html_path} ({mode})")


if __name__ == "__main__":
    main()
