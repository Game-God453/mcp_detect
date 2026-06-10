# Case Index — 126 个 GPT Image 2 真实 prompt 分类检索

> 数据来源：`raw-data/awesome-gpt-image-2-zh.md`（YouMind-OpenLab GitHub 仓库，126 案例）

## 怎么用

1. 从下表按**你要做的图像类型**找对应分类
2. 看标题挑 2-3 个感觉接近的案例
3. 去 `raw-data/awesome-gpt-image-2-zh.md` grep `### No. X:` 看完整 prompt
4. 仿造结构，换词汇/参数

**常用命令**：
```bash
# 看第 N 号案例完整内容
grep -A 200 '^### No. N:' raw-data/awesome-gpt-image-2-zh.md | head -200

# 搜关键词找类似案例
grep -n 'VTuber\|直播\|thumbnail' raw-data/awesome-gpt-image-2-zh.md
```

## 统计总览

- **总案例**：126
- **分类数**：9
- **JSON 结构**：75
- **自然语言**：51

## 个人资料 / 头像（20 个）

| No. | 名称 | 结构 |
|-----|------|------|
| 1 | Cosplay Selfie Prompt | 自然语言 |
| 2 | Personalized Minecraft Skin Prompt | 自然语言 |
| 3 | Vintage 35mm Flash Portrait | 自然语言 |
| 4 | Idol Maid Polaroid Collection | JSON |
| 5 | 4-Panel Professional Avatar Grid | JSON |
| 6 | Goth Style Transformation | 自然语言 |
| 7 | Graffiti Sketch AI Builder Style | 自然语言 |
| 8 | Photorealistic Anime Schoolgirl Crouching Portrait | 自然语言 |
| 9 | 3D Animated Character Expression Grid | JSON |
| 10 | Kawaii 3D Character Icon | 自然语言 |
| 11 | 神话角色头像网格 | JSON |
| 12 | 写实风格秋季和服人像 | 自然语言 |
| 13 | 定制 Logo 篮球自拍 | 自然语言 |
| 14 | 趣味动物贴纸套装 | 自然语言 |
| 15 | VTuber 个人资料卡生成器 | JSON |
| 16 | 涂鸦草图风格 AI Builder | 自然语言 |
| 17 | 3x3 角色肖像网格 | JSON |
| 18 | 历史皇帝肖像生成 | 自然语言 |
| 19 | 戏剧性湿发肖像摄影 | 自然语言 |
| 20 | 后台 Cosplayer 肖像 | 自然语言 |

## YouTube 缩略图（20 个）

> 💡 **子流派——日式信息产品徽章集群**：No. 61 / 62 / 63 属于同一模式的不同变体（金黑 / Neon / Business Neon）。
> 完整模式分析见 `structured-json-prompt.md` 模板 D2。
> 关键白话模板（来自 2026-04-24 Neal 投的日文版 No. 61）——用 **argument 覆盖率** 评估，见 `parametric-template.md`。

| No. | 名称 | 结构 |
|-----|------|------|
| 53 | Next-Gen Voxel Game Screenshot | 自然语言 |
| 54 | VTuber Stream Thumbnail | 自然语言 |
| 55 | VTuber Chat Stream Thumbnail | JSON |
| 56 | Pastel Pink VTuber Stream Thumbnail | JSON |
| 57 | Anime VTuber Livestream Thumbnail | JSON |
| 58 | VTuber Chat Stream Thumbnail | JSON |
| 59 | 日语网络研讨会缩略图生成器 | 自然语言 |
| 60 | VTuber 初配信缩略图 | JSON |
| 61 | 金色与黑色风格信息产品缩略图 | JSON |
| 62 | Neon AI 副业 YouTube 缩略图 | JSON |
| 63 | 霓虹商务信息产品缩略图 | JSON |
| 64 | 欧冠高光时刻卡片生成器 | 自然语言 |
| 65 | 古典钢琴家直播 | JSON |
| 66 | YouTube 直播界面模型 | JSON |
| 67 | VTuber 初配信直播封面 | 自然语言 |
| 68 | 动漫 VTuber 反应视频缩略图 | JSON |
| 69 | YouTube 直播演示界面模型 | JSON |
| 70 | 网红直播场景 | JSON |
| 71 | YouTube 开箱视频缩略图提示词 | 自然语言 |
| 72 | 真实犯罪调查缩略图 | 自然语言 |

## 漫画 / 故事板（18 个）

