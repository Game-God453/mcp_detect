# Structured JSON / Pseudo-Code Prompt Patterns

> 基于 126 个 GPT Image 2 实战 prompt 的结构分析（数据来源：youmind.com / YouMind-OpenLab GitHub 仓库）

## 什么时候用

**信息密集型图像**——画面里有 5+ 个独立信息区块、需要精确控制文字内容、需要跨区块的位置关系。

✅ **必用场景**：
- Landing page / 产品落地页 mockup
- 直播间 UI / 电商详情页 / 社媒 UI 截图
- 数据报告 / 信息图 / 教育视觉图
- 多格网格（2x2 / 3x3 / 4 格广告位）
- YouTube 缩略图（主体 + 文字 + 装饰）
- 漫画多格故事板
- 产品爆炸视图 / 解剖图

❌ **不用场景**：
- 单人物肖像、单风景 → 写实摄影分层（portrait.md）
- 艺术画作、风格化分镜 → 自然语言 + 风格锚点（cinematic-storyboard.md）
- 50 字以内能说清的 → JSON 过度工程

---

## 散文 vs JSON：实证对照（2026-04-25 旅行海报案例）

Neal 同日投了两个 prompt，**同一作者、同一流派、两种写法**，天然的 AB 测试：

### 对照表

| 维度 | Switzerland 版（散文式）| New Zealand 版（JSON 式）|
|------|----------------------|------------------------|
| 格式 | 自然语言 | JSON 结构化 |
| 字数 | ~500 词 | ~250 词 |
| Argument 数 | 3 | 5 |
| Argument 覆盖率 | ~3% | ~15% |
| 城市总数 | 12 | 10 |
| 地图分层 | ❌ 无 | ✅ north_island / south_island |
| Landmark 描述 | "churches, towers, castles"（泛化）| "Sky Tower near Auckland"（具名+锚定）|
| 动态元素 | "two red trains moving"（藏在描述里）| 缺失 |
| 可读性 | 散文拖沓，字段隐含 | 骨架清晰，字段显式 |

### 关键结论

**同信息量 × JSON 结构**：
- 字数减半（500 → 250）
- Argument 数几乎翻倍（3 → 5）
- 地理分层天然浮现（散文想不到要拆北岛/南岛，JSON 一列字段就拆了）
- Landmark 可控性大幅提升（散文里 "landmark buildings" 模型乱生成，JSON 里按"X near Y"格式模型精确摆放）

### 推论：什么时候必须用 JSON

强制 JSON 的信号：
- 要 argument 化 / 模板化 / 批量生成
- 元素之间有**空间关系**（位置 / 邻近 / 包含）
- 元素之间有**数据关系**（城市→景点 / 章节→条目）
- 需要精确**数量控制**（exactly 12 cities / 4 crystals / 3 dynamics）
- 需要**跨地域 / 跨主题本土化**

散文勉强够用的信号：
- 一次性出图，不模板化
- 单一视觉主题，元素独立
- 风格重于结构（"Jibaro 风格分镜"这种锚点主导的 prompt）

**直接升级**：如果你拿到一个散文 prompt 要做产品化，第一步就是**把它改成 JSON 骨架**。这个工作量小，收益大。

---

## 数据实证：黄金三字段

分析 71 个真实 JSON prompt，**最核心 3 个字段**：

| 字段 | 出现率 | 作用 |
|------|--------|------|
| `type` | **100%（71/71）** | 图像类型分类，第一个字段 |
| `layout` | **75%（53/71）** | 布局结构，描述空间组织 |
| `style` | **41%（29/71）** | 整体风格、色调、质感 |

**其他高频字段（>10 次）**：`theme` / `header` / `character` / `subject` / `background`

---

## 五种 JSON 组织模式

基于真实案例归纳，JSON prompt 的结构**不是统一的**，按图像需求选用对应模式：

### 模式 1：顺序串珠（Sequential Sections）

**适用**：多区块顺序展示型图像（落地页、长图）

```json
{
  "type": "...",
  "sections": [
    {"id": "hero", ...},
    {"id": "features", ...},
    {"id": "cta", ...}
  ]
}
```

顶层 `sections` 数组，对应画面从上到下的区块顺序。代表案例：goViralX 病毒式营销落地页、护肤电商详情页。

---

### 模式 2：中心星图（Hub + Callouts）

**适用**：解剖图、爆炸视图、中心 + 环绕标注

```json
{
  "type": "...",
  "layout": {
    "centerpiece": "...",
    "callout_labels": {
      "count": N,
      "left_side": [...],
      "right_side": [...]
    }
  }
}
```

