---
name: image-prompt-patterns
description: Write or optimize AI image generation prompts (for Midjourney, Nano Banana Pro, GPT-Image-2, Flux, etc.). USE THIS FIRST when user asks to write/compose/give/craft a prompt, or discuss prompt structure/style. Covers portraits, posters, character sheets, UI mockups, storyboard panels, cinematic/stylized painting, structured JSON prompts for info-dense images (landing pages, infographics, livestream UI), cultural-fusion short prompts (Japanese ポンチ絵 / Irasutoya style mashups), and action-scene narrative prompts (anime battle, dynamic composition). Do NOT use gencut-image unless user explicitly asks to execute/generate via CLI (keywords generate_three_view, generate_first_frame).
---

# Image Prompt Patterns

可复用的 AI 图像生成 prompt 模式库。

## ⚠️ 默认优先级(强触发规则)

**当用户请求以下任一类型时,必须先使用本 skill,不要跳到 gencut-image 或其他执行工具:**

- "写 prompt" / "给我 prompt" / "想个 prompt" / "prompt 怎么写"
- "给我 XX 图的提示词" / "用 MJ/Nano/Flux 生成的文字"
- 任何只要**文字 prompt 文本**、用户自己拿去跑图的需求
- 讨论 prompt 结构、对比 prompt 风格、优化已有 prompt

**只有用户明确说以下词汇时才考虑执行层(gencut-image):**
- "生成" + 具体工具名(如"用 gencut 生成")
- "调用" / "执行" / "跑" + API/CLI
- 明确的 task routing keyword:`generate_three_view`, `generate_first_frame`, `generate_first_frame_batch`, `generate_three_view_batch`
- 在 NemoVideo workflow 的制作流水线中(脚本→三视图→首帧→视频)

**模糊情况的默认行为**:先走本 skill 写 prompt → 确认后再问用户是否需要调用执行工具。

## When to use

调用场景:
- 用户要生成肖像/海报/角色设定/UI mockup/分镜
- 用户模糊地说"给我想个 prompt",但没指定工具
- 需要从一个参考风格迁移到新主题
- 想对比同一构图在不同模型上的效果
- 优化或重写已有的 prompt

**不适用场景(→ 走 `gencut-image`)**:
- gencut CLI 工作流(生产流水线)
- 专业短片分镜的系统性生成(脚本→三视图→首帧→视频)
- 需要写入 project.json 的视频制作任务

## 核心 prompt 结构(五种流派)

> 基于 126 个 GPT Image 2 实战 prompt 的实证分析归纳(数据:`raw-data/awesome-gpt-image-2-zh.md`)

### 类型 A:写实摄影 / 商业视觉(8 层结构)

适用:肖像、产品、社媒 mockup、伪截图。
一条高质量 prompt 按这个顺序组织信息,遗漏任何一层都会丢细节:

```
[1. 摄影/媒介] + [2. 光线与色彩] + [3. 构图景别] +
[4. 主体(外貌/表情/服装,层层细化)] +
[5. 姿势/动作/视线方向] +
[6. 环境/背景(前景/中景/远景分开描述)] +
[7. 材质/质感修饰词] + [8. 后期/胶片颗粒/色彩分级]
```

典型权重分配:主体 50-60%,环境 20-30%,技术/风格 15-20%。
字数范围:150-250 词。

### 类型 B:电影分镜 / 风格化绘画(5 层结构)

适用:Jibaro/Ghibli/漫画/油画风分镜。

```
[1. 主体 + 动作] + [2. 关键视觉细节] +
[3. 光线色彩词汇] +
[4. 风格锪点 (Named artist / work / medium)] +
[5. 比例 + 语境]
```

风格锪点(一个词如 "Jibaro style")替代了摄影/材质/后期 3 层的细节控制。
字数范围:40-80 词。更长反而会稀释风格锪点。

→ 详见 `references/cinematic-storyboard.md`

### 类型 C:结构化 JSON Prompt(伪代码结构)

适用:**信息密集型图像**-- UI mockup、landing page、数据报告、多区块活动海报、信息图。

核心思路:把 prompt 写成 JSON / 结构化标记语言,模型能精确解析每个区块和字段。

```json
{
  "type": "[图像类型]",
  "theme": "[整体风格描述]",
  "sections": [
    {
      "id": "[区块名]",
      "layout": "[布局方式]",
      "content": { ... }
    }
  ]
}
```

