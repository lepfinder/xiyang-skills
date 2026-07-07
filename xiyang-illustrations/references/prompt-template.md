# 生图提示词模板

在需要生成图片时，将以下变量替换为当前图的内容，确保生成单张独立图片：

```text
Generate one standalone 16:9 horizontal Chinese article illustration.

Visual DNA:
Pure white background. Minimalist black hand-drawn line art. Slightly wobbly pen lines. Lots of empty white space. Sparse orange-yellow/red/blue handwritten Chinese annotations. Clean product-sketch feeling with a sense of warm humanity. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI.

Recurring boy character required (describe in prompt only — NEVER write his name on the image):
A small minimalist hand-drawn chibi boy. Fluffy spiky black hair (刺刺的黑色短发), large round black-framed glasses (圆黑框眼镜), large round curious eyes, calm expression. Dark blue short-sleeved T-shirt (深蓝色短袖T恤), beige shorts (米色短裤), barefoot (光脚). He must perform the core conceptual action rather than just decorating. Keep him focused, intelligent, and helpful, not silly.

IMPORTANT — No character name on canvas:
Do NOT write 希扬, Xiyang, or any character name label, name tag, caption, or title above/near the boy. The boy has no text label identifying him. Only content-metaphor Chinese annotations are allowed (listed in Chinese handwritten labels below).

Theme:
{正文配图主题}

Structure type:
{结构类型：Workflow / 系统局部 / 前后对比 / 希扬状态 / 概念隐喻 / 方法分层 / 地图路线}

Core idea:
{这张图要表达的核心意思}

Composition:
{具体画面设计：小男孩在什么位置、做什么交互动作、核心物件和路径如何排布}

Suggested elements:
{元素1} / {元素2} / {元素3}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4}

Color use:
Black for main line art, text, hair, and glasses. Dark blue for 希扬's T-shirt. Warm amber/orange-yellow for main flow paths, lightbulbs, or things being "nurtured" or "lit up". Red only for key warnings, bugs, blocks, or problematic states. Blue only for secondary comments or system status.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels — content metaphors only, never the character's name. Do not write 希扬 or Xiyang anywhere on the image. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Do not copy prior examples or reuse known case compositions unless explicitly requested; invent a fresh visual metaphor for this specific article. It should be clear but not instructional, interesting but not childish, strange but clean.
```

## 图像局部编辑提示

**去除左上角多余标题**：
```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean white background, matching the surrounding blank paper. Preserve everything else exactly: characters, labels, paths, line style, composition, aspect ratio, and image quality. Do not add any new text or objects.
```

**增强角色主体性（如果小男孩太像背景贴纸）**：
```text
Regenerate this illustration with the same core meaning and simple layout, but make the hand-drawn boy with glasses more central to the conceptual action. He should be actively doing the work (like watering, connecting, lifting, or untangling) that explains the idea, not standing beside the diagram. Do not add any character name label. Keep it clean, sparse, hand-drawn, and not cute.
```
