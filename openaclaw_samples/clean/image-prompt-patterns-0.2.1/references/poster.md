# Poster & Illustration Patterns

## 什么时候用

- 城市宣传海报 / 电影海报 / 复古旅游海报
- 信息图 / 科学百科海报 / 烹饪流程图
- 创意广告海报 / 产品 Ad 重设计
- 夸张透视字体 / 极简留白构图

## 六大风格速查

### A. 城市宣传海报（City Promo Poster）
**关键词组合**：
```
2026 spring [CITY] city promo poster, illustrated cityscape with
iconic landmarks arranged in layered depth, warm [SEASON] color palette,
bold hand-drawn typography header, travel poster aesthetic,
inspired by vintage railway travel posters 1950s
```
**构图要诀**：
- 标志性建筑垂直堆叠 / 近远景分层
- 大标题字在顶部，副标在底部
- 主色调限定 3-4 色，有明确季节感

### B. 复古旅游海报（Vintage Travel Poster）
```
Vintage Amalfi coast travel poster 1960s aesthetic,
flat illustrated style with limited color palette,
sun-washed terracotta and cerulean blue,
stylized silhouettes of figures, distressed texture overlay,
serif retro typography, italian modernism influence
```
**构图要诀**：平涂色块 + 几何简化 + 复古字体

### C. 中式美学海报（Chinese Aesthetic）
```
Chinese minimalist S-shaped composition poster,
traditional ink wash painting with modern graphic elements,
negative space emphasized, calligraphy integrated into layout,
[THEME] subject with symbolic iconography,
muted earth tones with single red accent seal stamp
```
**子流派**：
- **水墨山水**：`new Chinese ink landscape`
- **剪纸**：`paper-cut silhouette style`
- **工笔**：`detailed traditional gongbi painting`
- **墨水曲线**：`ink-curve brushstroke composition`

### D. 科学百科 / 信息图（Science Encyclopedia）
```
vertical science encyclopedia poster, [SUBJECT] anatomical breakdown,
cross-section diagram with labels and arrows,
vintage scientific illustration aesthetic,
hand-drawn botanical/zoological plate style,
beige aged paper background, sepia and burgundy ink tones,
detailed latin nomenclature text
```
**经典案例**：
- 龙鱼解剖图（barreleye fish anatomy）
- 反向传播神经网络图（backpropagation diagram）
- 汉服分解信息图（hanfu breakdown）
- 辣椒猪肉烹饪流程图（chili pork cooking flowchart）

### E. 电影海报（Movie Poster）
```
fictional [GENRE] movie poster for "[TITLE]",
dramatic [MAIN SUBJECT] in foreground,
[SUPPORTING ELEMENTS] arranged in background,
[TAGLINE] prominent typography,
cast credits block at bottom, release date "[DATE]",
[STUDIO LOGOS] at base,
moody cinematic color grading [PALETTE]
```
**子流派**：
- **暗黑史诗**：`dark epic concept poster, silhouette against fire/sky`
- **科幻**：`science fiction movie poster, neon cyan accent`
- **黑帮**：`crime thriller poster, high contrast noir lighting`
- **动画**：`fictional anime movie poster, [STUDIO] aesthetic`

### F. 广告海报（Product Ad）
```
refreshing summer [PRODUCT] advertisement poster,
dynamic splash composition with product center-stage,
bold Japanese supermarket flyer style,
oversized price typography with yen/dollar symbols,
vibrant saturated colors, photography + graphic hybrid,
playful hand-drawn accents around product
```

### G. 3D Diorama Travel Infographic（浮雕地图旅行海报）

> 来源：2026-04-25 Neal 投的 Switzerland / New Zealand / Egypt 三版对照
> 特征：3D 浮雕地图为主体 + 周边 travel ephemera（行李箱/邮票/宝石/Polaroid/国旗）环绕 + 右侧景点列表 + 地图上具名 landmark + 动态元素

**与 A/B（城市宣传海报 / 复古旅游海报）的区别**：
- A/B 是**平面插画**风格
- G 是 **3D 立体 diorama + collage 拼贴**，地图有浮雕厚度，周围配件有真实投影

#### 完整 JSON 模板（融合三版优点）