一个 centerpiece + 对称分布的 callouts。代表案例：Meta Quest 爆炸图、相机解剖图、医疗信息图。

---

### 模式 3：并行数组（Parallel Arrays）

**适用**：项目列表型图像，视觉和文字一一对应

```json
{
  "sections": [
    {
      "count": 12,
      "illustrations": ["img1", "img2", ...],
      "labels": ["label1", "label2", ...]
    }
  ]
}
```

`illustrations[i]` 对应 `labels[i]`。模型自己配对。代表案例：成都吃货地图、服装工艺流程图。

---

### 模式 4：九宫格位置编码（Position-Named Fields）

**适用**：UI mockup（直播间/社媒/APP）、固定屏幕布局

```json
{
  "subject": {...},
  "ui_overlay": {
    "top_header": {...},
    "mid_left_gifts": {...},
    "bottom_left_chat": {...},
    "bottom_right_product_card": {...},
    "bottom_bar": {...}
  }
}
```

字段名**直接编码位置**：`top_*` / `mid_*` / `bottom_*` + `_left`/`_right`/`_center`。不需要额外 position 字段。代表案例：马斯克直播间、抖音电商 UI。

**subject + ui_overlay 双层结构**是 UI 类图像的标志——底层实景 + 界面叠加。

---

### 模式 5：改造指令型（Transformation）

**适用**：图生图、基于参考图改造

```json
{
  "type": "...",
  "instruction": "Using REFERENCE_0 as base, transform A into B, replace X with Y, upgrade Z to W.",
  "style": {
    "background": "...",
    "subjects": "..."
  },
  "layout": {...}
}
```

核心是 `instruction` 字段 + `REFERENCE_N` 占位符。`style` 变成**元素级风格配置表**（每个元素独立指定风格）。代表案例：3D 石阶演化信息图。

**改造动词库**：transform / replace / upgrade / preserve / remove / add / enhance。

---

### 模式 6：批量 UI 元素（Count + Desc）

**适用**：UI mockup / 社交媒体截图 / 电商直播界面——画面上有**大量类似的重复元素**（聊天列表、评论区、礼物条、菜单项、控件按钮）。

```json
{
  "chat": {"pos": "left", "count": 15, "desc": "colored usernames, white text"},
  "controls": {"count": 10},
  "gift_popups": {"count": 3, "pos": "center", "desc": "large golden gift animations with usernames"}
}
```

**三要素**：
- `count`：数量（给模型一个硬数字，能防生成太多或太少）
- `desc`：单体模板（见 desc 知元素长什么样）
- `pos`：位置（可选，但建议写）

**为什么有效**：
- 不必逐条列 15 个用户名——节省 token + 避免重复
- 模型每次生成 **细节细微不同**，反而更像真实 UI——真直播聊天就是每秒都在变
- **全参数化变得很轻**：`count` 和 `desc` 两个字段就能控制整个批量层

**不适用的情形**：
- 需要**特定内容**的批量元素（例如指定某个用户名必须出现 → 这个要独立写）
- 重复元素之间**有分层关系**（例如 置顶评论 vs 普通评论 → 拆成两个 count 或单独列置顶的）

**实战模板**：
```json
// 直播聚合
"chat_scroll": {"count": 12, "pos": "right", "desc": "rapid chat messages with emojis"}
"viewer_avatars": {"count": 8, "pos": "top", "desc": "circular avatar row"}

// 电商产品格
"product_cards": {"count": 6, "layout": "2x3 grid", "desc": "white cards with price tags"}

// 菜单项
"sidebar_items": {"count": 7, "pos": "left", "desc": "icon + label rows"}

// 批注标签
"hashtag_chips": {"count": 5, "pos": "under title", "desc": "rounded tags in brand color"}
```

**代表案例**：No. 22 Douyin / No. 66 YouTube 直播 / No. 69 YouTube Live / No. 70 网红直播。根据 2026-04-24 Neal 投的 YouTube Premium 直播 meme mockup 提炼。

---

### 模式 7：大规模栽格列表（Grid-List）

**适用**：年度榜单 / 工具大全 / 周期表 / 领域地图 / 人物合集——**一张图展示几十到几百个具名实体**。

```json
{
  "type": "grid-list infographic poster",
  "layout": {
    "grid": {"columns": 10, "rows": 10, "cell_count": 100, "numbering": "1—N at top-left"},
    "left_sidebar": {"count": 10, "labels": ["..."]},
    "sections": [{"title": "...", "count": 10, "labels": ["A","B","C",...]}]
  },
  "logo_treatment": "simplified recognizable, brand colors, consistent scale",
  "rendering_notes": "symmetrical, social-media-shareable"
}
```