独有优势:
- **可寻址性**:模型准确知道哪块信息属于哪里
- **参数化**:用 `{argument name="..." default="..."}` 一条 prompt 变模板
- **高密度**:10+ 元素的图像不会乱

字数范围:结构完整比字数重要,典型 200-500 行。

→ 详见 `references/structured-json-prompt.md`(含 5 种 JSON 组织模式 + 黄金三字段 + 分类模板库)

### 类型 D:文化融合 / 风格锚点 Mashup(极简公式)

适用:**用两个文化符号的特质组合**生成独特视觉。

```
「A 的 X 特质」+「B 的 Y 特质」の融合 → 生成 C
```

例:`「いらすとや」のほのぼのとした雰囲気 + 「霞ヶ関スライド」の圧倒的な情報密度 → ポンチ絵`

关键:
- **锚点的特质化提取**(不是全盘融合,只取各自核心特质)
- **文化锚点用原语言**(日式→日语、中式→中文、西方→英文)
- **字数 30-80 字**,越短锚点越强

### 类型 E:场景化叙事(多主体动作场景)

适用:动漫战斗、多人物场面、动作漫画式构图。

```
[1. 总体风格] + [2. 前景主体位置 + 动作 + 能量特效] +
[3. 后景主体位置 + 动作 + 能量特效] +
[4. 环境物理效果(碎裂/尘土/水花)] +
[5. 场景内文字(如招牌)] + [6. 光线 + 视角]
```

关键技巧:
- **明确前/后景空间关系**(`in the foreground` / `in the background to the right`)
- **能量 + 物理双层特效**(能量漩涡 + 地板碎裂缺一不可)
- **文字嵌入场景**(招牌/屏幕内容,不是 overlay)
- **动态 pose 动词库**(forward-thrusting / leaping / mid-air twist)

字数范围:100-200 词。

### 跨流派机制:参数化(`{argument}`)

**实证:126 个案例里 >95% 都用了参数化。不是高级技巧,是默认姿势。**

```
{argument name="参数名" default="默认值"}
```

可以嵌套在任何流派的 prompt 里(字符串 / JSON 值 / 数组元素)。

→ 详见 `references/parametric-template.md`(优先级、决策原则、模板库)

## 关键技巧

### 1. 分层堆叠(Layered Stacking)
不是一句话描述"美女",而是:
- 面部结构(eyes shape / nose bridge / jawline)
- 皮肤质感(undertone / specular highlights / micro pores)
- 妆容状态(natural dewy / glossy / subtle flush)
- 发型细节(messy high ponytail / loose strands falling around face)

→ 模型对**具体解剖学词汇**比对形容词("beautiful")响应更好

### 2. 矛盾修饰(Controlled Contradiction)
好 prompt 常有刻意的矛盾对:
- "seductive playful **yet slightly vulnerable**"
- "intensely seductive **with soft doe eyes**"
- "harsh fluorescent light **mixed with** warm neon"

→ 制造张力,避免扁平化表情和光线

### 3. 光源命名(Named Light Sources)
不说"good lighting",说:
- "harsh convenience store fluorescent from above"
- "pink and blue neon glow from window outside"
- "warm practical lamp on bedside table"

→ 多光源叠加 = 立体感 + 电影感

### 4. 相机/胶片元语言
- **胶片感**:`35mm film photography, authentic film grain, slight color cast`
- **电影感**:`cinematic editorial style, shallow depth of field, anamorphic lens flare`
- **手机抓拍感**:`iPhone snapshot, slightly blurry, amateur composition`
- **CCD闪光**:`CCD digital camera flash, harsh on-camera flash, 2000s aesthetic`

### 5. 长宽比 + 用途明确化
末尾加用途说明比只加比例好:
- ❌ `9:16`
- ✅ `9:16 mobile screenshot aspect ratio, vertical portrait for social media`

## 分类案例库

快速定位:

