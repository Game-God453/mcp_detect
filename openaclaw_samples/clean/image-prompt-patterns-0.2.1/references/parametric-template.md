# Parametric Template Mechanism（`{argument}` 参数化）

> 这是**跨所有 prompt 流派**的通用机制，不属于任何单一模式。

## 为什么重要

实证数据（126 个 GPT Image 2 真实 prompt）显示：

- **71 个 JSON prompt**：几乎全部都用了 `{argument}`
- **55 个自然语言 prompt**：52 个用了 `{argument}`
- 总体使用率：**>95%**

参数化不是"高级技巧"，是**写可复用 prompt 的默认姿势**。

---

## 基本语法

```
{argument name="参数名" default="默认值"}
```

**三个组成部分**：
- `argument` - 关键字
- `name="..."` - 参数描述性名字（用英文最通用）
- `default="..."` - 没填时模型用的值

**工作机制**：
- 即使用户不修改，模型读到 default 值会正常生成
- 传参时替换 default 值即可
- 支持嵌套在字符串、JSON 值、数组项里

---

## 可以放在哪里

### 1. JSON 值字段里
```json
{
  "type": "portrait",
  "character": {
    "name": "{argument name=\"character name\" default=\"Elon Musk\"}",
    "outfit": "{argument name=\"outfit\" default=\"black t-shirt\"}"
  }
}
```

### 2. 自然语言 prompt 里
```
An anime-style illustration of a {argument name="action type" default="battle"}
between two fighters in a {argument name="setting" default="dojo"}.
```

### 3. 数组元素里
```json
"elements": [
  "{argument name=\"element 1\" default=\"floating lantern\"}",
  "{argument name=\"element 2\" default=\"cherry blossoms\"}"
]
```

### 4. 嵌套在更长的文本里（部分替换）
```json
"logo": "∞ {argument name=\"brand name\" default=\"Meta Quest 3\"}"
```
→ `∞` 固定，品牌名可变。

### 5. default 值为数组（高级用法）

不是所有 argument default 都必须是字符串。**数组 default 有特殊价值**：

```json
"labels": "{argument name=\"row1 members\" default=[\"OpenAI\",\"Anthropic\",\"Google DeepMind\",\"Microsoft\",\"Meta\",\"Amazon\",\"Apple\",\"NVIDIA\",\"xAI\",\"IBM\"]}"
```

**适用场景**：
- 大规模列表海报（模式 7 的 grid-list）
- UI mockup 的菜单项 labels 批量
- 多选项卡片的文本群

**优势**：
- 一条 argument 管 10+ 个同类实体，不用写 10 条
- 换品类时整个数组整体替换，动作简单
- default 数组本身即是一个完整可用的榜单（不填参也能直接出图）

**使用要点**：
- JSON 语法合法（数组是合法的 JSON 值）
- 模型会读到 default 里的所有元素，逐个渲染
- 数组长度应该 **匹配 `count`** 字段（如果同时有）——不匹配会导致模型失控

---

## 参数化的维度优先级（实证）

看 126 个案例，**最值得抽出的变量**按优先级：

### ⭐⭐⭐ 优先级最高（几乎必抽）
- **主体名字**：人物名 / 角色名 / 品牌名
- **主要文案**：标题 / 标语 / slogan
- **核心配色**：color theme / accent color

### ⭐⭐ 经常抽
- **场景 / 地点**：setting
- **动作 / 状态**：pose / action type
- **产品名 / 型号**：product name
- **数字 / 价格**：price / metrics

### ⭐ 偶尔抽
- **风格 / 艺术媒介**：art style
- **背景 / 色调**：background
- **天气 / 时间**：weather / time of day

### 不要抽
- **结构骨架**（"2x2 grid" 这种）
- **布局方式**（九宫格位置字段）
- **经过测试的灵感组合**（一改就崩）
- **中文文字的固定句式**

---

## 三种设计决策

### 决策 1：一个还是多个 `{argument}`

- **模板化意图强**（同一张图批量换 50 个 variant）→ 抽 5-8 个
- **只想换 1-2 个关键变量**（改个人名）→ 只抽 1-2 个
- **一次性作品**（不会复用）→ 可以完全不抽

### 决策 2：default 值写得多具体

- **越具体越好**：`"character name"` 不如 `"Elon Musk"`
- default 就是**模型的兜底**，模糊 default = 模糊结果
- 好 default 本身就可以直接出图

### 决策 3：参数名用哪种语言

- **参数名用英文**：`character name` / `brand logo`
- **default 值跟随内容语言**：如果是中文海报，default 用中文
- 混用不报错，但英文参数名最通用

---

## 组合技：嵌套参数

```json
{
  "character": {
    "description": "a young {argument name=\"gender\" default=\"female\"} {argument name=\"profession\" default=\"warrior\"} with {argument name=\"hair color\" default=\"red\"} hair"
  }
}
```