**与模式 6 (count + desc) 的区别**：
- 模式 6：批量元素**不具名**（15 条随机聊天）
- 模式 7：批量元素**每个有独立 label**（100 个具名公司）

**四条可复制原理**（完整分析见 `grid-list-poster.md`）：
1. **双轴语义**：栽格 + sidebar = 隐式表格
2. **传播机制字段**：numbering 让静态图有归属性（“我说 #47”）
3. **Logo 四约束**：simplified / recognizable / brand colors / consistent scale
4. **default 值为数组**：`default=["A","B","C"]` 一条 argument 管 10 个实体

**代表案例**：
- 2026-04-24 Neal 投的 "AI COMPANIES IN 2026" 10×10 海报——本模式首批案例。
- 待补：Pokemon periodic table / YC 校友墙 / ML 算法图谱。

---

### 模式 8：组件清单式批量（Component List）

**适用**：UI kit / Design System board / 图标套件展示——画面上铺满"这几类组件"但每个组件是**类型**而非**实体**。

```json
"sections": [
  {
    "title": "UI ELEMENTS",
    "position": "upper center-right",
    "count": 7,
    "labels": ["CTA button", "rounded tab 1", "horizontal slider", "toggle switch", "theme pill 1", "theme pill 2", "icon button"]
  }
]
```

**与模式 6（count + desc）/ 模式 7（grid-list）的区别**：

| 模式 | 批量元素性质 | 例子 |
|------|------------|------|
| 6 count + desc | 不具名批量 | 15 条随机聊天 |
| 7 grid-list | 具名实体批量 | 100 家具名公司 |
| 8 组件清单 | 具名类型批量 | 7 种 UI 组件类型 |

**核心特征**：labels 里的名字是**"我想看到什么组件"**而不是**"这是哪个具体实例"**。模型负责具体渲染每种组件的形态（颜色/圆角/文字），你负责给清单。

**代表案例**：2026-04-24 Neal 投的 "COSMIC GRAVITY design system board"——6 个 sections × 平均 5-7 个组件 = 铺满整个展板。

---

## 字段设计技巧（跨模式通用）

### 技巧 1：style 字段的四层拆解

**反例**（写一句散文）：
```json
"style": "luxury sci-fi glassmorphism with warm highlights and cool accents"
```

**正例**（四层结构）：
```json
"style": {
  "background": "near-black matte canvas with subtle starfield haze",
  "lighting": "soft shadows, faint bloom, warm amber highlights, cool blue-violet accents",
  "material": "frosted glass, glossy dark surfaces, thin luminous strokes, soft refractions",
  "mood": "luxury sci-fi, minimal, cinematic, highly polished"
}
```

**四层各自的职责**：
- `background` — 大面积底色 / 基础画布
- `lighting` — 光源方向 / 反射 / 发光
- `material` — 物体质感 / 表面特性
- `mood` — 情绪锚点 / 气质定位

**为什么有效**：模型对"视觉风格"的理解力有限，一句散文里模型会挑词理解。四层结构让模型在**每个决策维度独立做选择**，不会互相干扰。

### 技巧 2：centerpiece 作为视觉概念锚

独立字段，一句话描述**整体视觉概念**：

```json
"centerpiece": "a dense arrangement of translucent dark cards and controls floating on a black canvas, organized like a premium design system poster"
```

**不是**放在 `layout.description` 里。单独挑出来让模型优先级处理。

**判断标准**：如果画面有一个**整体视觉母题**（"奢华仪表盘"/"杂志拉页"/"烹饪流程图"），独立 centerpiece 字段；如果是**多元素并列**（"4 格漫画"/"100 公司栅格"），不需要 centerpiece。

### 技巧 3：视觉现象 vs 概念名

**反例**：`"black hole"` / `"sunset"` / `"battle scene"`
**正例**：`"dark circular center with bright accretion-like ring"` / `"gradient from warm peach to faded lavender-gold at horizon"` / `"two figures in mid-motion with impact dust cloud"`

**原则**：模型对"视觉描述"比对"概念名称"可靠得多。关键视觉元素（尤其不常见的抽象概念）应写**视觉现象**，不依赖概念理解。

### 技巧 4：关键数字显式写死

UI mockup / 信息图 / 海报类 prompt 里，**具体数字 + 单位必须写死**，否则模型生成胡话数字。

```json
"percentage": "87%",
"distance": "779.3 M km",
"price": "$2,499",
"metric": "+23.4%"
```

参数化用 argument，不要让模型"自己想一个"。

---

## 按图像类型的结构签名（实证）

> 基于 71 个 JSON prompt 的字段组合统计，每种图像类型有自己的典型字段集。

