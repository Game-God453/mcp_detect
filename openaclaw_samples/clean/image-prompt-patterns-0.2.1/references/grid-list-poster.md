# Grid-List Poster Patterns（大规模栅格列表海报）

> 用一张图展示几十到几百个具名实体的流派。年度榜单、工具大全、周期表、领域地图、YC 校友合集都属此类。

## 什么时候用

- **年度榜单**：XX 领域 100 强 / 50 强
- **工具大全**：100 AI 产品 / 30 designer tools
- **领域地图**：ML 算法 periodic table / UX pattern library
- **人物合集**：YC 某届校友墙 / 公司核心团队网格
- **产品/品牌目录**：球队全家福 / 字体样本册

## 视觉签名

- 规则栅格（N × M 或 N×N）
- 每格一个独立实体（logo / 头像 / icon + 名字）
- 左侧或顶部 sidebar 提供**分类轴**（让栅格变成隐式表格）
- 统一深色/浅色背景
- 每个 logo / 头像保留原 brand color（色彩碎片 = 栅格视觉节奏）
- 常见 footer slogan + 年份

## 核心结构字段

### 基础骨架

```json
{
  "type": "grid-list infographic poster",
  "layout": {
    "type": "grid poster",
    "grid": {
      "columns": "{argument name=\"columns\" default=10}",
      "rows": "{argument name=\"rows\" default=10}",
      "cell_count": 100,
      "numbering": "cells numbered 1 through N in small numerals at the top-left of each cell",
      "cell_style": "uniform cells with thin borders and centered logo + name"
    },
    "left_sidebar": {
      "count": "{argument name=\"category count\" default=10}",
      "position": "far left vertical column aligned to each row",
      "style": "small uppercase text with line icons",
      "labels": "{argument name=\"category labels\" default=[\"CAT 1\",\"CAT 2\",...]}"
    },
    "sections": [
      {
        "title": "{argument name=\"row1 title\" default=\"...\"}",
        "position": "row 1",
        "count": 10,
        "labels": "{argument name=\"row1 members\" default=[...]}"
      }
      // ... rows 2..N
    ]
  },
  "logo_treatment": "each entity shown with simplified recognizable mark in brand colors, centered in tile, scaled consistently",
  "title_block": {
    "headline": "{argument name=\"headline\" default=\"DOMAIN X IN YEAR Y\"}",
    "style": "very large bold uppercase"
  },
  "branding": {"footer": "..."},
  "rendering_notes": "symmetrical composition, infographic precision, no perspective distortion, sharp vector edges, polished social-media-shareable design"
}
```

### 五个必填字段（缺一破相）

1. **`grid.columns / rows / cell_count`** — 精确数量，告诉模型栅格规模
2. **`grid.numbering`** — 编号字段（静态图的"交互性入口"，社交分享的回帖种子）
3. **`left_sidebar.labels`** — 分类轴，把栅格变表格
4. **`sections[].labels`** — 每行/每格的具名成员
5. **`logo_treatment`** — 统一 logo 处理规则

## 五条可复制原理

### 原理 1：双轴语义（栅格 + sidebar）

纯栅格只有 100 个并列实体，读者视线没落点。**加左侧分类列后，栅格变成"隐式表格"**——读者扫一行就知道这行是什么。

比显式写 table 更适合 AI 图像模型：模型擅长 uniform grid，不擅长 dynamic table。用视觉对齐代替结构化 HTML。

### 原理 2：传播机制字段（numbering）

`numbering` 不是美观需求，是**让这张图能被分享时讨论**的机制。

> "#47 是 Graphcore，但为什么 #48 是 Cerebras？"

编号 = 给讨论打锚点。**写 prompt 时要主动加"传播机制字段"**，这是内容设计，不是视觉设计。

### 原理 3：Logo 三约束（simplified / recognizable / consistent）

```
simplified       → 模型画不好复杂 logo 细节
recognizable     → 但要有识别度
brand colors     → 保留识别度
scaled consistently → 防止大小不一
```

**四个约束同时满足的秘诀是 "above or beside its name" 这种弹性语句**——给模型选择权，避免某一刚性约束破坏其他约束。

### 原理 4：Shareable 作为 rendering meta 指令

