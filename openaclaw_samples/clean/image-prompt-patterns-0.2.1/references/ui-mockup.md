# UI & Social Media Mockup Patterns

## 什么时候用

- 伪造社交媒体截图（推特/抖音/微博）用于传播或艺术
- 设计 UI 系统 / Design System 展示
- 制作 iPhone Keynote 风手机截图
- 历史人物/虚构角色现代化设计（如"乾隆的推特")
- 游戏 UI 状态屏 / 氪金抽卡界面

## 四大类型

### A. 社交媒体伪截图（Pseudo-Screenshot）

最热门的亚类是**"历史人物/虚构角色的现代社媒页"**。

**关键词组合**：
```
realistic [PLATFORM] screenshot mockup,
[HISTORICAL FIGURE]'s [PLATFORM] profile page,
profile avatar showing [OIL PAINTING/CLASSIC PORTRAIT of figure],
username "@[romanized_name]", verified blue checkmark,
bio paragraph written in period-appropriate tone,
recent posts visible showing [FIGURE]'s historical concerns
translated to modern internet speak,
accurate platform UI details:
- [PLATFORM] logo and header navigation
- realistic timestamps, like/retweet counts
- proper font rendering
- authentic color scheme
9:16 mobile screenshot aspect ratio,
slight compression artifacts for authenticity
```

**高互动案例**：
- 慈禧太后的 X 主页（西洋势力/后宫 drama）
- 李成桂的 X 页（建国期焦虑）
- 马斯克抖音直播截图
- 刘亦菲抖音直播
- 特朗普 x 金正恩 直播 PK
- 山姆奥特曼棒球比赛直播

### B. 平台 UI 精确还原

**抖音/TikTok 直播间**：
```
realistic Douyin (抖音) livestream screenshot,
9:16 vertical mobile screen, portrait orientation,
[STREAMER] visible in center frame doing [ACTIVITY],
floating heart animations, gift popups with [GIFT NAME],
live indicator "LIVE" badge top-left with red dot,
viewer count "[N]万人观看" top-right,
chat messages scrolling right side in small text,
bottom bar with comment input, red heart button,
"加购物车" yellow shopping cart button on right side,
authentic Chinese TikTok UI color scheme
```

**Twitter/X 手机版**：
```
iOS X/Twitter app screenshot, mobile vertical,
home timeline or profile view,
[TWEET CONTENT] as main post,
authentic iOS system bar (time, battery, signal),
X app dark mode or light mode (specify),
follow button, profile header banner,
realistic like/retweet/reply counts,
subtle screen glare, slight keystone for handheld feel
```

**Instagram Post**：
```
Instagram post screenshot mockup,
[IMAGE CONTENT] as main photo,
username "@[handle]" with circular avatar,
location tag, posting time "X hours ago",
like count, caption with emojis and hashtags,
first few comments visible,
authentic Instagram 2026 UI layout
```

**YouTube 直播 UI**（meme / 拼场面 / 让不可能同框的人同框）：

```json
{
  "type": "YouTube livestream UI",
  "top_nav": {
    "logo": "YouTube Premium",
    "search": "{argument name=\"search query\" default=\"主播名\"}",
    "icons": 3
  },
  "player": {
    "subjects": [
      "{argument name=\"guest\" default=\"female celebrity\"} in {argument name=\"guest outfit\" default=\"white cardigan\"}",
      "{argument name=\"host\" default=\"bearded man in beige jacket laughing\"}"
    ],
    "bg": "{argument name=\"background\" default=\"couch, 2 silver play buttons on wall, custom logo\"}",
    "overlays": {
      "chat": {"pos": "left", "count": 15, "desc": "colored usernames, white text"},
      "goal": {"pos": "top right", "text": "{argument name=\"goal text\" default=\"TONIGHT'S GOAL: 0 to 25\"}"},
      "banner": {"pos": "bottom center", "text": "{argument name=\"streamer handle\" default=\"@STREAMER\"}"}
    },
    "controls": {"count": 10}
  },
  "details": {
    "title": "{argument name=\"video title\" default=\"FULL STREAM | GUEST ✕ HOST\"}",
    "channel": "{argument name=\"channel name\" default=\"Host Channel Name\"}",
    "buttons": 5
  }
}
```

