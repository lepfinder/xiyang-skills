---
name: generate-image
description: >-
  AI 图像生成与项目内静态资源交付。通过 scripts/generate.py 直连阿里万相 (DashScope)
  或 Google Gemini API，支持垫图 (--ref)。用于生成配图、插画、文章插图、架构示意，
  或将图片保存到 share-tutorial assets；不依赖 Ada Core generate_image 工具。
---

# Generate Image

在 Ada 项目内外通用的生图技能：Agent **必须**通过 `scripts/generate.py` 执行生图，禁止编造图片 URL 或假装已生成。

## 快速开始

```bash
# 1. 配置密钥（勿提交 git）
cp .agents/skills/generate-image/.env.example .agents/skills/generate-image/.env
# 或写入 ~/.image_gen_env / 项目根 .env

# 2. 生图
python3 .agents/skills/generate-image/scripts/generate.py \
  "A hand-drawn diagram on white background" \
  -p wanxiang -a 16:9 \
  -o ./out/01.png --json
```

脚本读取密钥顺序：当前目录 `.env` → 技能目录 `.env` → `~/.image_gen_env`。

| 环境变量 | 用途 |
|----------|------|
| `DASHSCOPE_API_KEY` / `WANXIANG_API_KEY` | 阿里万相 |
| `GEMINI_API_KEY` | Google Gemini 图像 |
| `DASHSCOPE_BASE_URL`（可选） | 覆盖万相 endpoint |

---

## 命令参考

```bash
python3 .agents/skills/generate-image/scripts/generate.py <prompt> [选项]
```

| 选项 | 说明 | 默认 |
|------|------|------|
| `-p` / `--provider` | `wanxiang` \| `gemini` | `wanxiang` |
| `-m` / `--model` | 模型 ID | 万相 `wan2.7-image-pro`；Gemini `gemini-3.1-flash-image-preview` |
| `-a` / `--aspect-ratio` | `1:1` `16:9` `9:16` `4:3` `3:4` … | `16:9` |
| `-o` / `--output` | 输出路径 | `generated-时间戳.png` |
| `-r` / `--ref` | 参考图/垫图，**可多次** | 无 |
| `--base-url` | 万相 API 地址（仅 wanxiang） | Token Plan 默认 |
| `--json` | 输出 `{"ok":true,"path":"...","log_id":"..."}` | 否 |
| `--no-log` | 不写入本地记录 | 默认会记录 |

---

## 本地生图记录

每次调用 `generate.py`（成功或失败）会**自动追加**一条 JSON 到：

```
.agents/skills/generate-image/logs/generations.jsonl
```

（仓库根 `.gitignore` 已忽略 `logs/`，不会误提交）

单条记录示例：

```json
{
  "id": "a1b2c3d4e5f6",
  "ok": true,
  "created_at": "2026-07-06T01:12:00+00:00",
  "prompt": "…",
  "provider": "wanxiang",
  "model": "wan2.7-image-pro",
  "aspect_ratio": "16:9",
  "output_path": "/abs/path/to/01.png",
  "refs": [],
  "error": null
}
```

自定义路径：环境变量 `IMAGE_GEN_LOG`（见 `.env.example`）。

### 查看历史

```bash
# 最近 20 条
python3 .agents/skills/generate-image/scripts/history.py

# 最近 5 条，JSON 格式
python3 .agents/skills/generate-image/scripts/history.py -n 5 --json

# 仅失败记录
python3 .agents/skills/generate-image/scripts/history.py --failed
```

也可用 `jq` 直接查：

```bash
jq -s '.[-5:]' .agents/skills/generate-image/logs/generations.jsonl
```

---

| 场景 | 建议 |
|------|------|
| 中文手绘、正文配图 | `wanxiang` |
| 风格化、多模态、垫图改图 | `gemini` |
| 需要角色/IP 垫图 | 两者均可，优先 `gemini` + `--ref` |

常用 Gemini 模型：`gemini-3.1-flash-image-preview`（快）、`gemini-3-pro-image-preview`、`gemini-2.5-flash-image`。

### 垫图 `--ref`

对齐 Ada `imagePaths`：请求体为 **prompt 文本 + 按顺序附加的图片**。

```bash
python3 .agents/skills/generate-image/scripts/generate.py \
  "Keep reference character style, new scene: desk with laptop" \
  -p gemini -a 16:9 \
  --ref apps/core/public/character_refs/ref2.png \
  -o ./out/01.png
```

| 提供商 | 垫图 |
|--------|------|
| 万相 DashScope 原生 | ✅ 支持多张 |
| 万相 compatible-mode | ❌ 忽略 `--ref` 并警告 |
| Gemini | ✅ 支持多张 |

格式：`.png` `.jpg` `.jpeg` `.webp` `.gif`

---

## 静态资源交付（share-tutorial）

为 Markdown 配图时，**直接用 `-o` 写到目标 assets**，不要平铺在仓库根目录。

**路径规则**（与编辑中的 `.md` 同结构）：

```
apps/share-portal/public/share-tutorial/assets/<大类>/<文章主名>/01.png
```

示例：编辑 `1-philosophy/02_why-book.md` 时：

```bash
python3 .agents/skills/generate-image/scripts/generate.py \
  "..." -p wanxiang -a 16:9 \
  -o apps/share-portal/public/share-tutorial/assets/1-philosophy/02_why-book/01.png
```

**Markdown 引用**（相对路径）：

```markdown
![插图描述](../assets/1-philosophy/02_why-book/01.png)
```

- 同章多图：`01.png`、`02.png` …
- 正文配图默认 `-a 16:9`

---

## Agent 执行清单

1. **检查密钥**：未配置则提示用户设置，禁止猜测
2. **写 prompt**：详尽英文或中文均可；垫图时在 prompt 中说明如何使用参考图
3. **执行脚本**：加 `--json` 解析输出路径与 `log_id`
4. **落盘**：`-o` 指向 §静态资源交付 中的目标路径
5. **嵌入 Markdown**：写入正确的 `../assets/...` 相对路径
6. **失败重试**：换 provider 或简化 prompt，勿伪造结果

---

## 与其他技能配合

- **[xiyang-illustrations](../xiyang-illustrations/SKILL.md)**：负责希扬风格 shot list、提示词模板与 QA；**生图步骤调用本技能 `generate.py`**。成图**禁止**出现「希扬」「Xiyang」等 IP 名字，只保留人物形象；prompt 中须写明 `Do NOT write 希扬 or Xiyang on the image`。
- **[architecture-diagram](../architecture-diagram/SKILL.md)**：架构图 HTML 页面，不走本生图脚本

---

## 实现说明

脚本逻辑参考 Ada Core：

- `apps/core/src/domain/agent/tools/image/engines/wanxiang.ts`
- `apps/core/src/domain/agent/tools/image/engines/google.ts`
