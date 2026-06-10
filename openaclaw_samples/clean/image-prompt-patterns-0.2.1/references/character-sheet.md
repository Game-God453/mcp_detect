# Character Sheet Patterns

## 什么时候用

- 原创角色的三视图 / 设定表（Official Character Sheet）
- 游戏角色介绍页 / 卡牌网格
- 动漫快照转换（真人→动漫风）
- 隐藏面部的气氛向角色艺术

## 四大模式

### A. 官方设定表（日式 Official Character Sheet）
**核心结构**：单页多视图 + 信息面板

**关键词组合**：
```
official character design reference sheet, Japanese anime style,
multiple viewing angles arranged in grid:
[front view] [3/4 view] [side view] [back view],
separate close-up of [face detail] and [hand/weapon detail],
character height chart with scale markers,
color palette swatches in sidebar,
Japanese text annotations with character name and stats,
clean white background with light grid pattern,
studio design document aesthetic
```

**构成元素清单**：
- [ ] 主视图（正面全身）— 最大，居中或左侧
- [ ] 侧面图 + 背面图 — 尺寸略小
- [ ] 3/4 视角 — 展示立体感
- [ ] 面部特写 — 表情 2-3 个
- [ ] 细节特写 — 服装/武器/饰品的零件
- [ ] 身高对照 — 刻度线
- [ ] 配色板 — 色块 + 色号
- [ ] 文字标注 — 角色名、属性、设定要点

### B. 游戏角色介绍页（Gal Game / RPG 介绍页）
**核心结构**：立绘 + 半透明信息框

**关键词组合**：
```
Japanese visual novel character introduction page,
full body standing illustration on right side,
semi-transparent character info panel on left showing:
name (large typography), age, height, occupation,
character description paragraph, favorite things list,
soft gradient background with subtle floral/geometric patterns,
gal game / visual novel UI aesthetic,
warm soft lighting on character
```

### C. Persona5 卡牌参考风格（Tarot-Style Card）
**核心结构**：单角色 + 符号化边框 + 编号

**关键词组合**：
```
Persona5 style character reference card,
stylized pose with dynamic angle,
bold typography with character name in large letters,
Arcana card number prominent (e.g., "XIV"),
red-black-white color scheme with gradient accents,
graffiti/street art texture,
asymmetric composition with overlapping geometric shapes,
acid-jazz ui aesthetic
```

### D. 卡牌网格（多角色一张图）
**核心结构**：同一风格下的角色合集展示

**关键词组合**：
```
[N] characters arranged in [ROWS]x[COLUMNS] grid layout,
each character in identical pose and lighting setup
for visual consistency,
each with unique outfit/weapon/color palette,
unified background (plain white/gradient/textured),
character name label under each portrait,
[ART STYLE e.g. Saint Seiya gold saints, Persona5, Pokemon TCG]
```

---

## 风格迁移词汇库

### 动漫/日式风格细分
- **90年代赛璐璐**：`1990s cel-shaded anime aesthetic, hand-painted cels`
- **现代数字作画**：`modern digital anime illustration, Kyoto Animation style`
- **漫画黑白**：`manga black and white, screentone shading`
- **轻小说插画**：`light novel illustration style, soft pastel rendering`
- **赛博朋克动漫**：`cyberpunk anime aesthetic, neon-lit rim light`

### 美式/西式风格
- **美式卡通**：`western animation, Disney/Pixar 3D style`
- **图像小说**：`graphic novel illustration, Mike Mignola-style shadows`
- **蒸汽波角色**：`vaporwave character design, pink and cyan`

### 游戏风格
- **像素艺术**：`16-bit pixel art sprite sheet, SNES aesthetic`
- **2D Fighter**：`2D fighting game character select portrait`
- **JRPG 立绘**：`classic JRPG character portrait, [series e.g. Final Fantasy 7]`
- **Roguelike 像素**：`roguelike game pixel character, Hades-influenced`

---

## 三视图生成硬规则

### 必须指定
- [ ] 背景：`plain white background` 或 `grid pattern background`
  → 没指定会出现杂乱环境
- [ ] 镜头：`orthographic view` or `3/4 perspective view`
  → 防止透视变形
- [ ] 光源：`flat even studio lighting`
  → 三视图不要戏剧光
- [ ] 一致性：`same character, same outfit, identical proportions across all views`
  → 关键！不加会导致多视图像是不同人

### 容易出错的点
- ⚠️ 三视图里角色身高/比例不一致 → 加 `height chart scale reference`
- ⚠️ 服装细节每个视图都不同 → 加 `consistent clothing details across all angles`
- ⚠️ 表情杂乱 → 主视图指定 `neutral expression`，其他视图参考

---

## 完整案例模板

