<p align="center">
  <a href="#chinese">中文</a> · <a href="#english">English</a>
</p>

---

<a id="chinese"></a>
# md2htmlSkill

<p align="center">
将 Markdown 文件转换为精美的 HTML 页面<br/>
MD → JSON → HTML 两阶段管道，零依赖渲染
</p>

## 功能特性

- **两阶段管道**：MD 文件 → JSON（机器中间态）→ 自包含 HTML
- **零依赖渲染**：生成的 HTML 内嵌 CSS + JS，双击即可在浏览器中查看
- **复杂语法支持**：GFM 表格、删除线、代码块语法高亮、YAML front matter
- **自动目录**：根据标题层级自动生成 TOC，支持点击跳转
- **响应式布局**：桌面端和移动端均可正常阅读

## 架构

```
MD 文件 ──→ md_to_json.py ──→ JSON ──→ render_html.py --embed ──→ 单文件 HTML
              (Python 解析器)         (机器中间态)         (内嵌模式)      (浏览器直接打开)
```

## 快速开始

### 安装依赖

```bash
pip install markdown-it-py pyyaml
```

### 使用方式

```bash
# 第一步：MD 转 JSON
python code/md_to_json.py input.md -o output/input.json

# 第二步：JSON 转自包含 HTML（--embed 内嵌模式）
python code/render_html.py output/input.json -o output/input.html --embed
```

生成的 `output/input.html` 是一个完整的单文件，双击即可在浏览器中查看。

## 项目结构

```
md2htmlSkill/
├── SKILL.md                         # Skill 定义文件
├── code/
│   ├── md_to_json.py                # MD → JSON 解析器
│   ├── render_html.py               # JSON → HTML 生成器
│   ├── viewer.html                  # 通用查看器（URL 参数模式）
│   ├── renderer/renderer.js         # JS 动态渲染器模板
│   ├── templates/default_theme.css  # 默认 CSS 主题
│   └── requirements.txt            # Python 依赖
├── document/
│   └── PRD_v1.0.md                  # 产品需求规格说明书
├── output/                          # 生成的文件（gitignore）
└── README.md
```

## JSON 结构

JSON 是纯机器接口，结构清晰，方便程序读取：

```json
{
  "version": "1.0",
  "metadata": { "title": "...", "author": "..." },
  "toc": [{ "id": "section-1", "level": 1, "text": "标题" }],
  "blocks": [
    { "type": "heading", "level": 1, "text": "...", "id": "..." },
    { "type": "paragraph", "content": [...] },
    { "type": "code_block", "lang": "python", "content": "..." },
    { "type": "table", "header": [...], "rows": [...], "align": [...] },
    { "type": "list", "ordered": false, "items": [...] },
    { "type": "blockquote", "content": [...] }
  ]
}
```

## 支持的语法

| 类型     | 支持项                                         |
| -------- | ---------------------------------------------- |
| 标题     | H1 - H6                                       |
| 行内元素 | 加粗、斜体、删除线、行内代码、链接、图片       |
| 代码块   | 多语言语法高亮（Python/JS/Bash/JSON/HTML/CSS） |
| 表格     | GFM 表格，支持对齐方式                         |
| 列表     | 有序/无序列表，支持嵌套                        |
| 引用     | 引用块，支持嵌套                               |
| 元数据   | YAML front matter（标题、作者、日期）          |
| 其他     | 水平线、自动目录（TOC）                        |

## 许可

MIT

---

<a id="english"></a>
# md2htmlSkill

<p align="center">
Convert Markdown files to beautifully rendered HTML pages<br/>
MD → JSON → HTML two-stage pipeline, zero-dependency rendering
</p>

## Features

- **Two-stage pipeline**: MD file → JSON (machine-intermediate) → Self-contained HTML
- **Zero-dependency rendering**: Generated HTML embeds CSS + JS, open directly in browser
- **Complex syntax support**: GFM tables, strikethrough, code block syntax highlighting, YAML front matter
- **Auto-generated TOC**: Automatically generates table of contents with click-to-jump
- **Responsive layout**: Works on both desktop and mobile

## Architecture

```
MD File ──→ md_to_json.py ──→ JSON ──→ render_html.py --embed ──→ Single HTML File
             (Python Parser)        (Intermediate)          (Embed Mode)     (Open in Browser)
```

## Quick Start

### Install Dependencies

```bash
pip install markdown-it-py pyyaml
```

### Usage

```bash
# Step 1: Convert MD to JSON
python code/md_to_json.py input.md -o output/input.json

# Step 2: Convert JSON to self-contained HTML (--embed mode)
python code/render_html.py output/input.json -o output/input.html --embed
```

The generated `output/input.html` is a complete single file — just double-click to view in browser.

## Project Structure

```
md2htmlSkill/
├── SKILL.md                         # Skill definition
├── code/
│   ├── md_to_json.py                # MD → JSON parser
│   ├── render_html.py               # JSON → HTML generator
│   ├── viewer.html                  # Universal viewer (URL param mode)
│   ├── renderer/renderer.js         # JS dynamic renderer template
│   ├── templates/default_theme.css  # Default CSS theme
│   └── requirements.txt            # Python dependencies
├── document/
│   └── PRD_v1.0.md                  # Product requirements spec
├── output/                          # Generated files (gitignored)
└── README.md
```

## JSON Structure

JSON serves as a machine-readable intermediate format:

```json
{
  "version": "1.0",
  "metadata": { "title": "...", "author": "..." },
  "toc": [{ "id": "section-1", "level": 1, "text": "Heading" }],
  "blocks": [
    { "type": "heading", "level": 1, "text": "...", "id": "..." },
    { "type": "paragraph", "content": [...] },
    { "type": "code_block", "lang": "python", "content": "..." },
    { "type": "table", "header": [...], "rows": [...], "align": [...] },
    { "type": "list", "ordered": false, "items": [...] },
    { "type": "blockquote", "content": [...] }
  ]
}
```

## Supported Syntax

| Type      | Supported                                      |
| --------- | ---------------------------------------------- |
| Headings  | H1 - H6                                        |
| Inline    | Bold, italic, strikethrough, inline code, links, images |
| Code      | Multi-language syntax highlighting (Python/JS/Bash/JSON/HTML/CSS) |
| Tables    | GFM tables with alignment                       |
| Lists     | Ordered/unordered, nested                      |
| Blockquote | Nested blockquotes                              |
| Metadata | YAML front matter (title, author, date)        |
| Other     | Horizontal rules, auto-generated TOC           |

## License

MIT
