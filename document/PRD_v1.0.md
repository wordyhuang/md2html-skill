# MD to HTML Skill — 产品需求规格说明书

| 属性       | 内容                           |
| ---------- | ------------------------------ |
| 创建时间   | 2025-07-10 19:22:00            |
| 最后修改   | 2025-07-10 19:22:00            |
| 当前版本   | V_1.0                          |
| 适用对象   | 开发团队                       |
| 核心目标   | 将 Markdown 文件转换为自包含的可视化 HTML 页面 |
| 简要描述   | 两阶段管道：MD → JSON（机器中间态）→ HTML（浏览器直接渲染，内置默认样式） |

---

## 1. 项目概述

### 1.1 背景

需要一个工具，将 Markdown 文档转化为人类友好、浏览器可直接查看的 HTML 页面。转化过程分为两个阶段，中间通过 JSON 格式传递结构化数据。

### 1.2 核心价值

- **MD 只存数据**：Markdown 文件作为纯数据源，不含任何渲染逻辑
- **JSON 作为桥梁**：机器可读的中间态，方便后续扩展（如搜索、索引、二次加工）
- **HTML 负责呈现**：自包含页面，浏览器直接打开，零外部依赖，内置美观样式

---

## 2. 架构设计

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│   MD 文件    │ ──→ │ Python 解析器     │ ──→ │ JSON（机器中间态）     │
│  (数据源)    │     │ md_to_json.py    │     │ 结构化 AST            │
└─────────────┘     └──────────────────┘     └──────────┬───────────┘
                                                       │
                                                       ▼
                                              ┌──────────────────────┐
                                              │ HTML 渲染器            │
                                              │ render_html.py        │
                                              │ (生成自包含 HTML 文件)  │
                                              └──────────┬───────────┘
                                                         │
                                                         ▼
                                              ┌──────────────────────┐
                                              │ HTML 文件              │
                                              │ (浏览器直接打开渲染)    │
                                              └──────────────────────┘