`rendering_notes: "polished social-media-shareable design"` 一句话指挥了 5-6 个视觉决策：
- 对称（截屏不破）
- 高对比（feed 里抓眼球）
- 鲜明色彩（竞品缩略图中杀出）
- 清晰文字（移动端看得清）

**用"作品使命"代替"视觉清单"**，让模型自己展开技术决策。

### 原理 5：Category + Instance 的双层参数化

```json
"labels": "{argument name=\"row1 members\" default=[\"OpenAI\",\"Anthropic\",...]}"
```

**default 值可以是数组**——这是 GPT Image 2 的高级用法，但用来做大规模列表模板再合适不过。

优势：
- 一条 argument 管 10 个实体
- 换品类只改 10 个 argument（而不是 100 个字符串）
- default 本身就是一个完整可用的榜单（不替换也能出图）

## 变体空间

| 变量 | 可替换值 |
|------|---------|
| 栅格尺寸 | 10×10（100 个）· 7×7（49 个）· 8×5（40 个）· 6×6 周期表式 |
| 分类轴 | 垂直 sidebar · 顶部 header row · 栅格内色块分区 |
| 主题领域 | AI 公司 · 游戏 studio · 字体 · cocktail · 乐队 · Pokemon |
| 背景色调 | 深 navy · 纯黑 · 浅米色（paper look）· 白板白 |
| 实体呈现 | Logo · 头像 · Icon · 文字（纯排版）· 产品照 |
| 传播字段 | 编号 · 星级 · 百分比 · 首字母索引 |
| 分辨率 | 1:1（Instagram/LinkedIn）· 9:16（手机竖屏）· 16:9（电脑壁纸）|

## 反面清单

❌ 不写 `grid.cell_count` → 模型可能生成 8×8 或 12×12
✅ 同时写 columns / rows / cell_count，三重约束

❌ Label 全硬编码 → 换品类要改 100+ 字符串
✅ 用数组 default：`"labels": "{argument ... default=[...]}"`

❌ 不写 `logo_treatment` → 每个 logo 渲染方式不一致
✅ 统一 4 条约束：simplified + recognizable + brand colors + consistent scale

❌ 分类名和行成员**语义不对应**（如 Healthcare AI 行放 Duolingo）
✅ 每次替换 default 时**校验分类纯度**，避免脏数据腐烂模板

❌ 没考虑"看不懂怎么办"的 fallback
✅ 加 `unknown_logo_fallback: "use a clean abstract geometric mark in industry color"`

❌ 主标题塞太多子信息
✅ headline 只写一句（"AI COMPANIES IN 2026"），细节让 footer 说

## 参数化覆盖率建议

这个流派**天生适合 ⭐⭐⭐ 可复用模板**（80-95%）：

必抽：
- headline / year
- category count / labels（数组）
- 每 row 的 members（数组）
- grid 尺寸（columns/rows/cell_count）
- 主题色 / 背景色

可以不抽：
- logo_treatment（四约束是流派签名，改了就不像这类图）
- rendering_notes（polished/shareable 是流派标记）
- grid.numbering（编号是传播机制字段，不改）

一个标准 AI 公司榜单模板，改换成"100 家游戏公司"只需要改：
- headline（1 处）
- 10 个 category argument（10 处）
- 100 个 member name（但用数组 default 只需替换 10 个数组）

**总共 21 个替换点，换一个全新品类 → 符合"可复用模板"标准**。

## 来源案例

- **2026-04-24 Neal 投稿**：AI COMPANIES IN 2026 (10×10, navy, LinkedIn 风) —— 本流派首批沉淀案例
- 待补：周期表式（periodic table）变体、头像合集（team grid）变体、icon-only 极简变体

## 延伸：非栅格的大规模列表变体

栅格不是唯一选择。相关变体：
- **树状图**（treemap）：按面积比例展示，大类占更多 cell
- **Hex grid**（蜂窝网格）：更致密，有机感
- **Scatter plot**（散点图）：把分类映射到 2D 坐标，而非 row/column
- **Mindmap**（思维导图）：分类为中心辐射，非网格

这些不属于 grid-list poster，但是**同一个信息设计母题**（大规模列表可视化）的其他演化方向，另文沉淀。
