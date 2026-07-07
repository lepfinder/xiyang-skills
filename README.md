# xiyang-skills

一套 AI Agent 技能集，包含图像生成、手绘风格正文配图和架构图生成能力。

## 技能概览

| 技能 | 说明 |
|------|------|
| [**generate-image**](generate-image/) | AI 图像生成脚本，支持阿里万相 (DashScope) 和 Google Gemini 两种后端，提供垫图、历史记录、静态资源交付等完整工作流 |
| [**xiyang-illustrations**](xiyang-illustrations/) | 希扬风格中文正文配图，以手绘简笔 IP 角色为核心，为文章生成 16:9 横版解释性插图 |
| [**architecture-diagram**](architecture-diagram/) | 暗黑科技风架构图与知识地图 HTML 页面生成，结构与样式分离，支持 PNG/PDF 导出 |

## 快速开始

### 1. 配置 API 密钥

```bash
cp generate-image/.env.example generate-image/.env
# 编辑 .env 填入 DASHSCOPE_API_KEY 或 GEMINI_API_KEY
```

> `.env` 已在 `.gitignore` 中，不会被提交。

### 2. 生成图片

```bash
python3 generate-image/scripts/generate.py \
  "A hand-drawn diagram on white background" \
  -p wanxiang -a 16:9 \
  -o ./out/01.png
```

查看历史记录：

```bash
python3 generate-image/scripts/history.py       # 最近 20 条
python3 generate-image/scripts/history.py --failed  # 仅失败记录
```

### 3. 生成希扬插图

向 Agent 描述需要配图的文章或段落，Agent 会自动使用 xiyang-illustrations 技能制定配图策略，并调用 generate-image 完成生图。

### 4. 生成架构图

向 Agent 描述系统架构，Agent 会生成独立的 HTML 文件，内嵌 SVG 架构图，提供一键导出 PNG/PDF 的悬浮工具栏。

## 目录结构

```
├── generate-image/              # 图像生成引擎
│   ├── scripts/
│   │   ├── generate.py          # 生图主脚本
│   │   └── history.py           # 历史记录查询
│   ├── logs/                    # 生图日志 (git-ignored)
│   ├── .env.example             # 环境变量模板
│   └── SKILL.md
├── xiyang-illustrations/        # 希扬风格配图
│   ├── agents/openai.yaml       # Agent 配置
│   ├── assets/examples/         # 参考案例
│   ├── references/              # 风格 DNA / IP 定义 / 构图模板 / QA 检查表
│   └── SKILL.md
├── architecture-diagram/        # 架构图生成
│   ├── resources/
│   │   ├── template.html        # 页面模板
│   └── SKILL.md
└── .gitignore
```

## 使用建议

- **中文手绘正文配图** → `generate-image` + `wanxiang` 提供商
- **风格化/多模态/垫图改图** → `generate-image` + `gemini` 提供商
- **需要角色 IP 垫图** → 优先 `gemini` + `--ref` 参数
- **系统架构图/知识地图** → `architecture-diagram` 技能，不走生图脚本

## License

Private