### 原创角色官方设定表
```
official character design reference sheet for original character "[NAME]",
Japanese anime studio design document aesthetic,
multiple orthographic views arranged horizontally:
front view (largest, center), 3/4 left view,
side profile left view, back view,
smaller panel with face close-up showing 3 expressions:
[neutral / smiling / determined],
hand detail showing [weapon/item],
character stat block in sidebar: height [X]cm, age [Y], class/role,
color palette swatches with hex codes,
name printed at top in Japanese and English,
plain white background with light blue grid pattern,
flat even studio lighting,
consistent proportions across all views,
clean line art with cell-shaded coloring
```

### Gal Game 介绍页
```
Japanese visual novel style character introduction page,
9:16 vertical composition,
full body character illustration on right 60% of frame:
[CHARACTER DESCRIPTION - appearance, outfit, pose],
soft cheerful expression, looking at viewer,
left 40% is semi-transparent glass panel containing:
character name "[NAME]" in large serif typography at top,
stats: age [X], height [Y], birthday [Z],
introduction paragraph (3 lines lorem ipsum placeholder),
list of favorite things with small icons,
background: soft blurred cherry blossom garden at golden hour,
warm color palette, anime gal game aesthetic
```

### 多角色卡牌网格
```
6 original characters arranged in 2x3 grid layout,
each character in identical 3/4 standing pose,
consistent lighting: soft top-front key light,
[THEME e.g. "royal guards of fantasy kingdom"],
each character has unique:
- color palette (color-coded roles)
- weapon/accessory
- armor style variation within theme
shared design language: [e.g. "ornate gold trim, navy blue base"],
character name plate under each portrait,
unified dark navy background with subtle pattern,
[STYLE REFERENCE e.g. "Saint Seiya gold cloth design"]
```

---

## 模式 E：动作分镜表 / Movement Sheet（pose-as-prompt）

### 核心思路

把"时间维度的动作序列"编码成**一张带网格的参考图**，再喂给 img2video 模型（Seedance 2.0 / Kling / Runway 等）驱动角色跳舞、做动作、打斗。

**原理**：img2video 默认只能指定首帧/尾帧，中间靠模型瞎猜 → 动作幅度和节奏全失控。给它一张 16 格的动作分镜表当参考，等价于手动提供了一个"pose sequence storyboard"，把时间控制权从文字 prompt 挪到图像里。

**对应的行业趋势**：这是"Video-as-Prompt / Pose-as-Prompt"在 img2video 通道上的 workaround。Kling 3.0 原生支持 Video-as-Prompt；Seedance 2.0 没有原生时序控制，但支持多模态参考图（最多 12 个），于是"动作表图"成了实际可行的替代方案。

### prompt 模板

```
[STYLE]
Monochrome grayscale illustration, 3D-rendered character,
clean instructional reference sheet, white background,
comic-style cell grid layout, [N] cells arranged in [ROWS]x[COLUMNS],
each cell numbered 1-[N] with bold header label,
full-body character in each cell performing one dance/action step,

[MOTION ANNOTATION]
motion arrows (curved/straight) indicating body rotation, arm swing,
footwork direction drawn on each figure,
dotted lines for secondary motion, solid arrows for primary motion,

[CELL CONTENT]
cell 1: [ACTION NAME e.g. WARM-UP POSE] — [POSE DESCRIPTION]
cell 2: [ACTION NAME e.g. RHYTHM FLOW] — [POSE DESCRIPTION]
...

[CAPTION UNDER EACH CELL]
short instructional sentence like "Arms pop quickly. Lower center of gravity,
rotate. Cross feet, stop." — matches the pose,

[AESTHETIC]
instructional manual / training poster aesthetic,
sans-serif condensed typography, uppercase labels,
no color, no background clutter, information-first design
```

### 使用要点

- **黑白灰 + 白底**：把"动作信息"从"画面信息"里剥离，喂给 img2video 时不污染目标角色的造型
- **箭头 + 文字双重约束**：单独用图模型会漏节奏，单独用文字会漏幅度，两者叠加才稳
- **网格数量 = 目标视频关键帧数**：15 秒视频取 12-16 格比较合适；动作越复杂网格越多
- **cell 内角色保持同一身体，只换姿势**：保证 img2video 阶段的角色一致性
- **动作名用大写标签**（WARM-UP / FOOTWORK / WAVE MOVEMENT）：模型识别率比小写描述高

### 配套 img2video 调用

```
[目标角色参考图] + [动作分镜表] → Seedance 2.0 多参考图输入
prompt: "[角色描述] performing the dance sequence shown in the reference sheet,
        following the 16 movements in order, smooth transitions between steps,
        [环境描述], [时长] seconds, 9:16 vertical"
```

### 项目溯源