**关键元素（YouTube 直播独有）**：
- 红色 LIVE 小圆点 + 观众数（如 `1.2M watching`）
- 左侧聊天条（比 Twitch 更稀疏，有颜色签名级别）
- super chat 折叠卡（带用户 + 颜色 + 金额）
- 右上角分享/通知按钮、扩展屏幕按钮
- 下方控件条：暂停、音量、CC、设置、全屏（`controls.count: 10`）
- 视频下方：标题 + 频道名 + 订阅/like/share/download/save 按钮（`buttons: 5`）

**meme 属性触发（如何让它看起来像 meme 而不是官方）**：
- 自制感的 goal 框（“TONIGHT'S GOAL: 0 to 25”——官方直播不会这么沙雕）
- 精神分裂的主播品牌（个人 logo 带动物/像素/恢复感字体）
- 嵌套标题空气感：“FULL STREAM | 演员名 × 主播名”（或混入非英文字符集增加真实感）
- 忧鬱的背景（沙发 + 2 个银色 Play 奖杯 + 奇怪的附加 logo）

**版权红线：模板可存，生成时拿 default 换掉**
- 不要 default 填真实名人名字（生成时测试换占位词）
- 虽然 GPT Image 2 有时会生成“像 XX 但不是 XX”的脸，商业使用时仍然需要自查
- 混入名人名字是 meme 网给人的结构一部分，但商用需换掉

### C. Design System / UI 套件

**玻璃拟态 UI**（Glassmorphism）：
```
modern glass UI design system showcase,
multiple interface components arranged on single canvas:
navigation bar, button variants (primary/secondary/ghost),
input fields, card components, modal dialogs,
all with frosted glass effect: semi-transparent background,
subtle backdrop blur, soft drop shadows,
gradient backgrounds visible behind glass,
rounded corners 16px-24px, consistent padding,
typography hierarchy shown,
dark mode variant alongside light mode,
minimal labels describing each component
```

**赛博朋克霓虹 UI**：
```
cyberpunk neon UI design system,
dark navy/black background with electric magenta/cyan accents,
glowing neon edges on all components,
pixel-perfect terminal-style typography,
glitch effects on transitions (stylized),
futuristic iconography with wire-frame aesthetics,
grid of: buttons, dropdowns, progress bars,
notification cards, modal dialogs,
consistent 4px glow blur on active states
```
**主题化 Design System Board（JSON 结构化，进阶）**

完整 JSON 模板，来自 2026-04-24 案例「COSMIC GRAVITY 深空探索仪表板」。
这类 board 是 Dribbble / Behance 作品集格式——单张静态图铺满调色板 / 组件库 / 卡片 / 数据可视化 / 视觉示例，整体氛围强调"概念+奢华科技"。