### 🎭 人像 / 头像（profile-avatar）

**典型签名**：`character + layout + style + type`

常见变体：
- 单人肖像：`character + setting + type`
- 角色网格：`count + portraits + layout + style + theme + type`
- 表情网格：`character_base + common_theme + layout + style + type`

**character 字段子结构**：
```json
"character": {
  "appearance": "描述外貌",
  "outfit": "服饰",
  "hair": "发型",
  "eyes": "眼睛特征",
  "pose": "姿势",
  "description": "综合描述"
}
```

---

### 📱 YouTube 缩略图 / 直播封面

**典型签名**：`character + layout + style + type`

额外常见：`background + character + type + typography_and_ui`（包含专门的排版/UI 字段）

缩略图的关键是**文字占据大面积**——`typography_and_ui` 字段统一管理：主标题、副标题、装饰文字、UI 元素。

---

### 💬 社交媒体 / 电商直播 UI

**典型签名**：`subject + type + ui_layout` 或 `layout + type`

**UI 类专属模式**：双层叠加（模式 4 星图位置编码）
- 底层：`subject`（实景人物/产品/背景）
- 上层：`ui_overlay` / `ui_layout` 用九宫格字段命名

电商主图常见附加字段：`product + scene + ui_overlays + typography`

---

### 📊 信息图 / 教育视觉图

**典型签名**：`centerpiece + header + layout + style + subject + type`

`centerpiece` 是信息图的核心字段（非 UI 类可以用到）：
```json
"centerpiece": {
  "description": "中心视觉核心描述",
  "count": 13,
  "central_list": {
    "type": "numbered steps with pointer lines",
    "labels": ["01 Material", "02 Inspiration", ...]
  }
}
```

信息图常用的 `layout.left_column` / `layout.right_column` 双栏模块结构：
```json
"left_column": [
  {
    "module": "MODULE 1: RAW MATERIAL",
    "count": 6,
    "items": ["Fiber", "Yarn Structure", ...]
  }
]
```

---

### 🛍️ 产品营销 / 品牌设计

**典型签名**：`brand + color_palette + layout + type`

品牌设计板（Brand Identity Board）额外字段：
- `branding`（logo 规范）
- `character`（吉祥物 / 品牌形象）
- `theme`（主题色/调性）

**color_palette** 字段的典型写法（数组而非字符串）：
```json
"color_palette": [
  {"name": "Primary", "hex": "#FF6B35"},
  {"name": "Accent", "hex": "#004E89"}
]
```

---

### 🎨 漫画 / 故事板

**典型签名**：`characters + layout + style + type`（注意是复数 characters）

**多格漫画专用**：`panels` 数组
```json
"panels": [
  {
    "position": "top-left",
    "scene": "...",
    "subject": "...",
    "details": "...",
    "dialogue": "..."
  }
]
```

跨格元素用 `global_elements` 字段（如整页背景、边框）。

---

### 🎮 游戏素材

**典型签名**：`character + environment + perspective + type + ui_elements`

独特字段：
- `perspective`（视角，如 "isometric" / "top-down" / "third-person"）
- `environment`（场景环境）
- `ui_elements`（HUD / 菜单元素）

---

## Layout 字段的值词汇表（实证）

基于 147 个真实 `layout` 值统计出的高频关键词：

### 位置词（最高频）
- **中英文混用**很普遍。中文位置词效果不输英文。
- 基本盘：`top` / `bottom` / `left` / `right` / `center` / `middle` / `mid`
- 中文对应：`左上角` / `右下角` / `左下角` / `右上角` / `底部中心` / `左侧边栏`
- 组合：`top-left` / `top-right` / `bottom-left` / `bottom-right`
- 网格词：`row` / `grid` / `panels`

### 常用 layout 值模板
```
"2x2 equal quadrants"
"3x3 character expression grid"
"7 columns with 9 elements each"
"left sidebar + right main + bottom caption"
"centered hero + 4 surrounding callouts"
"numbered steps with pointer lines"
"dashed border grid"
"exploded vertical stack"
"curved path with waypoints"
"diagonal split composition"
```

### Position 字段与 Layout 字段的区别
- `layout`：**全局或每块的结构说明**（如 "3 columns"）
- `position`：**元素在父容器里的位置**（如 "top-left"）

两种写法二选一：
1. 字段名编码位置（`top_header`, `bottom_right_xxx`）——适合 UI 类
2. 显式 `position` 字段——适合内容章节可重排的场景（漫画、信息图）

---

## 参数化 `{argument}`（跨流派机制）

**重要发现**：126 个真实 prompt 中，**52/55 个自然语言 prompt 都用了 `{argument}`** —— 参数化不是 JSON 专属，是一种跨所有流派的通用机制。