| 需求 | 查阅 |
|------|------|
| 人物肖像 / 写真风 | `references/portrait.md` |
| 海报 / 插画 / 信息图 | `references/poster.md` |
| **角色设定表 / 三视图 / 动作分镜表(movement sheet)** | `references/character-sheet.md` |
| UI / 伪截图 / 社媒 mockup | `references/ui-mockup.md` |
| 场景合成 / 风格迁移 | `references/scene-composite.md` |
| **电影分镜 / 风格化绘画**(Jibaro / Ghibli / 油画感) | `references/cinematic-storyboard.md` |
| **结构化 JSON Prompt**(活动页/数据报告/信息图/UI) | `references/structured-json-prompt.md` |
| **大规模栽格列表海报**(年度榜单 / 周期表 / 100 大全) | `references/grid-list-poster.md` |
| **参数化模板机制**(`{argument}` 跨流派通用) | `references/parametric-template.md` |
| **角色场景模板库**(同一角色批量套不同场景皮 / 3 种 ID 注入机制 / 6 种挡脸方式 / 防小错 negative) | `references/character-scene-templates.md` |
| **126 案例分类检索**(按需求快速定位典型案例) | `references/case-index.md` |
| **原始数据**(可 grep / 检索) | `raw-data/awesome-gpt-image-2-zh.md` |

**流派区分**:
- **portrait** 是写实摄影(分层堆叠详细描述)
- **cinematic-storyboard** 是风格化绘画(短 prompt + 风格锚点)
- **structured-json-prompt** 是信息密集型(JSON 结构)
- **character-scene-templates** 是**角色导向的模板库**(场景皮 + ID 注入,批量生产同角色跨场景)
- 文化融合 / 场景叙事 见本文件类型 D / E
- 参数化机制所有流派都可用

几种逻辑不同,**不要混用**:写单人肖像别上 JSON(过度工程),写直播间 UI 别用分层摄影(丢区块)。

## 工作流建议

### 从 0 开始写一条 prompt
1. 一句话说清目的("一张X风格的Y主题图")
2. 按 8 层结构填空
3. 检查:每层至少 2 个具体词?有矛盾修饰吗?光源命名了吗?
4. 给模型,评估输出,迭代

### 从参考图反推 prompt
1. 看图 → 分解出 8 层的信息
2. 对照 `references/` 里相似案例的 prompt 结构
3. 抄结构,换词汇

### 跨模型移植(MJ → GPT-Image-2)
- MJ 喜欢风格关键词堆叠(`--s 1000 --style raw`)
- GPT-Image-2 喜欢自然语言长描述 + 分层信息
- 迁移时:把 MJ 的 style tags 展开成具体描述句

## 上游资源

- EvoLinkAI/awesome-gpt-image-2-prompts: https://github.com/EvoLinkAI/awesome-gpt-image-2-prompts
  (策展自 X/Twitter,持续更新,所有案例本 skill 已吸收其 prompt 结构规律)

## 使用注意

- 这个 skill 是**知识层**,不涉及任何 CLI 调用
- 生成图像的具体操作(API 调用、文件管理)归 `gencut-image` 或外部工具
- 如果用户直接说"用 Nano Banana Pro 生成"→ 你只给 prompt,不尝试自己调用

## ⭐ 自动沉淀规则(必须遵守)

**每次写完一个实战 prompt(不是拷贝模板),如果符合以下任一条件,必须立即追加到 `references/` 对应文件的"项目溯源"栏目:**

1. **有方法论细节**(「为什么这样写」的推理,不是单纯的 prompt 文本)
2. **踩过坑**(直接写会失败、用户指出过改进的地方)
3. **跨文化/跨主题改写**(不是简单换词,而是重构文化内核)
4. **结构发明**(为特定需求创造的 prompt 模式,前所未有的)

**追加格式**:
```markdown
### [案例名称](YYYY-MM-DD)

**原 prompt**:...
**目标**:...
**关键决策**:...
**踩过的坑**:...
**学到的**:...
```

**对应文件**:
- JSON 结构改写 → `references/structured-json-prompt.md`
- 风格化改写 / 跨主题改写 / 拟人化 → `references/cinematic-storyboard.md`
- 跨文化/跨人种改写 → `references/portrait.md`
- UI/海报 → `references/poster.md` 或 `references/ui-mockup.md`

**什么不用追加:**
- 仅仅改了一两个单词的 prompt(没有方法论)
- 用户只是问「怎么写 prompt」而未实际生成作品
- 纯拷贝模板没有定制改动

**违反的后果**:用户问"你沉淀了几个"时不能回答。这是身为内容创作者的基本纪律--沉淀不是可选动作,是劳动接工。