```json
{
  "type": "futuristic glassmorphism UI design system board",
  "theme": "{argument name=\"theme name\" default=\"deep-space planetary exploration dashboard\"}",
  "style": {
    "background": "near-black matte canvas with subtle starfield haze",
    "lighting": "soft shadows, faint bloom, warm amber highlights, cool blue-violet accents, translucent glass panels",
    "material": "frosted glass, glossy dark surfaces, thin luminous strokes, soft refractions",
    "mood": "luxury sci-fi, minimal, cinematic, highly polished"
  },
  "layout": {
    "format": "single wide presentation board",
    "sections": [
      {"title": "BRANDING", "position": "left column", "count": 5, "labels": ["header branding block", "color palette swatches", "gradient bar", "typography specimen", "text scale list"]},
      {"title": "UI ELEMENTS", "position": "upper center-right", "count": 7, "labels": ["{argument name=\"cta button\" default=\"EXPLORE button\"}", "rounded tab 1", "rounded tab 2", "horizontal slider", "toggle switch", "{argument name=\"theme pill 1\" default=\"BLACK HOLE pill button\"}", "{argument name=\"theme pill 2\" default=\"JUPITER pill button\"}"]},
      {"title": "CARDS", "position": "middle center-right", "count": 3, "labels": ["hero card with illustration", "secondary card", "small metric card"]},
      {"title": "DATA DISPLAY", "position": "lower middle-right", "count": 3, "labels": ["circular progress card", "line graph card", "horizontal control card"]},
      {"title": "bottom navigation", "position": "lower center", "count": 7, "labels": ["home", "cloud", "spark", "signal", "rounded rect", "heart", "tray"]},
      {"title": "VISUAL EXAMPLES", "position": "bottom row", "count": 5, "labels": ["{argument name=\"visual 1\" default=\"BLACK HOLE\"}", "{argument name=\"visual 2\" default=\"GRAVITY RING\"}", "{argument name=\"visual 3\" default=\"LIGHT GLOW\"}", "{argument name=\"visual 4\" default=\"NEBULA DUST\"}", "{argument name=\"visual 5\" default=\"GLASS SURFACE\"}"]}
    ],
    "centerpiece": "a dense arrangement of translucent dark cards and controls floating on a black canvas, organized like a premium design system poster"
  },
  "text": {
    "branding": "{argument name=\"headline text\" default=\"COSMIC GRAVITY\"}",
    "microcopy": "tiny uppercase sans-serif throughout, mostly illegible but styled as technical UI annotations",
    "key_numbers": {
      "percentage": "{argument name=\"percent\" default=\"87%\"}",
      "distance": "{argument name=\"distance\" default=\"779.3 M km\"}",
      "slider_value": "{argument name=\"slider\" default=\"79%\"}"
    }
  },
  "visuals": {
    "palette": [
      {"name": "bright white", "appearance": "soft glowing white swatch"},
      {"name": "warm sand", "appearance": "creamy beige swatch"},
      {"name": "muted plum", "appearance": "dusky violet swatch"},
      {"name": "deep navy", "appearance": "blue-black swatch"},
      {"name": "teal black", "appearance": "dark teal swatch"}
    ],
    "theme_objects": "{argument name=\"theme objects\" default=[{\"name\": \"Jupiter-like planet\", \"appearance\": \"banded gas giant with thin glowing orbit ring\"}, {\"name\": \"black hole\", \"appearance\": \"dark circular center with bright accretion-like ring\"}, {\"name\": \"distant star\", \"appearance\": \"small bright golden point with faint halo\"}]}",
    "chart_motifs": ["glowing circular progress ring", "minimal mountain-like line graph", "horizontal value slider"]
  },
  "typography": {
    "primary": "sleek geometric sans-serif in uppercase with wide tracking",
    "specimen": "large Aa sample in white",
    "secondary": "small clean sans-serif for labels and data"
  },
  "colorScheme": {
    "primary": "{argument name=\"accent color\" default=\"warm amber gold\"}",
    "secondary": "{argument name=\"secondary glow color\" default=\"deep blue-violet\"}",
    "surface": "charcoal black translucent glass",
    "text": "soft white and muted gray"
  },
  "camera": {
    "view": "straight-on flat lay poster view",
    "composition": "balanced grid with generous negative space and thin panel borders"
  },
  "rendering": "ultra-detailed modern product design mockup, high contrast, elegant glassmorphism, crisp UI kit presentation, subtle blur and glow, premium concept sheet for a sci-fi app or dashboard"
}
```

#### 为什么这个模式有效（可复制原理）