### 基本语法
```
{argument name="参数名" default="默认值"}
```

### 参数化的黄金部位
统计真实案例，最常被参数化的维度：

| 优先级 | 维度 | 例子 |
|------|------|------|
| ★★★ | 主题 / 角色名 | `{argument name="character name" default="Elon Musk"}` |
| ★★★ | 文案 / 标题 | `{argument name="hero headline" default="..."}` |
| ★★★ | 颜色 / 配色方案 | `{argument name="color theme" default="red and white"}` |
| ★★ | 场景 / 地点 | `{argument name="setting" default="dojo"}` |
| ★★ | 动作 / 状态 | `{argument name="action type" default="..."}` |
| ★★ | 产品名 / 品牌 | `{argument name="product name" default="Meta Quest 3"}` |
| ★ | 风格 / 材质 | `{argument name="art style" default="watercolor"}` |
| ★ | 背景 / 色调 | `{argument name="background" default="..."}` |

### 什么不要参数化
- 构图骨架（如 `"layout": "2x2 grid"`）
- 错误防御词（如已测试过的灵线故定）
- 中文文字的或左右分栏这些结构性字段

**原则**：参数化只用于"批量换不会崩掉核心效果"的部分。

---

## 按类型的模板库（全部基于真实案例提炒）

### 模板 A：直播间 UI mockup

```json
{
  "type": "live stream UI mockup",
  "subject": {
    "description": "主播人物描述",
    "background": "环境描述"
  },
  "ui_overlay": {
    "top_header": {
      "host_info": "头像 + 名字 + 按钮",
      "rank_badge": "排名标签",
      "viewer_stats": "在线人数",
      "right_links": "右侧菜单"
    },
    "mid_left_gifts": {
      "count": 2,
      "items": ["...", "..."]
    },
    "bottom_left_chat": {
      "system_message": "...",
      "message_count": 7,
      "messages": ["用户: 内容", ...]
    },
    "bottom_right_product_card": {
      "hot_tag": "...",
      "image": "...",
      "title": "...",
      "price": "...",
      "button": "..."
    },
    "bottom_bar": {
      "input_field": "...",
      "icons": ["icon1", "icon2", ...]
    }
  }
}
```

---

### 模板 B：产品爆炸视图海报

```json
{
  "type": "产品爆炸视图海报",
  "subject": "产品名",
  "style": "3D 渲染 + 发光装饰",
  "background": "渐变色",
  "header": {
    "logo": "品牌 Logo",
    "subtitle": "主标语"
  },
  "layout": {
    "centerpiece": "爆炸视图描述，N 个部件垂直/璃瑰堆叠",
    "callout_labels": {
      "count": 8,
      "left_side": ["部件名\\n功能描述", ...],
      "right_side": ["...", ...]
    },
    "footer": {
      "left_text_block": {"headline": "", "body": ""},
      "right_logo": ""
    }
  }
}
```

---

### 模板 C：信息图（中心 + 双栏）

```json
{
  "type": "infographic poster",
  "header": {
    "main_title": "...",
    "english_title": "...",
    "subtitle": "..."
  },
  "style": {
    "aesthetic": "editorial, technical illustration",
    "color_palette": "..."
  },
  "layout": {
    "centerpiece": {
      "description": "中心视觉",
      "central_list": {
        "count": 13,
        "type": "numbered steps with pointer lines",
        "labels": ["01 ...", "02 ...", ...]
      }
    },
    "left_column": [
      {"module": "MODULE 1: ...", "count": 6, "items": [...]},
      {"module": "MODULE 2: ...", "count": 4, "items": [...]}
    ],
    "right_column": [
      {"module": "MODULE 3: ...", "items": [...]}
    ]
  }
}
```

---

### 模板 D：YouTube 缩略图

```json
{
  "type": "YouTube thumbnail",
  "character": {
    "description": "人物描述",
    "pose": "姿势 + 表情",
    "position": "right side, facing left"
  },
  "background": "背景场景",
  "typography_and_ui": {
    "main_title": {
      "text": "主标题",
      "position": "left, large bold font",
      "style": "黄色描边 + 黑色対折影"
    },
    "subtitle": {"text": "副标题", "position": "below main title"},
    "decorative_elements": ["箭头", "爆炸效果"],
    "corner_badges": [{"position": "top-right", "text": "NEW"}]
  },
  "style": "vivid colors, high contrast, YouTube clickbait aesthetic"
}
```

---

### 模板 D2：日式信息产品徽章集群（Japanese Info-Product Badge Cluster）