```

### 2.1 阶段一：MD → JSON

- **输入**：任意 `.md` 文件（支持 YAML front matter）
- **输出**：结构化 JSON 文件
- **工具**：`markdown-it-py`（功能全面，支持 GFM 扩展，AST 友好）

### 2.2 阶段二：JSON → HTML

- **输入**：阶段一输出的 JSON 文件
- **输出**：自包含 `.html` 文件（内嵌 JS 渲染器 + 默认 CSS）
- **渲染方式**：HTML 内嵌 JS，浏览器加载时 JS 读取同目录下的 JSON 并动态渲染 DOM
- **样式**：内置一套默认 CSS 主题，开箱即用

---

## 3. JSON 结构规范

JSON 是纯机器接口，不需要人类可读。追求结构清晰、解析高效。

```jsonc
{
  "version": "1.0",
  "metadata": {
    "title": "文档标题",
    "author": "作者",
    "created": "2025-07-10",
    "modified": "2025-07-10"
  },
  "toc": [
    { "id": "section-1", "level": 1, "text": "一级标题" },
    { "id": "section-1-1", "level": 2, "text": "二级标题" }
  ],
  "blocks": [
    {
      "type": "heading",
      "level": 1,
      "text": "标题",
      "id": "section-1"
    },
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "content": "普通文本 " },
        { "type": "strong", "content": "加粗" },
        { "type": "em", "content": "斜体" },
        { "type": "link", "href": "url", "content": "链接文字" },
        { "type": "code_inline", "content": "行内代码" },
        { "type": "image", "src": "path", "alt": "描述", "title": "标题" }
      ]
    },
    {
      "type": "code_block",
      "lang": "python",
      "content": "print('hello')"
    },
    {
      "type": "table",
      "header": ["列1", "列2"],
      "rows": [["值1", "值2"], ["值3", "值4"]],
      "align": ["left", "right"]
    },
    {
      "type": "list",
      "ordered": false,
      "items": [
        { "type": "list_item", "content": [...], "items": [...] }
      ]
    },
    {
      "type": "blockquote",
      "content": [...]
    },
    {
      "type": "hr"
    },
    {
      "type": "task_list",
      "items": [
        { "checked": true, "content": [...] },
        { "checked": false, "content": [...] }
      ]
    },
    {
      "type": "math_block",
      "content": "E = mc^2"
    }
  ]
}
```

### 3.1 支持的块类型

| 块类型          | type 值       | 说明                   |
| --------------- | ------------- | ---------------------- |
| 标题            | heading       | level 1-6              |
| 段落            | paragraph     | 内含行内元素            |
| 代码块          | code_block    | 支持语言标记           |
| 表格            | table         | 含表头、行、对齐方式    |
| 无序列表        | list          | 支持嵌套               |
| 有序列表        | list          | ordered: true          |
| 任务列表        | task_list     | GFM 扩展               |
| 引用块          | blockquote    | 支持嵌套               |
| 水平线          | hr            | —                      |
| 数学公式块      | math_block    | —                      |
| 图片            | image         | 独立段落级图片          |

### 3.2 支持的行内元素

| 行内类型        | type 值          | 说明               |
| --------------- | ---------------- | ------------------ |
| 纯文本          | text             | —                  |
| 加粗            | strong           | **bold**           |
| 斜体            | em               | *italic*           |
| 删除线          | strikethrough    | ~~strike~~ (GFM)   |
| 行内代码        | code_inline      | `code`             |
| 链接            | link             | [text](url)        |
| 图片            | image            | ![alt](src)        |
| 数学公式        | math_inline      | $formula$          |
| 换行            | softbreak / hardbreak | —            |

---

## 4. HTML 渲染规范

### 4.1 自包含要求

- HTML 文件必须能**浏览器直接打开**渲染，不依赖外部资源
- JSON 数据通过以下方式加载：
  - **默认方式**：JSON 文件与 HTML 同目录，HTML 内 `<script>` 标签用 `fetch` 加载同目录 JSON
  - **备选方式**：支持将 JSON 内嵌到 HTML 的 `<script type="application/json" id="md-data">` 标签中，实现真正的单文件输出
- CSS 样式内置在 `<style>` 标签中
- JS 渲染逻辑内置在 `<script>` 标签中

### 4.2 内置默认样式

- 排版清晰、间距舒适、适合长文阅读
- 支持代码块语法高亮（轻量方案，不依赖外部库）
- 支持表格、任务列表、数学公式的样式
- 支持响应式布局（桌面/移动端）
- 支持目录（TOC）侧边栏或顶部导航
- 提供浅色/深色主题切换（可选，作为加分项）

### 4.3 渲染流程

```
页面加载 → 读取 JSON 数据 → 遍历 blocks 数组 → 根据每个块的 type 动态生成 DOM → 插入页面容器
```

---

## 5. Python 程序规范

### 5.1 md_to_json.py

- **功能**：读取 `.md` 文件，输出 `.json` 文件
- **依赖**：`markdown-it-py` + `pyyaml`（解析 front matter）
- **CLI 用法**：

```bash
python md_to_json.py input.md -o output.json
```

- **特性**：
  - 解析 YAML front matter → 填充 `metadata`
  - 解析 MD 正文 → 生成 `toc` 和 `blocks`
  - 支持 GFM 扩展（表格、任务列表、删除线）
  - 支持数学公式（KaTeX 风格 `$...$` 和 `$$...$$`）

### 5.2 render_html.py

- **功能**：读取 `.json` 文件，输出 `.html` 文件
- **CLI 用法**：

```bash
python render_html.py data.json -o output.html [--embed] [--theme default]
```

- **参数**：
  - `--embed`：将 JSON 内嵌到 HTML 中，生成真正的单文件
  - `--theme`：指定 CSS 主题（默认 `default`，后续可扩展）
- **特性**：
  - 生成自包含 HTML（含 JS 渲染器 + CSS 样式）
  - JSON 数据可外链或内嵌
  - 支持 GFM 表格、任务列表、代码高亮、数学公式的渲染

---

## 6. 目录结构

```
MD to HTML Skill/
├── document/                # 方案与需求文档
│   └── PRD_v1.0.md
├── code/                    # 源代码
│   ├── md_to_json.py        # MD → JSON 解析器
│   ├── render_html.py       # JSON → HTML 渲染器
│   ├── templates/
│   │   └── default_theme.css # 默认 CSS 样式
│   ├── renderer/
│   │   └── renderer.js       # 内嵌 JS 渲染器模板
│   └── requirements.txt     # Python 依赖
├── temp/                    # 临时文件
├── log/                     # 日志文件
├── output/                  # 输出文件
└── README.md                # 项目说明
```

---

## 7. 验收标准

| # | 验收项                                       | 通过条件                           |
|---|---------------------------------------------|-----------------------------------|
| 1 | 基础语法转换                                  | 标题、段落、加粗、斜体、链接、行内代码、列表、代码块、引用、水平线均正确渲染 |
| 2 | GFM 扩展语法                                 | 表格、任务列表、删除线正确渲染      |
| 3 | YAML front matter                           | 标题、作者、日期等元数据正确解析到 JSON metadata 中 |
| 4 | 目录（TOC）                                  | 自动生成，层级关系正确，点击可跳转  |
| 5 | 自包含 HTML                                  | 浏览器直接打开，无外部依赖，样式正常 |
| 6 | JSON 内嵌模式（--embed）                     | 生成单文件 HTML，不依赖外部 JSON   |
| 7 | 代码块语法高亮                               | 不同语言有对应的颜色区分            |
| 8 | 数学公式                                     | 行内公式和公式块正确渲染           |
| 9 | 响应式布局                                   | 桌面端和移动端均可正常阅读         |
| 10 | 复杂嵌套文档                                 | 三级列表、嵌套引用、表格内含代码等复杂场景正确渲染 |

---

## 8. 版本记录

| 版本   | 日期         | 变更说明                                     |
| ------ | ------------ | -------------------------------------------- |
| V_1.0  | 2025-07-10   | 初始版本，定义两阶段管道架构和全部功能规范    |