| No. | 名称 | 结构 |
|-----|------|------|
| 73 | Saint Seiya Golden Saints Card Grid | 自然语言 |
| 74 | Dynamic Anime Warrior with Whip-Sword | 自然语言 |
| 75 | Satirical 4-Panel Caricature Comic Strip | JSON |
| 76 | Two-Page Psychological Thriller Manga Spread | JSON |
| 77 | Manga Spread: Fantasy Game Developer | JSON |
| 78 | Food Pun Therapy Session | 自然语言 |
| 79 | Elderly Yakuza Drawing Katana | 自然语言 |
| 80 | Anime Movie Pitch Document with Poster and Settei | JSON |
| 81 | Dynamic Anime Magic Action Scene | 自然语言 |
| 82 | Futuristic Corporate 3-Panel Manga Page | JSON |
| 83 | 4-Panel Parody Movie Poster Grid | JSON |
| 84 | Anime Character Reference Sheet | JSON |
| 85 | Anime BBQ Girls Key Visual | 自然语言 |
| 86 | Anime Production Layout Sheet | JSON |
| 87 | Anime Light Novel Cover Illustration | 自然语言 |
| 88 | 5-Panel Manga Page: Creepy Delivery Man | JSON |
| 89 | Anime Fantasy Movie Poster | JSON |
| 90 | Watercolor Picture Book Cover | 自然语言 |

## 社交媒体帖子（17 个）

> 💡 **子流派——直播 UI 带批量元素**：No.22 (Douyin) / No.66 (YouTube 直播) / No.69 (YouTube Live) / No.70 (网红直播) 共享 **count + desc 模式**（完整原则见 `structured-json-prompt.md` 模式 6）。
> 💡 **meme/拼场面 YouTube 直播 mockup** 子模板见 `ui-mockup.md` “YouTube 直播 UI”章节（2026-04-24 Neal 投 Bilal×Sydney meme 提炼，已去掉真实名人名）。

| No. | 名称 | 结构 |
|-----|------|------|
| 21 | 4 格日式数字广告横幅网格 | JSON |
| 22 | Douyin Livestream Screenshot Prompt | 自然语言 |
| 23 | Surreal Gothic Hall with Floating Masks | 自然语言 |
| 24 | 7-Day Fashion Lookbook Infographic | JSON |
| 25 | Whiteboard Marker Anime Sketch | 自然语言 |
| 26 | Vintage Arcade Repair Flash Photography | 自然语言 |
| 27 | Satirical 4-Panel Product Ads | JSON |
| 28 | Food Recipe Flowchart Prompt | 自然语言 |
| 29 | Goth Girl on Unicorn Ride | 自然语言 |
| 30 | Historical Figure Social Media Mockup | JSON |
| 31 | Oriental Fantasy City Poster | 自然语言 |
| 32 | 3D Cinematic Multi-Panel Promo Poster | JSON |
| 33 | 5-Panel Mixed Style Collage | JSON |
| 34 | 2x2 SNS School Banner Ad Grid | JSON |
| 35 | 2x2 Grid of Online School Banner Ads | JSON |
| 36 | 2x2 Social Media Course Banner Ads | JSON |
| 37 | 9-Panel Self-Care Infographic Grid | JSON |

## 信息图 / 教育视觉图（15 个）

> 💡 **子流派——大规模栽格列表（Grid-List Poster）**：完整模式见 `grid-list-poster.md`，简概见 `structured-json-prompt.md` 模式 7。
> 2026-04-24 Neal 投的「AI COMPANIES IN 2026 10×10」作为本流派首批案例，目前 case-index 没收录原案例，但方法论已沉淀。

| No. | 名称 | 结构 |
|-----|------|------|
| 38 | Eastern Mythology Infographic Manuscript | 自然语言 |
| 39 | Fashion Design Process Infographic | JSON |
| 40 | Medical Infographic on Diabetes Progression | JSON |
| 41 | Medical Infographic of Gout Pathology | JSON |
| 42 | Camera Exploded View Infographic | JSON |
| 43 | Camera Exploded View Infographic | JSON |
| 44 | Botanical Growth Atlas Infographic | JSON |
| 45 | 3D Urban Systems Atlas Infographic | JSON |
| 46 | Encyclopedia Style Infographic Generator | 自然语言 |
| 47 | Pose and Lighting Analysis Sheet Transformer | 自然语言 |
| 48 | Scientific Optical Hardware Diagram | JSON |
| 49 | Optical Hardware Setup Diagram | JSON |
| 50 | Soccer Match Infographic Poster | JSON |
| 51 | Character Relationship Diagram Poster Generator | 自然语言 |
| 52 | Epic Concept/Movie Poster Generator | 自然语言 |

## 电商主图（14 个）

| No. | 名称 | 结构 |
|-----|------|------|
| 104 | Custom Building Block Set Photography | 自然语言 |
| 105 | Luxury Cosmetic Web Advertisement | 自然语言 |
| 106 | E-commerce Product Page Generator | 自然语言 |
| 107 | 直播带货界面模型 | JSON |
| 108 | 夏季海滩饮品商业摄影 | 自然语言 |
| 109 | 4 格广告网格概念 | JSON |
| 110 | 电商直播 UI 样机 | JSON |
| 111 | 药膳鸡汤标签设计转换 | 自然语言 |
| 112 | 机库中的跑车与客机 | 自然语言 |
| 113 | 逼真的 VTuber 周边商品样机 | 自然语言 |
| 114 | 直播电商 UI 原型 | JSON |
| 115 | 电商 LED 驱动器信息图 | JSON |
| 116 | 电商直播间 UI 设计稿 | JSON |
| 117 | 电商直播界面模型 | JSON |