#### Oggii 动作分镜表 × Seedance 2.0（2026-04-26，来源：X @oggii_0）

**原 prompt（节选）**：
```
[STYLE]
Monochrome grayscale illustration, 3D-rendered character,
clean instructional reference sheet, white background,
comic-style cell grid layout, ...
```

**目标**：让 Seedance 2.0 生成一段 15s 连贯舞蹈，角色是巴黎街头的亚洲女孩（绿开衫 + 格子短裙）。

**关键决策**：
- 先用 GPT Image 2.0 生成 4×4 动作分镜表（16 格：WARM-UP POSE / RHYTHM FLOW / GENTLE WAVE / FOOTWORK / POPPING / WAVE MOVEMENT / CROSS STEP / WAVE STEP 等）
- 每格下面都挂一句一样的指令式描述（"Arms pop quickly. Lower center of gravity, rotate. Cross feet, stop."）
- 分镜表和目标角色图**分开做**：分镜表只管动作，角色图只管造型，在 Seedance 侧合并

**踩过的坑**：
- 如果直接用 prompt 文字描述"跳舞 15 秒"，Seedance 会反复循环同一个 2-3 秒动作
- 如果动作表带背景/颜色，img2video 会把背景也迁过去，污染目标场景
- 文字指令必须短句 + 祈使式，不要写叙事"she slowly moves her arms"

**学到的**：
- img2video 的时序控制瓶颈可以用"动作表图"绕过，是当前（2026-Q2）最具操作性的方案
- 这是一种"把知识从时间维度压缩到空间维度"的典型手法，character sheet（角度压缩）和 movement sheet（时间压缩）是同一套思维的两个面
- 这个工作流适合：短舞蹈、打斗序列、循环动作合集、体操/瑜伽示范类视频

---

---

## 模式 E 沉淀：可复用双 prompt 模板（2026-04-29）

> Neal 的使用场景：动作拆解工作流，换主人公即可复用。
> 分两步：(1) 先生成灰度 movement sheet 锁动作 → (2) 再 img2img 风格化成发得出去的海报。
> 实际用的时候：**第一步必须先确认 16 格动作都对了再进第二步**，不然风格化救不回动作错误。

### 模板 A：灰度动作分镜表（text2image，第一步）

**用途**：生成干净的 4×4 动作教学图，作为 img2video 的时序参考，或作为模板 B 的输入。

**变量**：
- `{CHARACTER_DESCRIPTION}` — 具体外观描述（纯 text2image 时必填；带参考图时可写 `use reference image as character design`）
- `{ACTION_THEME}` — 整体动作主题（如 "spinning hook kick" / "K-pop chorus choreography" / "yoga sun salutation"）
- `{16_ACTION_LABELS}` — 16 个连续关键帧标签，每个 2-3 词

```
[STYLE]
Monochrome grayscale illustration, 3D-rendered character,
clean instructional reference sheet, white background,
comic-style cell grid layout, technical diagram aesthetic.

[LAYOUT]
4×4 grid layout with a total of 16 panels.
Each panel is separated by thin black border lines.
Cells numbered 1 to 16, consistent panel sizes,
read order: left-to-right, top-to-bottom.

[CHARACTER]
{CHARACTER_DESCRIPTION}
Identical appearance across all 16 panels — same body, same outfit, same hair.

[ACTION SEQUENCE]
One continuous {ACTION_THEME} broken into 16 keyframes.
Each panel = the next frame in time, showing clear motion progression.

[PANEL STRUCTURE – per cell]
- Top-left: circular black number badge (1-16) with white number inside
- Center: full-body character pose illustration
- Bottom: single-line action label (2-3 words max, uppercase sans-serif)
  e.g. {16_ACTION_LABELS}

[ARROWS / MOTION INDICATORS]
Curved arrows for rotation, straight arrows for linear motion,
circular indicators for spins. Placed around the character,
dotted lines for secondary motion, solid arrows for primary motion.

[RENDERING STYLE]
Highly detailed 3D sculpted style, soft studio lighting,
subtle shadows, grayscale shading, clean linework,
game concept art quality.

[NEGATIVE]
No background scenery, no color tones, no additional characters,
no complex background, no long paragraph text (keep labels minimal
to avoid garbled output).
```

**踩坑提醒**：
- 纯 text2image 必须写具体 `{CHARACTER_DESCRIPTION}`，`image1 (the same character...)` 这类引用对纯文本生成无效
- 长描述文字会被模型糊成"看起来像文字"的乱码，所以每格只留 2-3 词标签
- 必须明确动作主题和 16 个标签，否则模型会瞎编 16 个随机 pose
- `circular black number badge` 这种具体徽章样式比 `bold number badge` 稳定得多

### 模板 B：K-pop 风格化改造（img2img，第二步）