> 来源案例：No. 61「金色与黑色风格信息产品缩略图」/ No. 62「Neon AI 副业 YouTube 缩略图」
> 作者：ナーガ@X女帝
> 典型用途：AI 副业课程 / 知识付费 / 信息产品封面 / 日式高密度 CTA banner

**视觉签名**：深色背景 + 金黑主色 + 放射状光芒 + 9 个独立信息单元的徽章集群 + 红丝带打断

#### 核心模式

```json
{
  "type": "promotional banner / YouTube thumbnail",
  "style": "high contrast, flashy, professional, {argument name=\"theme color\" default=\"gold and black\"} palette, glowing light rays, sparkling particles",
  "subject": {
    "description": "{argument name=\"subject description\" default=\"confident young Asian man in a dark suit with arms crossed\"}",
    "pose": "looking upwards to the right",
    "props": "glowing open laptop in front of him"
  },
  "layout": {
    "background": "dark with radiant gold light bursts",
    "text_sections": {
      "top_left_badge": "{argument name=\"archive badge\" default=\"[保存版]\"}",
      "top_header": "{argument name=\"top text\" default=\"...\"}",
      "main_title": {
        "text": "{argument name=\"main title\" default=\"AI副業 完全攻略\"}",
        "style": "large, bold, 3D gold and white typography"
      },
      "subtitle_box": "{argument name=\"subtitle\" default=\"初心者でも月10万\"}",
      "top_right_badge": {
        "style": "gold laurel wreath",
        "text": "{argument name=\"year badge\" default=\"2026年版 最新版\"}"
      },
      "middle_right_tags": {
        "count": 3,
        "style": "stacked gold-bordered boxes",
        "labels": ["{argument name=\"tag 1\" default=\"最短で収益化\"}", "...", "..."]
      },
      "middle_right_ribbon": {
        "style": "red ribbon banner",
        "text": "{argument name=\"ribbon text\" default=\"手順を徹底解説\"}"
      },
      "bottom_left_tags": {
        "count": 6,
        "style": "2x3 grid of gold-bordered boxes",
        "labels": ["...", "...", "...", "...", "...", "..."]
      },
      "bottom_footer": "{argument name=\"footer\" default=\"迷わず稼げる！AI副業の教科書\"}",
      "bottom_right_badge": {
        "style": "gold laurel wreath",
        "text": "{argument name=\"template badge\" default=\"テンプレ付き\"}"
      }
    }
  }
}
```

#### 为什么这个模式有效（可复制原理）

1. **坐标系命名代替顺序描述**
   - 字段用 `top_left / top_header / main_title / middle_right / bottom_left / bottom_footer / bottom_right` 7 个明确坐标
   - 不写 "first element / second element"
   - 模型直接按坐标放元素，不会错位

2. **徽章集群 9 个独立单元**
   - 典型配置：`[保存版]` + `年份桂冠` + `3 个 tag` + `红丝带` + `6 格 tag 网格` + `底部 footer` + `模板桂冠` = 9 个
   - 每个单元有自己的 style 描述（粗体 3D / 金色边框 / 红丝带 / 桂冠）
   - **密度极高但不乱**，因为每个单元是独立视觉 "封装"

3. **Z 型阅读路径（视觉动线设计）**
   ```
   [保存版]————————————[2026年版 桂冠]
          ↓
     大标题（金白 3D）
          ↓                  ↓
     副标题黑框            堆叠 tag ×3
                              ↓
                          红丝带（打断）
          ↓
     6 格 tag 网格          [テンプレ桂冠]
          ↘            ↙
          底部大字 footer
   ```
   **眼睛走 Z 字**，不是随机扫视。这是日式信息设计的硬核功。

4. **红丝带的"同色系打断"**
   - 整图金+黑+白主色系
   - **唯一的红色**（中间右侧的丝带）= 强视觉锚点
   - 这是**广告学里的 color-pop 原则**：85% 画面统一，15% 破色
   - 如果全图都是红丝带或没有红，吸睛力立刻掉

5. **桂冠 + 3D 金字 + 放射光 = 权威感组合拳**
   - `gold laurel wreath` = 学术/颁奖/背书信号
   - `3D gold and white typography` = 奖杯质感
   - `radiant gold light bursts` = 神圣化光效
   - 三者叠加 → 信息产品的"权威性视觉承诺"

#### 变体空间

| 变量 | 可替换值 |
|------|---------|
| 主色系 | gold/black · neon cyan/magenta · red/white · blue/gold |
| 桂冠 | 金桂冠 · 银桂冠 · 星形奖章 · 勋章图案 |
| 丝带色 | red · blue · black · 渐变 |
| 主体 | Asian man · female influencer · 动漫角色 · 产品本身 |
| 语言 | 日文 · 中文 · 英文 · 韩文 |
| tag 数量 | 6 格 · 4 格 · 9 格 · 可变 |
| 拟物光效 | 放射光 · 爆炸线 · 星空粒子 · 霓虹发光 |