```json
{
  "type": "travel poster infographic",
  "theme": "vintage-inspired premium travel guide map",
  "subject": {
    "country": "{argument name=\"destination country\" default=\"Egypt\"}",
    "map_style": "3D illustrated topographic map shaped like the country, viewed slightly tilted from above, on a clean warm-neutral background",
    "terrain": "{argument name=\"terrain description\" default=\"golden desert relief, deep blue Nile cutting vertically, green fertile valley hugging both banks, Red Sea mountains in the east, Mediterranean coast in the north\"}",
    "route": "soft white trails connecting major destinations with circular city markers"
  },
  "layout": {
    "format": "square poster",
    "centerpiece": "large sculpted 3D relief map with miniature landmarks rising from the terrain, labeled city markers, warm diorama lighting with long soft shadows"
  },
  "text": {
    "headline": "{argument name=\"headline text\" default=\"EGYPT\"}",
    "subheadline": "{argument name=\"subheadline text\" default=\"TRAVEL GUIDE\"}",
    "intro": "{argument name=\"intro text\" default=\"From ancient pyramids and timeless temples along the Nile to vibrant coral reefs and desert oases.\"}",
    "stamp_text": "{argument name=\"stamp text\" default=\"TRAVEL TO EGYPT\"}"
  },
  "map_details": {
    "geographic_regions": "{argument name=\"regions\" default=[{\"name\":\"Nile Delta & North\",\"cities\":[\"ALEXANDRIA\",\"CAIRO\",\"GIZA\"]},{\"name\":\"Western Desert\",\"cities\":[\"SIWA OASIS\"]},{\"name\":\"Upper Egypt\",\"cities\":[\"LUXOR\",\"ASWAN\",\"ABU SIMBEL\"]},{\"name\":\"Red Sea & Sinai\",\"cities\":[\"HURGHADA\",\"SHARM EL-SHEIKH\",\"DAHAB\"]}]}",
    "mini_landmarks": "{argument name=\"landmarks\" default=[\"three Great Pyramids of Giza with the Sphinx at their base near GIZA\",\"Karnak-style temple colonnade near LUXOR\",\"four colossal rock-carved seated statues near ABU SIMBEL\",\"Pharos-style lighthouse near ALEXANDRIA\",\"palm oasis pool near SIWA OASIS\",\"obelisk rising from rock quarry near ASWAN\",\"coral reef fish and snorkel mask near SHARM EL-SHEIKH\"]}",
    "dynamic_elements": "{argument name=\"dynamic\" default=[\"small white Nile cruise ship slowly moving north along the Nile\",\"camel caravan of 3 silhouettes moving across the Great Sand Sea\",\"tiny dhow fishing boat drifting off the Red Sea coast\"]}",
    "flag": {
      "count": 1,
      "description": "{argument name=\"flag description\" default=\"Egyptian national flag on a brass pole in the upper right corner\"}"
    }
  },
  "travel_props": "{argument name=\"ephemera\" default=[\"vintage tan leather suitcase with travel stickers and a country-flag badge in the upper left\",\"antique brass compass rose with weathered patina on the left\",\"sun-faded postage stamp upper right reading TRAVEL TO EGYPT with pyramid art\",\"tilted polaroid photo in the lower left with caption 'Pyramids at Dawn'\",\"4 faceted scarab-shaped gemstone charms total with 2 lapis-lazuli blue and 2 carnelian red\",\"papyrus scroll partially unrolled in the bottom right with hieroglyph-like markings\"]}",
  "destination_highlights": "{argument name=\"highlights\" default={\"CAIRO\":[\"Egyptian Museum\",\"Khan el-Khalili Bazaar\",\"Citadel of Salah al-Din\"],\"GIZA\":[\"Great Pyramid of Khufu\",\"Sphinx\",\"Solar Boat Museum\"],\"LUXOR\":[\"Karnak Temple\",\"Valley of the Kings\",\"Luxor Temple\"]}}",
  "style": {
    "color_palette": "{argument name=\"palette\" default=\"warm desert sand, terracotta, deep Nile blue, fertile-valley green, gold accents\"}",
    "lighting": "soft golden-hour studio lighting with realistic long shadows from miniature landmarks, diorama depth cues",
    "typography": "bold condensed sans-serif headline, clean editorial body",
    "render_quality": "high-detail polished commercial poster, hybrid of infographic design and realistic miniature diorama, premium tourism campaign aesthetic"
  }
}
```

#### 6 条可复制原理

1. **3D 浮雕而非平面插画**：`terrain` 字段强调 "raised relief / sculpted / diorama"，给地图厚度感
2. **地理分层字段 `geographic_regions`**：按子区域拆城市，模型摆点不会跨区（北岛城市不飞到南岛去）
3. **`mini_landmarks` 具名到点**：格式 `"{视觉描述} near {城市}"`——视觉+锚点+关系三合一
4. **`dynamic_elements` 独立字段**：船/火车/骆驼这种运动元素单独拆出，避免被静态元素挤掉
5. **Ephemera 堆叠密度**：travel_props 数组含 6-7 件手账式配件，每件写 **数量 + 颜色分布 + 位置 + 纹理**
6. **双层信息设计**：地图上点 + 右侧列表详情（destination_highlights 对象映射城市→景点数组）

#### 本土化变量（换国家时要同步改的清单）

| 维度 | Switzerland | New Zealand | Egypt |
|------|------------|-------------|-------|
| 地形 | 雪山+湖泊+铁路 | 两岛+峡湾+绿岭 | 沙漠+尼罗河+红海 |
| 地理分区 | 无（整张地图）| 2（北岛/南岛）| 4（Delta/Western/Upper/Red Sea）|
| 动态元素 | 2 列红火车 | 小红车 | Nile 游轮 + 骆驼 + Dhow |
| Ephemera 颜色 | 银+红心 | 绿+蓝宝石 | Lapis+Carnelian scarab |
| 特色配件 | — | — | Papyrus scroll |
| 国旗 | Swiss cross | NZ blue ensign | Red-white-black with eagle |
| Color palette | 阿尔卑斯绿+蓝湖+白雪 | 绿岭+板岩灰+蓝海 | 沙金+尼罗蓝+绿谷+金色 |