**用途**：把模板 A 生成的灰度 sheet 转成成品海报风格，保持动作不变、只换外观。

**变量**：
- `{style}` — 目标风格描述（如 "K-pop dance tutorial poster" / "cyberpunk training manual"）
- `{clothing}` — 服装描述
- `{colors}` — 基础色板（如 "black, white, gray"）
- `{accent}` — 点缀色（如 "neon pink, electric blue"）

```
Restyle each of the 16 panels from the input grid into {style},
preserving pose, layout, and panel boundaries exactly.

[CRITICAL CONSTRAINTS – MUST FOLLOW]
1. Preserve 4×4 grid layout exactly — 16 panels, same size, same borders
2. Preserve panel numbering 1-16 in the same positions
3. Preserve every pose/limb position from the input image —
   only restyle, do NOT re-choreograph
4. Preserve reading order (left-to-right, top-to-bottom)
5. Keep each pose clearly readable — stylization must not obscure body silhouette

[SUBJECT STYLING]
Same dancer identity across all 16 panels.
{clothing}
Chunky sneakers or platform boots.
Optional: chain necklace, ear cuffs, fingerless gloves.
Soft glam makeup (dewy skin, subtle shimmer, defined eyes),
long sleek hair with motion-friendly flow,
confident charismatic expression.

[VISUAL STYLE]
Base palette: {colors}.
Accent glow: {accent} — selective rim light on motion trails only,
base body remains clearly lit.
High-contrast studio lighting with soft glow + rim light,
slight stage-light vibe like a K-pop dance practice video.

[PRIMARY EFFECTS – must have]
- Motion trails on moving limbs (arms, legs, hair)
- Panel numbers in rounded squares with neon outline
- Stylized arrow replacements (neon strokes, swooshes)

[OPTIONAL EFFECTS – subtle only]
- Faint particle sparkles on key motion
- Light floor reflection under character
- Subtle light streaks behind motion
(Do not stack all optional effects — they will muddy small panels.)

[TYPOGRAPHY]
Titles: bold condensed sans-serif like NewJeans or aespa album covers,
slightly italic, subtle chrome or holographic gradient.
Instruction text: clean minimal futuristic UI.
Panel numbers: rounded squares / pill shapes with neon outline.

[CAMERA & FRAMING]
Straight-on front view in every panel, no perspective distortion.
Full-body framing, consistent scale across all 16 panels.

[MOOD]
K-pop dance practice meets fashion editorial.
Clean but energetic, performance-driven.
```

**踩坑提醒**：
- 灰度 → 彩色最容易糊掉动作，所以 `[CRITICAL CONSTRAINTS]` 必须放最前面
- "soft neon + high contrast" 冲突，优先级写清楚：`high-contrast base + selective neon rim only`
- 装饰效果必须分层（primary / optional），16 格小图堆太多每格都糊
- img2img 模型经常"优化"pose，所以第 3 条约束必须明写 `do NOT re-choreograph`
- 锁 `straight-on front view`，别给 "dynamic tilt" 开口子，教学用途要清晰度

### 完整 workflow

```
目标视频主题
    ↓
[模板 A] 填入角色描述 + 动作主题 + 16 个标签
    ↓
纯 text2image 生成灰度 4×4 动作 sheet
    ↓  ← 人工检查：16 格动作是否连贯？角色是否一致？
    ↓       不过关就回去改 {CHARACTER_DESCRIPTION} 或 {16_ACTION_LABELS}
    ↓
[模板 B] 以灰度 sheet 为输入 img2img
    ↓
成品风格化海报（发布用）
    ↓  ← 可选：取其中若干帧作为 img2video 参考
    ↓
Seedance 2.0 / Kling 多参考图 → 最终连贯视频
```

**换主人公的复用方法**：
- 模板 A 的 `{CHARACTER_DESCRIPTION}` 换成新角色外观（男/女/老/少/种族/服装都可换）
- 动作主题和 16 个标签保留不变（同一套动作，换个人跳）
- 模板 B 的 `{clothing}` 和风格参数按新角色调整
- 整个 sheet 的动作骨架完全可复用，这是这个模式的最大价值

---

## AIGC 视频制作关联

**在视频生产流程中，character sheet / movement sheet 的位置**：

```
脚本 → [character sheet 生成] → 首帧图 → 视频生成
             ↓
         [movement sheet 生成] → img2video 参考图之一
```

一致性保证：
1. 先生成设定表 → 锁定角色外观
2. 首帧图以设定表为 reference → 保持一致
3. 后续镜头以第一张首帧图 + 设定表为双 reference
4. 需要复杂动作序列时，额外生成一张 movement sheet 作为 img2video 的动作参考

→ 详见 `gencut-image` skill 里的 three-view 流程