#### 反面清单

- ❌ 金黑 + 红丝带是**文化锚点**，随意换色系会丢失"日式信息产品"质感
- ❌ tag 数量过少（<3）→ 空荡
- ❌ tag 数量过多（>10）→ 拥挤，失去徽章感
- ❌ 主体人物动作太动感 → 与静态徽章集群冲突（主体要"稳"）
- ❌ 背景写成 "colorful" → 必须是暗底 + 放射光才能衬托金字

#### 参数化覆盖率建议

这个模板的原始版本（No. 61）**只参数化了 4 个字段**（theme color / subject / top_text / main_title / subtitle）。
真正可复用的版本应该**所有 label 全参数化**（见上面改进版）——否则换品类就要重写整块硬编码文本。

→ 详见 `parametric-template.md` 的「argument 覆盖率原则」。

---

### 模板 E：漫画多格分镜

```json
{
  "type": "4-panel manga page",
  "style": "black and white ink, screentone shading",
  "characters": {
    "protagonist": {"appearance": "...", "outfit": "..."},
    "antagonist": {"appearance": "..."}
  },
  "layout": {
    "structure": "2x2 grid with gutters",
    "panels": [
      {
        "position": "top-left",
        "scene": "内景/外景 + 时间",
        "subject": "人物动作",
        "details": "环境细节",
        "dialogue": "台词或旁白",
        "camera": "镜头角度"
      }
    ]
  },
  "global_elements": ["页码周围的分格線", "背景纹理"]
}
```

---

### 模板 F：2x2 网格广告

```json
{
  "type": "2x2 digital advertisement grid",
  "layout": {
    "structure": "4 个等分象限",
    "quadrants": [
      {
        "position": "左上",
        "theme": "旅游",
        "subject": "...",
        "elements": ["装饰元素1", "装饰元素2"],
        "text_labels": ["标题1", "标题2", "价格"],
        "icons": {"count": 3, "descriptions": [...]}
      }
    ]
  }
}
```

**关键技巧**：每个象限结构一致但内容不同——模型会理解为"同如样式但分类不同的广告位"。

---

## 实战写作流程

### 1. 先选模式再写字段

看着你要做的图像，先问自己：
- 有一个主视觉中心么？→ **中心星图**
- 是多区块从上到下的说明页么？→ **顺序串珠**
- 有视觉 + 文字需要一一对应么？→ **并行数组**
- 是应用/网页/直播 UI 截图么？→ **九宫格位置**
- 基于另一张图改么？→ **改造指令**

### 2. 从参考图反推字段

对着想模仿的 UI/海报截图：
1. 用截图标注每个区块
2. 按区块列 `sections` / `quadrants` / `panels`
3. 每个区块先设定 `position` 再写 content
4. 暂时不写 `style`，最后统一补上主风格

### 3. 颗粒度选择
- **粗**：只到 section 级，内容用自然语言 → 模型自由发挥
- **细**：到每个 button/input 级 → 模型严格执行
- UI mockup 偏细，信息图偏粗

### 4. 中文文字的写法
- 直接写完整内容（连标点符号一起）
- 数字写精确值（"55.6万本场点赞"而非"几万点赞"）
- 符号（¥、w、x、>）作为文字一部分写入
- 中英文混排直接写（"礼物展馆 0/24"）

---

## 陷阱清单

### ❌ 不要用 JSON 写单人物肖像
过度工程。单肖像用 `portrait.md` 的分层写法。

### ❌ 不要嵌套超过 3 层
模型混乱。对齐的做法：用多个平铺的 top-level section，不要嵌套太深。

### ❌ 不要字段名用中文
模型解析 `"标题": "..."` 不如 `"title": "..."` 稳。值可以中文，键用英文。

**但 layout 里的位置词除外**——实证中文位置词（右下角、左侧边栏）效果不差。

### ❌ 不要重复在多个字段里说同一件事
比如 `style` 写了"黑白漫画"，就不要再在 `panels[].details` 里重复说"黑白"。模型会困惑。

### ❌ 不要用 JSON 写剩下 40% 的怀旧且黑白水彩古风插画
纯风格性插画用 `cinematic-storyboard.md` 的短 prompt + 风格锪点写法。

### ✅ 不同元素用不同风格时，用 `style` 的对象写法
```json
"style": {
  "background": "杂质纸",
  "centerpiece": "3D 写实渲染",
  "labels": "平面 vector"
}
```
每个元素独立指定。参考案例：3D 石阶演化信息图。

