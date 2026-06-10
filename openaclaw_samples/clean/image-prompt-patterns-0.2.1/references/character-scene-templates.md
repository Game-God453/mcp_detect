# Character Scene Templates / 角色场景模板

> **用途**:把同一个角色 ID(你自己的 IP / 虚拟人 / 模特) 套进不同场景皮,批量生产同一角色在不同场景/姿势/服装下的形象。
>
> **核心工作模式**:场景是舞台,角色是演员,模板是让你快速换戏的道具。
>
> **原始案例**:见 `raw-data/character-scene-cases.md`(9 条 Neal 投喂,2026-05-09)

---

## 1. 为什么需要场景模板(而不是单次写 prompt)

单次写 prompt 的痛点:
- 换场景要重写 — 环境、光线、姿势、服装、相机参数全重来
- 换人要改一堆变量 — 发色、肤色、风格全散在文本里
- 同一角色跨场景**面部一致性**极差 — 每次文字描述略不同,AI 就给不同的脸

模板化的解法:
- **场景皮** 写死一次,存进库
- **角色变量** 参数化抽出(subject / hair / outfit / watermark)
- **角色 ID** 用参考图锁定(最稳)或参数化描述(次稳)
- 下次换戏:选模板 → 填参数 → 丢参考图 → 出图

## 2. 角色 ID 注入的三种机制(按一致性从低到高)

### 2.1 留白 + 后期贴脸(最灵活但要后期)
模板里用 **挡脸指令** 留一个占位:
- Rectangular solid(硬色块,编辑感)
- Soft-edged blur(skin-tone 柔边,融入)
- Mosaic blur(像素化,街拍感)
- Soft rectangular blur(纯模糊,极简)
- **Object occlusion(道具遮挡)** ← 第 6 种,有叙事含量(书/相机取景器/捧花/手/头发垂下)
- Style-degraded(low quality night selfie 这类风格化退化,隐式去识别)

**写法**:
```
The face is obscured by a centered matte {color} rectangular square
face intentionally obscured by a centered soft-edged square blur in warm brown skin tones
holding a manga book in front of her face, covering her mouth and chin so that only her eyes and part of her nose are visible
```

### 2.2 文字完整描述(独立可用,跨模板一致性差)
把人脸特征写进 prompt:
```
beautiful young woman with long wavy fiery blonde hair and fair skin with light freckles
```

问题:每个模板里这段描述的措辞略微不同 → AI 给出略微不同的脸。用于单张出图 OK,用于角色系列差。

### 2.3 参考图锁定(GPT-Image-2 / Nano Banana,一致性最高)
第一句显式写:
```
Use the uploaded portrait as the facial identity reference.
```

然后 prompt 里描述场景/姿势/服装即可。**这是批量生产同一角色的最佳实践**。

## 3. 场景模板的标准字段结构

每个模板推荐包含这些字段(部分可省):

```
[cinematic tag]                 # "photorealistic cinematic photograph" / "9:16 smartphone selfie"
[aspect_ratio]                  # 9:16 / 4:5 / 4:3 / 3:1 / 2:3
[ID_injection]                  # 留白 / 文字 / 参考图三选一
[subject_parametric]            # {argument name="subject" default="..."}
[pose_specificity]              # 精确到动作(crouching + hands cupping cheeks)
[outfit_parametric]             # {argument name="outfit" default="..."} 或 {top}/{skirt} 分拆
[environment_description]       # 具体场景 + 透视引导线 + 背景元素
[environment_parametric]        # {argument name="location" default="..."}(可选)
[lighting]                      # golden hour / pink fluorescent / soft daylight
[camera_params]                 # 85mm / f/1.8 / shallow DOF / 35mm film look
[composition_precision]         # "slightly left of center" / "leave open space to the right"
[style_tag]                     # candid street / documentary editorial / film photography / UGC phone selfie
[color_grading]                 # muted gray / teal-turquoise / warm earthy / nocturnal warm
[watermark_parametric]          # {argument name="watermark text" default="..."}(可选)
[negative_prompt]               # 统一防错列表
```

## 4. Negative Prompt 的"防小错"实战清单

这是 Neal 案例 9 带来的关键沉淀 —— 具体到身体部位和素材缺失的防错指令,比泛泛的 "bad anatomy" 有用十倍:

```
必备:
- blurry, low quality, overexposed
- distorted face, bad anatomy
- extra fingers, deformed hands
- unnatural body proportions

身体部位具体防错:
- cropped feet(确保脚在画面内)
- missing shoes(确保鞋没漏画)
- cropped head / cropped hands
- duplicate limbs / extra limbs

素材一致性:
- duplicate accessories(避免多戴一副耳环/一只表)
- duplicate objects
- text artifacts / watermark(模板自己要水印时另加)

风格防污:
- cartoon, anime, CGI(防走风格化)
- plastic skin, heavy makeup(防假)
- fake background, messy composition
```

## 5. 九条投喂案例的场景皮清单

(原始 prompt 在 `raw-data/character-scene-cases.md`)