## Design System / UI Kit 展板（新兴分类）

> 💡 **Dribbble / Behance 风格作品集**：单张图铺满调色板 / 组件库 / 卡片 / 数据可视化 / 视觉示例。
> 完整 JSON 模板 + 7 条可复制原理见 `ui-mockup.md` 的「主题化 Design System Board」章节。
> 关联技法：`structured-json-prompt.md` 技巧 1（style 四层拆解）+ 技巧 2（centerpiece 锚点字段）+ 模式 8（组件清单式批量）。
> **首批案例**：2026-04-24 Neal 投的「COSMIC GRAVITY 深空探索仪表板」—— case-index 暂未收录原案例，方法论已完整沉淀。

**典型子变体**：
- 玻璃拟态（Glassmorphism）
- 赛博朋克霓虹（Cyberpunk Neon）
- 深空/深海/赛博/极简 主题化 Board
- 纯 icon 展示板 / 纯色卡展示板 / 组件 kit only

## 产品营销（13 个）

| No. | 名称 | 结构 |
|-----|------|------|
| 91 | 动漫角色品牌形象与周边项目 | JSON |
| 92 | 深色模式病毒式营销案例研究落地页 | JSON |
| 93 | 18 面板吉祥物品牌识别文档 | JSON |
| 94 | Brand Identity System Board | JSON |
| 95 | Skincare E-commerce Landing Page Mockup | JSON |
| 96 | Men's Skincare Website Landing Page Mockup | JSON |
| 97 | Skincare E-commerce Landing Page | JSON |
| 98 | Beauty Product Landing Page Mockup | JSON |
| 99 | Fashion Collection Catalog Layout | JSON |
| 100 | Hyper-Energetic Japanese Promo Poster | JSON |
| 101 | Green Tea Bottle Advertisement Poster | JSON |
| 102 | Anime Strawberry Promo Banner Set | JSON |
| 103 | Anime Idol Merchandise Catalog | JSON |

## Featured（主推精选）（6 个）

| No. | 名称 | 结构 |
|-----|------|------|
| 1 | VR 头显爆炸视图海报 | JSON |
| 2 | 手绘城市美食地图 | JSON |
| 3 | 混合风格的桃太郎讲解 Slides | 自然语言 |
| 4 | 电商直播 UI 样机 | JSON |
| 5 | 动漫武术对决 | 自然语言 |
| 6 | 3D 石阶演化信息图 | JSON |

## 游戏素材（3 个）

| No. | 名称 | 结构 |
|-----|------|------|
| 118 | Retro Skeuomorphic Icons | 自然语言 |
| 119 | Open-World Game Screenshot Mockup | JSON |
| 120 | Voice Personification Character | JSON |

---

## 按需求快速定位

### 想做 YouTube/B站视频封面
- 看 **YouTube 缩略图** 分类（20 个）
- 重点：No.53 体素游戏截图、No.64 欧冠高光卡片、No.72 真实犯罪调查

### 想做直播间 / 电商 UI 截图
- 看 **电商主图** 分类 + Featured No.4 电商直播
- 重点：No.107 直播带货、No.114 直播电商 UI、No.117 电商直播间

### 想做信息图 / 教程图
- 看 **信息图 / 教育视觉图** 分类（15 个）
- 重点：No.38 东方神话、No.40 糖尿病医疗图、No.42 相机爆炸图、No.44 植物图鉴

### 想做个人头像 / 自拍风
- 看 **个人资料 / 头像** 分类（20 个）
- 重点：No.1 Cosplay Selfie、No.3 复古 35mm 闪光、No.9 3D 表情网格

### 想做产品爆炸图 / 解剖图
- Featured No.1（Meta Quest）、No.42/43 相机爆炸图
- 这是 centerpiece + callouts 的典型星图模式

### 想做旅行海报 / 3D 地图 infographic
- 看 **`poster.md` G 子类「3D Diorama Travel Infographic」**
- 首批案例：2026-04-25 Neal 投的 Switzerland / New Zealand / Egypt 三版对照
- 关联技法：`parametric-template.md` 地理分层字段 + `structured-json-prompt.md` 散文 vs JSON 实证

### 想做手绘地图 / 城市指南
- Featured No.2（成都美食地图）
- 这是并行数组模式的典型

### 想做漫画多格分镜
- 看 **漫画 / 故事板** 分类（18 个）
- 重点：No.75 讽刺 4 格漫画、No.82 三格未来企业漫画、No.88 5 格配送员漫画

### 想做品牌识别 / VI 系统板
- 看 **产品营销** 分类（13 个）
- 重点：No.93 18 格吉祥物品牌文档、No.94 Brand Identity Board、No.99 时尚系列画册

### 想做动作分镜表 / img2video 的舞蹈或打斗序列
- 看 **`character-sheet.md` 模式 E「Movement Sheet / pose-as-prompt」**
- 项目溯源：2026-04-26 Oggii × Seedance 2.0（X @oggii_0 案例）
- 启示：img2video 的时序控制瓶颈用 16 格动作表绕过，适合短舞蹈/打斗/体操等有序列的动作视频