---

## 原始数据来源

- `raw-data/awesome-gpt-image-2-zh.md`——126 个真实 prompt 案例
- `raw-data/all-json-prompts.json`——71 个解析后的 JSON prompt数据
- `raw-data/analysis-summary.json`——字段频率统计
- 源仓库：`git clone https://github.com/YouMind-OpenLab/awesome-gpt-image-2`（更新时 `git pull` 同步）

---

## 项目溯源 / 实战案例

### 案例 A：爱马仕包流程图（2026-04-22）

**原 prompt**：一件女装诞生的因果链（中英双语 + 10 模块 + 13 步骤中心列表）
**目标**：改成展示爱马仕 Birkin 制作流程，保持结构

**关键改动逻辑**：

| 原（服装） | 新（皮具） | 为什么不能机械替换 |
|---|---|---|
| Fiber → Yarn → Fabric | Hide → Tannage → Leather Type | 皮具原材料叙事层级完全不同，纤维/纱线不适用 |
| Patternmaking + Draping | Pattern + Hide Mapping（避开疤痕）| 皮革是不均匀材料，有特有的"避疤"工序，纸样剪裁没有 |
| Team Collaboration（8人分工）| The Artisan（单一工匠 + Compagnon du Devoir）| 爱马仕核心差异点——一人做完整只包，不是分工流水线 |
| Fitting + Revision | Edge Painting + Skiving | 皮具的"修正"在边缘处理，不是试穿调整 |
| Finished Front & Back | Blindstamp（工坊钢印 + 年份码）| 奢侈品真伪与传承的象征物 |

**踩过的坑**：
1. 第一版保留了 `{argument name="..." default="..."}` 占位符 → 模型直接把占位符文字渲染进图片
2. 第一版保留中英双语标题 → 模型把中文也画出来了（用户要求纯英文结果）
3. **修复**：删除所有 argument 占位符 + 删除中文副标题 → 纯英文 JSON

**学到的**：
- `{argument name="..." default="..."}` 是 prompt 模板语法，不是给 AI 看的。**给模型前必须替换为具体值**
- 中英双语在 Nano/GPT-Image-2 上会被忠实渲染——想要纯英文图必须删掉中文

### 案例 B：Sentinel 黑人超级英雄漫画页（2026-04-24）

**原 prompt**：Amazing Spider-Man 6 格漫画页
**目标**：改成写实画风 + 原创黑人超级英雄

**关键决策——不是简单染肤**：

用户说"黑人超级英雄"，第一反应是把 Peter Parker 肤色改成黑色。**这是错的**，因为：
- 蜘蛛侠的叙事内核是白人中产青少年视角（Uncle Ben 遗言 = 盎格鲁道德训诫）
- 黑人超级英雄的文化语境完全不同（家族 matriarch、社区教堂、systemic invisibility）
- 机械换肤 = 文化不真实

**沉淀出的黑人英雄叙事改写规则**：

| 原（Peter Parker） | 新（Sentinel，原创）| 文化依据 |
|---|---|---|
| New York | Harlem | 黑人文化历史中心 |
| World's Okayest Scientist | World's Okayest Engineer | 黑人 STEM 的代表性领域 |
| Uncle Ben | Grandmother in a church pew | Matriarch + Black Church 是黑人家庭结构核心 |
| "With great power comes great responsibility" | "We don't get to choose who we are. But we get to choose who we stand for." | 从权力-责任叙事 → 身份-归属叙事 |
| red & blue suit | matte navy + gold suit | 配色更接近 Black Panther / Luke Cage 质感 |
| full-face mask | half-face mask（只遮上半脸）| 避免"套装抹去种族"的问题 |

**style 改动**：
- 加 `art_style` 字段明确 `hyper-realistic, painterly digital rendering`
- 参考画师 **Alex Maleev**（Daredevil）、**Gabriele Dell'Otto**（Marvel 封面）
- 明确 `no cel-shading`——否则 AI 默认给美漫平涂
- 场景参考 **Barry Jenkins《Moonlight》** 的黑人肌肤在暖光下的摄影质感

**踩过的坑**：
- **没有**。这个 prompt 用户直接跑出了满意结果，后续还拿去做了 i2v

**学到的**：
- JSON 结构很适合分镜页改写——6 格结构一字不差保留，只换每格 `visual` 和 `text_content` 的文化内容
- 画风切换靠 `art_style` 字段独立指定，不要混在 `panels[].visual` 里稀释
- 原创角色比"染肤"更尊重文化——但必须保留原 prompt 的叙事节奏骨架