1. **style 字段四层拆解**：`background / lighting / material / mood` 比写一整句散文精准 10 倍。每层独立管一个视觉维度。
2. **centerpiece 独立字段**：给模型一个**终极视觉概念锚**，其他字段都围绕它服务。不要把它塞到 `layout.description`。
3. **labels = 组件类型清单**（新模式）：不是具名实体（model 7 grid-list），而是"这一块我想看到哪 7 种组件类型"。模型负责具体渲染。
4. **数字和单位写死**：`87% / 779.3 M km / 79%` — UI mockup 不写死数字就生成胡话。
5. **"视觉现象" vs "概念名"**：写 `"dark circular center with bright accretion-like ring"` 而不是 `"black hole"` — 模型对视觉描述更可靠。
6. **主题耦合字段要参数化**：`"BLACK HOLE pill button"` / `"JUPITER pill button"` 这类按钮名必须 argument 化，否则换主题改 10+ 处。
7. **双 argument 配色方案**：`accent color` + `secondary glow color` 两个核心色参数化 = 一模板生 N 种主题。

#### 变体空间

| 变量 | 可替换值 |
|------|---------|
| 主题 | 深空探索 · 深海潜航 · 热带雨林 · 赛博朋克 · 极简白 · 文艺复兴油画感 |
| 材质 | 磨砂玻璃 · 镜面金属 · 纸质印刷 · 编织纤维 · 陶瓷釉面 |
| 光照 | 冷蓝 · 暖金 · 霓虹紫红 · 全白实验室 · 窄光源戏剧感 |
| 布局 | free-form organic · 6 列严格网格 · 单 hero + 环绕小组件 · 垂直长卷 |
| 导航图标数 | 5 / 7 / 9（按应用复杂度）|
| 组件复杂度 | Kit（10+ 组件）· Lite（5 组件）· Hero Only（2-3 组件）|

#### 反面清单

❌ style 字段写一整句散文 → 视觉决策模糊
✅ 拆成 background / lighting / material / mood 四层

❌ labels 里硬编码主题名（"JUPITER pill button"）→ 换主题改 10+ 处
✅ argument 化：`{argument name="theme pill 1" default="JUPITER pill button"}`

❌ 不写具体数字 → 模型生成胡话数字
✅ 数字 + 单位明写并参数化

❌ 写 "black hole" 指望模型理解 → 大概率失真
✅ 写"深色圆心 + 明亮吸积环"描述视觉现象

❌ 缺 centerpiece 字段 → 所有元素各做各的
✅ 一句 centerpiece 统领全局视觉概念

#### 参数化覆盖率建议

这个流派**天生适合 ⭐⭐⭐ 可复用模板**（80-95%）：

必抽：
- 主题名（theme name / headline text）
- 配色方案（accent / secondary）
- 主题特定组件名（theme pill 1/2 / visual examples 1-5）
- theme_objects 数组（星球/深海生物/树木等）

可以不抽：
- style 字段（材质/光照/mood 是流派签名）
- typography 结构（几何无衬线 + Aa specimen 是流派锚）
- 组件类型清单骨架（改了就不像 design system board）

参考原版案例只抽了 5 个 argument（13%，交际级）——**我们的改进版抽了 13 个（约 45%，仍只是交际级偏高）**。真正可复用模板需要把 sections[].labels 数组整体参数化到更高级别，此处为可读性折中。



### D. 手机截图 / Keynote 风

**iPhone Keynote 简陋截图**：
```
amateur iPhone screenshot of Keynote presentation,
slightly blurry handheld quality,
presenter's hand partially visible pointing at screen,
fluorescent office lighting reflection on device,
authentic iOS status bar,
slide content: [TITLE] with [BULLET POINTS],
messy casual conference aesthetic,
intentionally un-polished
```

**手写笔记照片**：
```
overhead iPhone photo of handwritten notebook page,
moleskine-style ruled paper,
mix of handwriting and small sketches,
blue ballpoint pen with occasional red annotations,
coffee cup visible at edge of frame,
warm desk lamp lighting,
authentic amateur photography
```

---

## 平台 UI 关键元素清单