一条字符串里嵌 3 个参数。**语法完全兼容**，模型会并行替换。

---

## 实战模式库

### 模式 1：品牌参数化模板
```json
{
  "header": {
    "brand_name": "{argument name=\"brand name\" default=\"YourBrand\"}",
    "tagline": "{argument name=\"brand tagline\" default=\"Innovation Simplified\"}"
  },
  "hero_image": "{argument name=\"hero visual\" default=\"3D rendered product\"}",
  "cta_text": "{argument name=\"cta\" default=\"Learn More →\"}"
}
```
→ 可批量生成多品牌 landing page mockup。

### 模式 2：角色参数化模板
```json
{
  "character": {
    "name": "{argument name=\"character name\" default=\"Alex\"}",
    "appearance": "{argument name=\"appearance\" default=\"young, athletic\"}",
    "outfit": "{argument name=\"outfit\" default=\"cyberpunk streetwear\"}",
    "pose": "{argument name=\"pose\" default=\"confident standing\"}"
  }
}
```
→ 同一构图换角色。

### 模式 3：季节/主题参数化模板
```json
{
  "theme": "{argument name=\"season\" default=\"autumn\"}",
  "color_palette": "{argument name=\"palette\" default=\"warm oranges and browns\"}",
  "background_elements": "{argument name=\"seasonal elements\" default=\"falling leaves, pumpkins\"}"
}
```
→ 同模板出春夏秋冬四版。

---

## 工程化建议

### 变模板的 5 步检查清单

1. **先写死**：先写完整 prompt，确认出图效果
2. **找变量**：回头扫一遍，标出所有"下次可能改的值"
3. **抽出参数**：把变量替换成 `{argument name="..." default="<原值>"}`
4. **再测一次**：传 default，应该和步骤 1 的效果一致
5. **试改一个参数**：换个 value，确认改对了地方

### Default 值的"可上场"原则

default 应该就是一个**完整可用的值**。测试方法：
- 不填任何参数，直接跑 prompt
- 如果出的图能直接用 → default 合格
- 如果出的图奇怪 → default 太抽象，需要重写

### 配合 GitHub Copilot / Cursor 做模板管理

把 `{argument}` prompt 存成 `.json` 文件：
```
prompts/
├── landing-page.json
├── avatar-3x3-grid.json
├── product-explosion.json
└── youtube-thumbnail.json
```
每个文件 = 一个可复用模板。传参只需改 default 值。

---

## 和其他流派的配合

| 流派 | 参数化使用场景 |
|------|--------------|
| **写实摄影（A）** | 抽出 subject name / location / time of day |
| **风格化分镜（B）** | 抽出 character / scene / mood，风格锚点保持不变 |
| **结构化 JSON（C）** | 绝大多数 value 字段都能抽 |
| **文化融合（D）** | 抽出主题，锚点保留（如"桃太郎" → {theme}）|
| **场景叙事（E）** | 抽出多主体的关键属性（配色、pose、台词）|

---

## 记忆口诀

> **结构不变，细节可变。**
>
> 抽变量前先问：这个值变了，图还成立吗？

- 变了还成立 → 抽
- 变了就崩 → 别碰

---

## argument 覆盖率原则（Parametric Coverage）

> 来源：No. 61 日式信息产品徽章集群案例的反案教材

很多在外流传的「GPT Image 2 模板」看似很完整，但值值**只参数化了 3-5 个字段**（通常是 theme color / subject / title / subtitle），
其他徽章文字、tag label、footer、ribbon 全部**硬编码**。

这意味着：
- **换一个品类就要手改 N 处**，失去了模板价值
- **模型出图每次都带原始品类的 meta 语义污染**（例如值值硬编码了「AI 副业」级联想）

### 判断覆盖率的 3 个等级

| 等级 | 覆盖率 | 判断标准 | 用途 |
|------|-------|---------|------|
| ⭐ **一次性** | 10-30% | 只抽了主体/标题 | 自己用一次，结就结 |
| ⭐⭐ **交际级** | 40-60% | 抽了主要文本、主体、色系 | 帮同事跳调 2-3 个版本 |
| ⭐⭐⭐ **可复用模板** | 80-95% | 所有 label / tag / footer / ribbon 都抽 | 产品化、批量生成 50+ 变体 |

### 实战法则

1. **写模板前先问：「未来哪些字会改？」**
   - 所有会改的 → 必须参数化
   - “徽章集群风格」这种统一特征 → 不抽，写死

2. **随手过一遍迫注试字**——“如果换个课程类型，这个词会改吗？”
   - 会：抽为 argument
   - 不会：留着

3. **宁愉多抽不欠抽**：一个多余的 argument 最多增加一行代码，一个必要的缺失要重写模板

4. **检查清单（放徽章模板前）**：
   - [ ] 所有徽章文字全参数化？（top_left_badge / top_right_badge / bottom_right_badge）
   - [ ] 所有 tag label 全参数化？（每个格子的文字都有 argument）
   - [ ] 标题 + 副标题 + footer + ribbon text 全参数化？
   - [ ] 主色系 + 主体描述 + 主体 pose 全参数化？

