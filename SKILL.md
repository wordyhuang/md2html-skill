---
name: "md2htmlSkill"
description: "Convert any Markdown file to a beautifully rendered HTML page. Invoke when user wants to convert MD to HTML, preview a markdown file, or view a .md document in browser."
---

# md2htmlSkill

将任意 Markdown 文件转换为浏览器可查看的 HTML 页面。

## 工作流程（内嵌模式，无需 HTTP 服务器）

1. **读取 MD 文件**：确认用户提供的 `.md` 文件路径
2. **转换为 JSON**：运行 `python code/md_to_json.py <md文件> -o output/<文件名>.json`
   - 依赖：`markdown-it-py`、`pyyaml`
   - JSON 输出到：`output/`
3. **生成自包含 HTML**：运行 `python code/render_html.py output/<文件名>.json -o output/<文件名>.html --embed`
   - `--embed` 参数将 JSON 数据内嵌到 HTML 中，生成单文件
   - 输出 HTML 也保存到：`output/`
4. **发送给用户**：通过 OpenPreview 发送 `computer://` 链接给用户查看，不要自动打开浏览器

## 关键规则

- md_to_json.py 路径：`code/md_to_json.py`
- render_html.py 路径：`code/render_html.py`
- 输出目录：`output/`
- 默认使用 `--embed` 内嵌模式，生成单文件 HTML，无需 HTTP 服务器
- 每次运行前检查 output 目录是否存在，不存在则创建