**心法**：换国家时**不只是换地名**——terrain / dynamic / ephemera 颜色 / 特色配件 / palette 都要本土化，否则 AI 会给你一张"瑞士皮肤的埃及"。

#### Argument 覆盖率

本模板 ⭐⭐⭐ **可复用模板级（~85%）**：
- `destination country` / `headline` / `subheadline` / `intro` / `stamp_text`
- `terrain description` / `regions` / `landmarks` / `dynamic` / `flag description`
- `ephemera` / `highlights` / `palette`

换国家只改 13 个 argument（其中 7 个是数组）= 真正可复用。

#### 反面清单

❌ 只 argument 化国家名，地形描述还是原国家 → AI 给"瑞士皮肤的埃及"
✅ terrain / palette / dynamic 全本土化

❌ 不拆 geographic_regions → 城市点乱飞
✅ 3-5 个地理分区，每区 1-4 个城市

❌ mini_landmarks 泛化 → 给你一堆"generic churches"
✅ 具名到地标 + 锚定到城市 + 加视觉关系

❌ 把动态元素混在 mini_landmarks 里 → 运动感丢失
✅ 独立 `dynamic_elements` 字段

❌ ephemera 只有 3-4 件 → 画面空
✅ 6-8 件堆叠，有颜色/数量分布

---

## 信息密度层级

### 极简（Ultra-Minimal）
- 1-2 主要视觉元素
- 大量留白
- 仅一行主文案
- 关键词：`negative space emphasized, single focal point`

### 平衡（Balanced Editorial）
- 3-5 视觉层
- 图文各占 50%
- 关键词：`editorial magazine layout, harmonious hierarchy`

### 极度密集（Ultra-Dense Information）
- 10+ 视觉元素
- 图文比 1:2，文本占主导
- 关键词：`ultra-dense information design, encyclopedic layout,
         overwhelming amount of labels and diagrams`
- 典型：老式科学图鉴、地铁路线图、游戏 UI

---

## 字体描述词汇

### 手写感
- `bold hand-drawn typography`
- `brushstroke calligraphy header`
- `handwritten sharpie marker`
- `chalkboard style lettering`

### 复古感
- `retro serif typography 1960s`
- `art deco geometric font`
- `Japanese showa-era typography`
- `Chinese calligraphy brush stroke`

### 现代感
- `ultra-bold sans-serif, Helvetica-influenced`
- `variable width display type`
- `grotesque neo-modern typography`

### 极限透视
- `extreme perspective typography, forced foreshortening,
  letters emerging from vanishing point, architectural type`
- 效果：字体像建筑一样从地平线冲向观众

---

## 色彩方案词汇

### 中式色调
- `muted earth tones with single red accent`
- `traditional Chinese five-element palette`
- `ink black with gold leaf highlights`

### 日式色调
- `Japanese showa warm palette, sepia and cream`
- `Ukiyo-e woodblock color palette, indigo and vermillion`

### 电影感
- `teal and orange cinematic grading`
- `high-contrast film noir black and white`
- `bleach bypass desaturated cool`

### 复古印刷
- `Risograph print limited palette, pink and blue`
- `offset print with CMYK misregistration`
- `screen print halftone texture`

---

## 完整案例模板

### 城市春季海报
```
[CITY] spring 2026 city promo poster,
illustrated cityscape composition with [LANDMARK1],
[LANDMARK2], and [LANDMARK3] arranged in layered depth,
foreground featuring [SEASONAL ELEMENT like cherry blossoms/daffodils],
people in [ACTIVITY] scattered throughout,
warm spring color palette of [COLOR1], [COLOR2], [COLOR3],
bold hand-drawn typography header "[CITY NAME] SPRING 2026",
subtitle in smaller brush font, date range at bottom,
travel poster aesthetic inspired by 1960s Japan National Railways posters,
flat illustration with subtle texture overlay, vertical A1 format
```

### 信息图海报
```
vertical scientific encyclopedia poster about [SUBJECT],
cross-section diagram showing internal structure with callout labels,
surrounding detailed illustrations of [SUBTOPIC1], [SUBTOPIC2],
[SUBTOPIC3] in panel layout,
vintage botanical plate aesthetic 1890s-1920s,
aged ivory paper background with subtle foxing,
sepia brown and burgundy red ink illustration,
hand-lettered latin nomenclature and measurement scales,
ornate serif title header, dense information design
```

---

## 反面清单

❌ "poster design" → 没有风格方向
✅ 具体指定：`vintage travel poster 1960s` / `minimalist S-shaped Chinese`

❌ "nice colors" → 模型乱给
✅ 具体命名：`muted earth tones with single red accent` / `teal and orange`

❌ 只说构图，不说层次
✅ 明确写 `foreground / middleground / background` 各有什么

❌ "with text" → 文字会乱码
✅ 写具体文字内容 + 字体风格：`headline "SPRING 2026" in bold hand-drawn serif`