全勾选 → 真的可复用模板。缺任何一项 → 是个「为了 ×× 主题写的定制版」，不是模板。

---

## 地理分层字段（Geographic Region Splitting）

> 来源：2026-04-25 旅行海报三版对照案例

### 陷阱

做地图 / 领土 / 分区类 prompt 时，把所有城市/区域放在一个平铺数组里：

```json
"cities": ["BAY OF ISLANDS","AUCKLAND","ROTORUA","TAUPO","NAPIER","WELLINGTON","NELSON","CHRISTCHURCH","QUEENSTOWN","DUNEDIN"]
```

**问题**：模型不知道这些城市哪些在北岛、哪些在南岛。生成时**点可能跨区乱飞**——Queenstown 跑到北岛去了，Auckland 落海里了。

### 修法

按地理子区域拆字段：

```json
"map_details": {
  "north_island": {"count": 6, "labels": ["BAY OF ISLANDS","AUCKLAND","ROTORUA","TAUPO","NAPIER","WELLINGTON"]},
  "south_island": {"count": 4, "labels": ["NELSON","CHRISTCHURCH","QUEENSTOWN","DUNEDIN"]}
}
```

**原理**：字段名本身是空间锚点。`north_island` / `south_island` 告诉模型"这些要放在这个区域"。

### 适用场景

| 主题 | 分区示例 |
|------|---------|
| 新西兰 | north_island / south_island |
| 日本 | hokkaido / honshu / shikoku / kyushu |
| 英国 | england / scotland / wales / northern_ireland |
| 美国 | west_coast / midwest / east_coast / south |
| 中国 | 华北 / 华东 / 华南 / 华中 / 西北 / 西南 / 东北 |
| 埃及 | nile_delta / western_desert / upper_egypt / red_sea_sinai |

**可复用模板版**：

```json
"geographic_regions": "{argument name=\"regions\" default=[{\"name\":\"region 1\",\"cities\":[\"A\",\"B\"]},{\"name\":\"region 2\",\"cities\":[\"C\",\"D\"]}]}"
```

数组 default 直接定义整个分区结构，换国家只改一个 argument。

---

## 主题耦合反模式（Theme Coupling Anti-Pattern）

> 来源：2026-04-24 Neal 投稿的 COSMIC GRAVITY Design System board 案例

### 陷阱

labels / sections / value 字段里夹带**主题特定命名**，但没参数化。

**反例**：
```json
"UI ELEMENTS": ["EXPLORE button", "BLACK HOLE pill button", "JUPITER pill button"]
```

第一个 "EXPLORE button" 是通用组件（按钮），后两个 "BLACK HOLE" / "JUPITER" **把深空主题耦合到结构里**。换主题做"深海探索 dashboard"时：

- 如果你 argument 只覆盖了 theme name → 模板告诉模型是"深海主题"，但 labels 里仍然指名要 "BLACK HOLE" 按钮 → 模型冲突，乱生成
- 要修要改这两个 label，每次换主题都人工介入

**判断规则**：

写完 prompt 后扫一遍所有 labels / names / values，问：
- "这个名字**换主题就要改**吗？"
  - 要改 → 必须 argument 化
  - 不用改 → 保留

### 典型的"该 argument 但常被遗漏"位置

| 字段 | 反例 | 修正 |
|------|-----|------|
| 按钮文案 | `"EXPLORE button"` | `"{argument name=\"cta button\" default=\"EXPLORE button\"}"` |
| 主题实体名 | `"JUPITER pill button"` | `"{argument name=\"theme pill 1\" default=\"JUPITER pill button\"}"` |
| 视觉示例标签 | `"BLACK HOLE"` | `"{argument name=\"visual 1\" default=\"BLACK HOLE\"}"` |
| 数组里的实体 | `"planets": [{...Jupiter...}]` | `"theme_objects": "{argument ... default=[{...}]}"` |

### 修法

**两种改造**：

**改造 A：逐个参数化**（小范围主题耦合）
每个主题耦合字段抽成独立 argument。适合主题相关字段少于 5 个的场景。

**改造 B：整组参数化为数组**（大范围主题耦合）
把整个 sections 或 visuals 组抽成一个大 argument（用数组 default）。适合主题和结构深度耦合的场景。

参考 `parametric-template.md` 的"数组 default"用法（技巧 5）。

---

## 最后一条警告

不是所有案例都该追求 ⭐⭐⭐ 级覆盖率。

- 图越简单 → 覆盖率低就够
- 图越密集（像日式徽章集群）→ 越需要高覆盖率，否则模板名不副实
- 判断准则：“换个品类，改动量是不是 <10% 字段”
  - 是 → 模板合格
  - 不是 → 现在还不是模板