### Twitter/X
- [ ] Logo (黑色 X 或蓝色鸟，看时代)
- [ ] 蓝钩（verified badge）位置、颜色
- [ ] Like 爱心 / Retweet 转发 / Reply 图标
- [ ] Timeline 顶部导航（For you / Following）
- [ ] Compose 按钮（蓝色圆形浮动）

### Douyin / TikTok
- [ ] 竖版 9:16
- [ ] 右侧交互按钮（爱心/评论/分享/音符）
- [ ] 底部用户名 + 描述文字
- [ ] 顶部"推荐 | 关注"切换
- [ ] 直播间独有：礼物特效、购物车按钮

### Instagram
- [ ] 方形/4:5/9:16 photo
- [ ] Stories 圆形头像在顶部
- [ ] 爱心/评论/分享/保存 图标
- [ ] 用户名 + 蓝钩
- [ ] Caption 展开/收起

### 微信 / WeChat
- [ ] 绿色背景泡泡（自己）右对齐
- [ ] 白色背景泡泡（对方）左对齐
- [ ] 头像方形圆角
- [ ] 时间戳格式 "X分钟前"

---

## 历史人物现代化技巧

### 风格反差产生戏剧性
```
[HISTORICAL PERIOD oil painting aesthetic] × [MODERN UI element]
```

示例：
- 乾隆画像 + 朋友圈九宫格 = 戏剧
- 希腊神话油画 + Instagram Stories = 戏剧
- 秦兵马俑 + 抖音直播间 = 戏剧

### 语言风格的时代错置
```
bio written in [PERIOD tone] but format follows [MODERN structure]:
- Tweet length but ancient Chinese grammar
- Hashtags in classical phrasing
- Emoji replaced with period-appropriate symbols
```

### 互动数据也要时代化
- 慈禧的推特：点赞数用"万" 而非 "k"
- 乾隆朋友圈：评论有太监/大臣身份标注
- 奥特曼棒球直播：观众名字显示为代码风格

---

## 完整案例模板

### 历史人物社媒
```
ultra-realistic [PLATFORM] screenshot mockup,
[HISTORICAL FIGURE, period specified]'s personal profile,
profile photo: authentic period portrait of figure (oil painting/woodblock),
display name in their historical language,
username "@[romanized handle]",
bio: "[PERIOD-APPROPRIATE tone description of role and interests]",
3 recent posts visible:
1. [HISTORICAL CONCERN translated to modern social media voice]
2. [PERIOD EVENT described as viral moment]
3. [PERSONAL OBSERVATION in thoughtful long-form]
UI elements: accurate [PLATFORM] 2026 mobile layout,
realistic timestamps (hours/days ago),
engagement metrics appropriate to figure's fame,
authentic fonts and color scheme,
9:16 mobile screenshot ratio,
subtle image compression artifacts
```

### 抖音直播
```
realistic Douyin livestream screenshot captured mid-session,
9:16 vertical iPhone mobile view,
[HOST] in center frame: [APPEARANCE + CURRENT ACTION],
flying heart animations floating up-right,
massive gift popup "xxxx送出了[GIFT]" in center,
LIVE indicator top-left with red pulsing dot,
viewer count "[NUMBER]万观看" top-right,
scrolling chat on right side: 6-8 messages visible with usernames,
bottom bar: comment input on left, gift icon, share icon,
"加购物车" yellow button on right side,
Douyin 2026 UI perfectly replicated
```

---

## 反面清单

❌ 让 AI 自由发挥 UI → 会生成四不像，非真实平台
✅ 明确指定"accurate [PLATFORM] UI"+ 关键元素清单

❌ 历史人物直接穿现代衣服 → 丢失反差
✅ 保留历史画像作为头像，只让 UI 是现代

❌ 让文字"随便写写" → 会乱码/没意义
✅ 具体写出发的内容，包括文字、emoji、hashtag

❌ 没指定 9:16 → 会出桌面端 UI
✅ 明确"9:16 mobile screenshot"
