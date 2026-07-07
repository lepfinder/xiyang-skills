---
name: architecture-diagram
description: 在项目中创建一致的暗黑科技风架构图与知识地图 HTML 页面。使用外链的 diagram-base.css 与 diagram-base.js 以保持样式统一。
---

# Architecture Diagram Skill (项目特化版)

本技能用于为 Ada 相关的文档和页面生成标准的、暗黑科技风格的系统架构图与知识地图。通过结构与样式分离的设计，保证项目内所有图表的视觉一致性和极低的代码冗余。

## 统一引用规范

所有生成的 `.html` 图标文件，**必须**在 `<head>` 中引入本项目的公共样式表与脚本以代替重复硬编码：

```html
<link rel="stylesheet" href="./diagram-base.css">
<!-- 导出 PNG/PDF 所需的三方依赖 -->
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js" integrity="sha384-ZZ1pncU3bQe8y31yfZdMFdSpttDoPmOZg2wguVK9almUodir1PghgT0eY7Mrty8H" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.2/dist/jspdf.umd.min.js" integrity="sha384-en/ztfPSRkGfME4KIm05joYXynqzUgbsG5nMrj/xEFAHXkeZfO3yMK8QQ+mP7p1/" crossorigin="anonymous"></script>
<!-- 公共交互与导出功能 -->
<script src="./diagram-base.js" defer></script>
```

## 页面骨架结构

生成的 HTML 文件体结构必须包含以下核心骨架（仅包含绘图区与绝对定位在右上角的悬浮工具栏）：

```html
<div id="report-container" class="container">
  <!-- 右上角悬浮工具栏 (事件由 diagram-base.js 自动接管) -->
  <div class="toolbar" id="diagram-toolbar">
    <button class="toolbar-toggle">⋯</button>
    <div class="toolbar-actions">
      <button class="toolbar-btn" data-action="copy">📋 复制 PNG</button>
      <button class="toolbar-btn" data-action="png">🖼️ 下载 PNG</button>
      <button class="toolbar-btn" data-action="pdf">📄 导出 PDF</button>
    </div>
  </div>

  <!-- 绘图包裹区 -->
  <div class="diagram-wrapper">
    <svg viewBox="0 0 1000 580" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- 具体的 SVG 内容 -->
    </svg>
  </div>
</div>
```

## 设计系统规范

所有核心配色与圆角依然遵循公共的 `diagram-base.css` 所定义的变量：

* **背景色**：`#020617` (slate-950) 配合微弱的暗网格系统。
* **卡片边框/分割线**：`#1e293b` (slate-800)。
* **语义主色调（描边/发光指示）**：
  * **Cyan (前端/客户端)**: `var(--accent-cyan)` / `#22d3ee`
  * **Emerald (后端/引擎)**: `var(--accent-emerald)` / `#34d399`
  * **Rose (安全/沙箱)**: `var(--accent-rose)` / `#fb7185`
  * **Violet (数据库/持久化)**: `var(--accent-violet)` / `#a78bfa`
  * **Amber (警告/核心概念)**: `var(--accent-amber)` / `#fbbf24`