| 场景 | 适用 | 标志性元素 |
|---|---|---|
| **Lo-fi Night Selfie** | 夜晚情绪向、ins 故事、个人风格自拍 | 单侧暖光、夜空虚无、super close up |
| **Abstract Pool Overhead** | 极简抽象封面、Vogue 风 | 水纹、3:1、色块挡脸 |
| **Daisy Field Dream** | 梦幻少女、春夏服装 lookbook | 花田、85mm、柔焦、金色时分 |
| **Lattice Fence Crouch** | 街拍 OOTD、品牌水印输出 | 蹲姿、围栏透视、水印角落 |
| **Minimalist Interior Lean** | 室内极简、documentary editorial | 混凝土、楼梯、4:5 Ins 原生 |
| **Gritty Restroom Glamour** | 反叛美学、摇滚 / 嘻哈 / 朋克 lookbook | 脏乱公厕、粉色荧光、涂口红 |
| **Western Desert Editorial** | 西部风、皮革服装、**JSON 工程化模板** | 沙漠、牛仔帽、金色时分 |
| **Schoolroom Overhead** | 日本青春怀旧、校服 lookbook | 榻榻米、漫画遮脸、俯视角 |
| **UGC Street Selfie** | **最高一致性批量生产**(参考图锁脸) | 手机下俯、红砖街、girl-next-door |

## 6. 快速套用流程(SOP)

1. **选场景** — 从上表或 `raw-data/character-scene-cases.md` 挑一个
2. **选 ID 注入方式** —
   - 有参考图 → 用 2.3(最稳)
   - 没参考图但角色只出一次 → 用 2.2(文字描述)
   - 想批量出图留后期 → 用 2.1(留白)
3. **填参数** — 把 `{argument name="..."}` 替换成当前角色/服装/场景细节
4. **追加 negative prompt** — 套用第 4 节清单
5. **出图** — GPT-Image-2 / Nano Banana / Midjourney 都能吃,Midjourney 把 argument 语法展平为普通文本

## 7. 工程化进阶:JSON 分层模板(案例 7)

最高阶的写法是把 prompt 拆成 JSON 字段,便于程序化替换:

```json
{
  "prompt": "...",
  "negative_prompt": "...",
  "style": "...",
  "lighting": "...",
  "camera": {
    "lens": "85mm",
    "aperture": "f/1.8",
    "depth_of_field": "shallow"
  },
  "quality": "ultra detailed",
  "aspect_ratio": "2:3"
}
```

优点:
- 程序可以逐字段替换,不用 regex 找 argument
- camera 参数独立一层,方便跨模板复用同一套相机设置
- negative_prompt 独立字段,不污染主 prompt

## 8. 参数化的"该"与"不该"

**该参数化**:
- subject / character description(换人)
- outfit / top / skirt / dress(换服饰)
- location / setting(换场景细节)
- face cover color(色块颜色匹配皮肤/服装)
- watermark text(换品牌)
- hair style / hair color(换发型发色)

**不该参数化**(会让模板崩):
- pose(每个姿势跟场景是一对一设计)
- camera_params(固定的 f/1.8 shallow DOF 是这个模板的视觉底色)
- aspect_ratio(画幅跟构图绑定)
- composition_precision("slightly left of center" 跟场景空间绑定)
- style_tag(风格标签跟整个模板精神绑定)

## 9. 下次扩展模板库时应该问的问题

Neal 投喂新 prompt 时,按这个清单看是不是独立���板:

- [ ] 场景是新的吗?(不是已有模板的微调)
- [ ] 机位 / 视角是新的吗?
- [ ] 姿势类是新的吗?(躺卧 / 倚靠 / 蹲姿 / 自拍 / 动态动作)
- [ ] 挡脸 / ID 注入方式是新的吗?
- [ ] 光线类型是新的吗?(自然光 / 霓虹 / 荧光 / 夜色 / 舞台光)
- [ ] 风格标签是新的吗?

**任意一个新 → 值得加进模板库**。全部重复 → 归入已有模板的变体。

## 10. 已覆盖 vs 待扩展

**已覆盖**:
- [x] 自拍(手机 + 夜拍)
- [x] 全身站姿(倚靠 + 沙漠)
- [x] 全身蹲姿
- [x] 俯视躺卧(花田 + 榻榻米 + 泳池)
- [x] 室内(公厕 + 混凝土)
- [x] 室外(街头 + 花田 + 沙漠 + 水)
- [x] 女性角色(9 条全部)
- [x] 亚洲 + 欧洲人设
- [x] 自然光 + 荧光灯 + 金色时分 + 夜色
- [x] 6 种挡脸方式 + 文字描述 + 参考图锁定

**待扩展**(下次投喂优先看):
- [ ] 男性角色
- [ ] 群体(2-3 人站位)
- [ ] 动态姿势(跑步 / 跳跃 / 骑行)
- [ ] 黑白色调
- [ ] 强对比硬光(戏剧光 / 舞台光 / 背光剪影)
- [ ] 儿童 / 老人角色
- [ ] 特殊视角(仰视 / 鱼眼 / 荷兰角)
- [ ] 运动场景(滑板 / 健身房 / 跑道)
- [ ] 室内特殊场景(酒吧 / 办公室 / 工业厂房)
- [ ] 季节性场景(雪地 / 秋天落叶)
