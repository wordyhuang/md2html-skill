/**
 * MD to HTML 渲染器
 * 读取 JSON 数据，动态渲染 DOM
 */
(function () {
  "use strict";

  // ========== 行内元素渲染 ==========
  function renderInline(elements) {
    if (!elements || !elements.length) return [];
    return elements.map(function (el) {
      switch (el.type) {
        case "text":
          return document.createTextNode(el.content);

        case "strong":
          var s = document.createElement("strong");
          el.content.forEach(function (c) { s.appendChild(renderInline([c])[0]); });
          return s;

        case "em":
          var em = document.createElement("em");
          el.content.forEach(function (c) { em.appendChild(renderInline([c])[0]); });
          return em;

        case "strikethrough":
          var del = document.createElement("del");
          el.content.forEach(function (c) { del.appendChild(renderInline([c])[0]); });
          return del;

        case "code_inline":
          var code = document.createElement("code");
          code.className = "inline-code";
          code.textContent = el.content;
          return code;

        case "link":
          var a = document.createElement("a");
          a.href = el.href;
          if (el.title) a.title = el.title;
          el.content.forEach(function (c) { a.appendChild(renderInline([c])[0]); });
          return a;

        case "image":
          var img = document.createElement("img");
          img.src = el.src;
          img.alt = el.alt || "";
          if (el.title) img.title = el.title;
          img.className = "inline-image";
          return img;

        case "math_inline":
          var span = document.createElement("span");
          span.className = "math-inline";
          span.textContent = el.content;
          return span;

        case "softbreak":
          return document.createElement("br");

        case "hardbreak":
          var br = document.createElement("br");
          br.className = "hardbreak";
          return br;

        default:
          return document.createTextNode("");
      }
    });
  }

  function appendInline(parent, elements) {
    renderInline(elements).forEach(function (node) { parent.appendChild(node); });
  }

  // ========== 块级元素渲染 ==========
  function renderBlock(block, container) {
    var el;

    switch (block.type) {
      case "heading":
        el = document.createElement("h" + block.level);
        el.id = block.id;
        el.textContent = block.text;
        container.appendChild(el);
        break;

      case "paragraph":
        el = document.createElement("p");
        appendInline(el, block.content);
        container.appendChild(el);
        break;

      case "code_block":
        var wrapper = document.createElement("div");
        wrapper.className = "code-block-wrapper";

        if (block.lang) {
          var langLabel = document.createElement("div");
          langLabel.className = "code-lang-label";
          langLabel.textContent = block.lang;
          wrapper.appendChild(langLabel);
        }

        var pre = document.createElement("pre");
        var code = document.createElement("code");
        if (block.lang) code.className = "language-" + block.lang;
        code.textContent = block.content;
        pre.appendChild(code);
        wrapper.appendChild(pre);
        applySyntaxHighlight(code, block.lang);
        container.appendChild(wrapper);
        break;

      case "table":
        el = document.createElement("div");
        el.className = "table-wrapper";
        var table = document.createElement("table");

        if (block.header && block.header.length) {
          var thead = document.createElement("thead");
          var tr = document.createElement("tr");
          block.header.forEach(function (cell, idx) {
            var th = document.createElement("th");
            th.textContent = cell;
            if (block.align && block.align[idx]) {
              th.style.textAlign = block.align[idx];
            }
            tr.appendChild(th);
          });
          thead.appendChild(tr);
          table.appendChild(thead);
        }

        if (block.rows && block.rows.length) {
          var tbody = document.createElement("tbody");
          block.rows.forEach(function (row) {
            var tr2 = document.createElement("tr");
            row.forEach(function (cell, idx) {
              var td = document.createElement("td");
              td.textContent = cell;
              if (block.align && block.align[idx]) {
                td.style.textAlign = block.align[idx];
              }
              tr2.appendChild(td);
            });
            tbody.appendChild(tr2);
          });
          table.appendChild(tbody);
        }

        el.appendChild(table);
        container.appendChild(el);
        break;

      case "list":
        el = document.createElement(block.ordered ? "ol" : "ul");
        if (block.ordered && block.start && block.start !== 1) {
          el.start = block.start;
        }

        // 检查是否为任务列表
        var hasTasks = block.items.some(function (item) { return item.type === "task_item"; });
        if (hasTasks) {
          el.className = "task-list";
        }

        block.items.forEach(function (item) {
          el.appendChild(renderListItem(item));
        });
        container.appendChild(el);
        break;

      case "blockquote":
        el = document.createElement("blockquote");
        if (block.content) {
          block.content.forEach(function (inner) { renderBlock(inner, el); });
        }
        container.appendChild(el);
        break;

      case "hr":
        el = document.createElement("hr");
        container.appendChild(el);
        break;

      case "math_block":
        el = document.createElement("div");
        el.className = "math-block";
        el.textContent = block.content;
        container.appendChild(el);
        break;

      case "raw_html_block":
        el = document.createElement("div");
        el.className = "raw-html-block";
        el.innerHTML = block.content;
        container.appendChild(el);
        break;

      default:
        break;
    }
  }

  function renderListItem(item) {
    var li = document.createElement("li");

    if (item.type === "task_item") {
      li.className = "task-item";
      var checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.disabled = true;
      checkbox.checked = !!item.checked;
      li.appendChild(checkbox);
    }

    if (item.content && item.content.length) {
      var span = document.createElement("span");
      appendInline(span, item.content);
      li.appendChild(span);
    }

    if (item.items && item.items.length) {
      var subList = document.createElement("ul");
      // 判断子列表是否为有序列表
      var isOrdered = item.items.some(function (sub) {
        return sub.type === "list_item";
      });
      // 如果有嵌套的任务列表项
      item.items.forEach(function (subItem) {
        subList.appendChild(renderListItem(subItem));
      });
      li.appendChild(subList);
    }

    return li;
  }

  // ========== 目录渲染 ==========
  function renderTOC(toc, container) {
    if (!toc || !toc.length) return;

    var tocContainer = document.createElement("nav");
    tocContainer.className = "toc";
    tocContainer.innerHTML = '<h3 class="toc-title">目录</h3>';
    var ul = document.createElement("ul");

    toc.forEach(function (item) {
      var li = document.createElement("li");
      li.className = "toc-level-" + item.level;
      var a = document.createElement("a");
      a.href = "#" + item.id;
      a.textContent = item.text;
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var target = document.getElementById(item.id);
        if (target) {
          target.scrollIntoView({ behavior: "smooth" });
          // 更新 hash
          history.pushState(null, null, "#" + item.id);
        }
      });
      li.appendChild(a);
      ul.appendChild(li);
    });

    tocContainer.appendChild(ul);
    container.appendChild(tocContainer);
  }

  // ========== 轻量语法高亮 ==========
  function applySyntaxHighlight(codeEl, lang) {
    if (!lang) return;
    var text = codeEl.textContent;

    var patterns = {
      python: [
        { regex: /(#.*)/g, cls: "hl-comment" },
        { regex: /\b(import|from|def|class|return|if|else|elif|for|while|in|not|and|or|is|with|as|try|except|finally|raise|yield|lambda|pass|break|continue|global|nonlocal|assert|del)\b/g, cls: "hl-keyword" },
        { regex: /\b(True|False|None)\b/g, cls: "hl-builtin" },
        { regex: /\b(print|len|range|int|str|float|list|dict|set|tuple|type|isinstance|open|input|super)\b/g, cls: "hl-function" },
        { regex: /(&quot;&quot;&quot;[\s\S]*?&quot;&quot;&quot;|&#39;&#39;&#39;[\s\S]*?&#39;&#39;&#39;)/g, cls: "hl-string" },
        { regex: /(&quot;[^&]*?&quot;|&#39;[^&#]*?&#39;|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, cls: "hl-string" },
        { regex: /\b(\d+\.?\d*)\b/g, cls: "hl-number" }
      ],
      javascript: [
        { regex: /(\/\/.*)/g, cls: "hl-comment" },
        { regex: /\/\*[\s\S]*?\*\//g, cls: "hl-comment" },
        { regex: /\b(var|let|const|function|return|if|else|for|while|do|switch|case|break|continue|new|this|class|extends|import|export|default|from|async|await|try|catch|finally|throw|typeof|instanceof|in|of|yield|null|undefined|true|false|void|delete)\b/g, cls: "hl-keyword" },
        { regex: /\b(console|document|window|Array|Object|String|Number|Boolean|Math|Date|JSON|Promise|Map|Set|RegExp|Error)\b/g, cls: "hl-builtin" },
        { regex: /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)/g, cls: "hl-string" },
        { regex: /\b(\d+\.?\d*)\b/g, cls: "hl-number" }
      ],
      bash: [
        { regex: /(#.*)/g, cls: "hl-comment" },
        { regex: /\b(echo|cd|ls|mkdir|rm|cp|mv|cat|grep|sed|awk|find|export|source|if|then|else|fi|for|do|done|while|case|esac|function|return|exit|sudo|apt|npm|pip|python)\b/g, cls: "hl-keyword" },
        { regex: /(\$[\w]+|\$\{[\w]+\})/g, cls: "hl-builtin" },
        { regex: /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, cls: "hl-string" }
      ],
      json: [
        { regex: /("(?:[^"\\]|\\.)*")\s*:/g, cls: "hl-keyword" },
        { regex: /:\s*("(?:[^"\\]|\\.)*")/g, cls: "hl-string" },
        { regex: /\b(true|false|null)\b/g, cls: "hl-builtin" },
        { regex: /\b(\d+\.?\d*)\b/g, cls: "hl-number" }
      ],
      html: [
        { regex: /(&lt;!--[\s\S]*?--&gt;)/g, cls: "hl-comment" },
        { regex: /(&lt;\/?[\w-]+)/g, cls: "hl-keyword" },
        { regex: /\b([\w-]+)=/g, cls: "hl-builtin" },
        { regex: /("(?:[^"\\]|\\.)*")/g, cls: "hl-string" }
      ],
      css: [
        { regex: /(\/\*[\s\S]*?\*\/)/g, cls: "hl-comment" },
        { regex: /([.#][\w-]+)/g, cls: "hl-keyword" },
        { regex: /\b(display|position|margin|padding|border|color|background|font|width|height|top|left|right|bottom|z-index|overflow|flex|grid|transition|transform|animation|opacity|text-align|line-height|box-sizing)\b/g, cls: "hl-builtin" },
        { regex: /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, cls: "hl-string" },
        { regex: /\b(\d+\.?\d*(px|em|rem|%|vh|vw|s|ms|deg)?)\b/g, cls: "hl-number" }
      ]
    };

    var langPatterns = patterns[lang] || patterns.javascript;
    var highlighted = escapeHtml(text);

    langPatterns.forEach(function (rule) {
      highlighted = highlighted.replace(rule.regex, function (match) {
        return '<span class="' + rule.cls + '">' + match + "</span>";
      });
    });

    codeEl.innerHTML = highlighted;
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  // ========== 主渲染函数 ==========
  function render(data) {
    var app = document.getElementById("app");
    if (!app) {
      app = document.createElement("div");
      app.id = "app";
      document.body.appendChild(app);
    }
    app.innerHTML = "";

    // 渲染元数据标题
    if (data.metadata && data.metadata.title) {
      var titleEl = document.createElement("header");
      titleEl.className = "doc-header";
      var h1 = document.createElement("h1");
      h1.textContent = data.metadata.title;
      titleEl.appendChild(h1);

      if (data.metadata.author || data.metadata.created) {
        var meta = document.createElement("div");
        meta.className = "doc-meta";
        if (data.metadata.author) {
          var authorSpan = document.createElement("span");
          authorSpan.textContent = "作者: " + data.metadata.author;
          meta.appendChild(authorSpan);
        }
        if (data.metadata.created) {
          var dateSpan = document.createElement("span");
          dateSpan.textContent = "日期: " + data.metadata.created;
          meta.appendChild(dateSpan);
        }
        titleEl.appendChild(meta);
      }

      app.appendChild(titleEl);
    }

    // 渲染目录
    renderTOC(data.toc, app);

    // 渲染内容区
    var content = document.createElement("main");
    content.className = "doc-content";
    if (data.blocks) {
      data.blocks.forEach(function (block) {
        renderBlock(block, content);
      });
    }
    app.appendChild(content);

    // 更新页面标题
    var pageTitle = (data.metadata && data.metadata.title) || "Markdown Document";
    document.title = pageTitle;
  }

  // ========== 暗黑模式切换 ==========
  function initThemeToggle() {
    var saved = localStorage.getItem("md-theme");
    if (saved === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    } else if (saved === "light") {
      document.documentElement.removeAttribute("data-theme");
    } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      document.documentElement.setAttribute("data-theme", "dark");
    }

    var btn = document.createElement("button");
    btn.className = "theme-toggle";
    btn.title = "切换明暗模式";
    updateThemeIcon(btn);
    btn.addEventListener("click", function () {
      var isDark = document.documentElement.getAttribute("data-theme") === "dark";
      if (isDark) {
        document.documentElement.removeAttribute("data-theme");
        localStorage.setItem("md-theme", "light");
      } else {
        document.documentElement.setAttribute("data-theme", "dark");
        localStorage.setItem("md-theme", "dark");
      }
      updateThemeIcon(btn);
    });
    document.body.appendChild(btn);
  }

  function updateThemeIcon(btn) {
    var isDark = document.documentElement.getAttribute("data-theme") === "dark";
    btn.textContent = isDark ? "\u2600" : "\u263D";
  }

  // ========== 启动 ==========
  function init() {
    initThemeToggle();
    // 优先从内嵌 script 标签读取
    var embeddedData = document.getElementById("md-data");
    if (embeddedData) {
      try {
        var data = JSON.parse(embeddedData.textContent);
        render(data);
        return;
      } catch (e) {
        console.error("解析内嵌 JSON 失败:", e);
      }
    }

    // 从外部 JSON 文件加载
    var jsonPath = document.body.getAttribute("data-json");
    if (!jsonPath) {
      // 自动检测：与 HTML 同名的 .json 文件
      var htmlPath = window.location.pathname;
      jsonPath = htmlPath.replace(/\.html?$/i, ".json");
    }

    fetch(jsonPath)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        render(data);
      })
      .catch(function (err) {
        console.error("加载 JSON 失败:", err);
        var app = document.getElementById("app");
        if (!app) {
          app = document.createElement("div");
          app.id = "app";
          document.body.appendChild(app);
        }
        app.innerHTML = '<div class="error">加载文档数据失败: ' + escapeHtml(err.message) + '</div>';
      });
  }

  // DOM 就绪后启动
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
