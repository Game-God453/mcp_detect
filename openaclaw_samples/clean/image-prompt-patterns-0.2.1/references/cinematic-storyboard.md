# Cinematic Storyboard & Stylized Painting Patterns

## 什么时候用

- 电影分镜 / 短片 storyboard
- 风格化插画（非写实）：油画、赛璐璐动画、漫画、工笔
- 有明确"作者锚点"的风格（Jibaro / LDR / Arcane / Spider-Verse / 铃木敏夫）
- 需要角色+风格+场景同时一致的序列图

**补充定位**：这一类 prompt 跟 `portrait.md` 的写实摄影不同，核心不是"精确还原真实"，而是"调用模型对某个风格/作者的记忆"。

## 核心配方

### 电影分镜 5 层结构（比摄影少 3 层）
```
[1. 主体 + 动作] + [2. 关键视觉细节] + [3. 光线色彩词汇] +
[4. 风格锚点 (Named artist / work / medium)] + [5. 比例 + 语境]
```

**为什么少 3 层？** 风格锚点（一个词如 "Jibaro style"）替代了摄影/材质/后期 3 层的细节控制。

### 信息密度对比

| 类型 | Prompt 字数 | 主要信息源 |
|------|------------|------------|
| 写实肖像（GPT-Image-2） | 150-250 词 | 分层堆叠具体描述 |
| 风格化分镜（MJ/Jibaro） | 40-80 词 | 风格锚点 + 叙事要素 |

→ 风格化 prompt **短而准**，长了反而干扰模型对风格的调用。

---

## 四大风格锚点类型

### A. 作者/作品锚点（Named Work）
最强力的风格调用方式。

**已验证有效的锚点**：
```
Jibaro art style / Love Death Robots Jibaro
Spider-Verse animation style / Into the Spider-Verse
Arcane animation style / Fortiche Production style
Studio Ghibli style / Hayao Miyazaki
Satoshi Kon animation style
Masaaki Yuasa animation style (Mind Game, Devilman Crybaby)
Hans Bellmer surrealism / Zdzisław Beksiński
Moebius (Jean Giraud) comic style
Egon Schiele expressionist line
Caravaggio chiaroscuro
```

**组合技**（两个锚点叠加）：
- `Jibaro × Caravaggio` — 赛璐璐 + 强光影对比
- `Ghibli × Moebius` — 温暖色彩 + 硬朗线条
- `Spider-Verse × Egon Schiele` — 多帧混合 + 扭曲表现

### B. 媒介锚点（Medium）
```
oil painting texture with visible brush strokes
watercolor on rough cotton paper
gouache illustration with flat color areas
Japanese ukiyo-e woodblock print
Chinese ink wash with calligraphy brushwork
digital matte painting for film concept art
2D cel-shaded animation with line boil
stop-motion clay puppet aesthetic
```

### C. 技法锚点（Technique）
```
hyper-saturated color palette
heavy motion blur as paint smear
radial blur from central vanishing point
Dutch angle tilted composition
extreme perspective foreshortening
backlit silhouette against bright sky
rim light separating subject from background
color desaturation in real-time as event progresses
```

### D. 情绪/氛围锚点（Mood）
```
operatic emotional intensity
melancholic contemplative stillness
frenetic kinetic aggression
dream-like detached surreality
tender intimate warmth
cold ruthless detachment
```

---

## 分镜 Prompt 模板

### 极简模板（40-60 词）
```
[SUBJECT + ACTION] [KEY VISUAL DETAIL],
[LIGHTING + COLOR],
[STYLE ANCHOR], [ASPECT RATIO]
```

例：
```
Warrior in ornate bronze Greek armor charging through dust clouds at dawn,
extreme radial motion blur, low angle ground-level POV,
spear tips catching golden sunlight,
oil painting texture, hyper-saturated amber and gold tones,
Jibaro art style, cinematic, 16:9 widescreen
```

### 情感戏模板（60-80 词）
```
[SHOT SIZE] of [SUBJECT(S)] [EMOTIONAL ACTION],
[BODY LANGUAGE DETAIL], [ENVIRONMENT CONTEXT],
[KEY LIGHT SOURCE] creating [VISUAL EFFECT on subject],
[COLOR PALETTE description with emotional quality],
[STYLE ANCHOR], [MOOD WORD], [ASPECT RATIO]
```

例：
```
Medium close-up of two Greek warriors in intimate embrace inside tent at night,
foreheads touching, fingers interlaced,
firelight glow on skin like burnished copper,
tender not sexual, warm honey amber tones,
oil painting texture, Jibaro style,
shallow focus background dissolves into abstract shapes, 16:9
```

### 动作戏模板（50-70 词）
```
[SHOT SIZE] [SUBJECT + ACTION VERB] at [LOCATION],
[MOTION TECHNIQUE e.g. motion blur, time dilation],
[IMPACT or KEY MOMENT DETAIL],
[COLOR SHIFT representing emotion],
[STYLE ANCHOR], [ASPECT RATIO]
```

### 对话戏模板（不需要动作）
```
[SHOT SIZE] of [CHARACTER] [EXPRESSION/MICROEXPRESSION],
[EYE DIRECTION / WHAT THEY'RE LOOKING AT],
[ENVIRONMENT context shown in BG with selective focus],
[LIGHTING setup emphasizing emotion],
[COLOR palette mood],
[STYLE ANCHOR], [ASPECT RATIO]
```

---

## 序列一致性技巧

分镜是**多图一组**，单图好看还不够，要保持：

### 1. 角色一致性
- **第一张先固定角色**：用最清楚的镜头（近景+中性表情）生成，作为后续 reference
- **char lock 描述**：每张都带同样的外貌关键词（hair color, scar, armor detail）
- **MJ 技法**：`--cref URL --cw 100` 用第一张做 character reference
- **GPT-Image-2 技法**：把第一张图作为 image input + 新 prompt

### 2. 风格一致性
- **style anchor 逐字复制**：每张 prompt 的风格词必须**一字不差**
- **palette 逐幕统一**：一个段落用同一套色词（比如全段都用 "amber and gold"）
- **seed 锁定**（MJ）：`--seed [NUMBER]` 保证噪声起点一致

### 3. 场景一致性
- **地点描述要固定**：不要这张是 "tent"，下张是 "camp"
- **时间要明确**：dawn / noon / golden hour / night 贯穿一幕

### 4. 跨幕变化
幕与幕之间**刻意变化**，但单幕内稳定：
```
幕一：Hot amber/gold palette
幕二：Cold ash-grey + single warm light
幕三：Deep night blue + gold accents
幕四：Liquid gold + turquoise
```

---

## 常见陷阱

### 风格污染
在同一条 prompt 里混用多个风格锚点，会产生四不像：
❌ `Jibaro style, Ghibli aesthetic, Pixar 3D rendering`  
✅ 选一个为主，其他用"情绪词"补充

### 过度细节
写实摄影 prompt 的技巧（解剖学词汇、具体光源命名）用到风格化 prompt 里会**抑制风格**：
❌ `Jibaro style close-up of warrior with almond-shaped eyes, high nose bridge, V-shaped jawline, porcelain skin with specular highlights`  
✅ `Jibaro style close-up of warrior's face with bloody paint-smear texture`

→ 风格化 prompt 信任锚点，把细节让给模型。

### 比例遗漏
分镜必须指定比例，否则输出随机：
- 电影：`16:9 widescreen` / `2.35:1 cinemascope`
- 手机竖屏：`9:16 vertical`
- 方形社媒：`1:1 square`
- 漫画格子：`4:3 panel format`

---

## 工具差异备忘

| 工具 | 风格化强度 | 角色一致性 | 推荐场景 |
|------|-----------|-----------|---------|
| **Midjourney v6+** | ★★★★★ | ★★★★（--cref） | 艺术分镜首选 |
| **Flux Pro** | ★★★ | ★★ | 写实感重的风格化 |
| **GPT-Image-2** | ★★ | ★★★（image ref） | 有指定文字元素时 |
| **SDXL + ControlNet** | ★★★★ | ★★★★★ | 需精确 pose 控制 |
| **Nano Banana Pro** | ★★★★ | ★★★ | 中国市场便利访问 |

---

## 项目溯源

**heels0409（Achilles' Heels）Jibaro 分镜实践**：
- Prompt 文件：`projects/heels0409/storyboard_prompts.md`
- 踩过的坑：
  - 早期 prompt 太长，稀释了 Jibaro 风格 → 改为 50-70 词
  - 尝试描述具体面部特征 → 模型出现写实漂移，不像 Jibaro
  - 红黑陶器画中画镜头：必须**另起 prompt**，完全不提 Jibaro
- 学到的：**一个项目用一种风格锚点，不要中途切换**，除非是画中画/回忆/双时空这类叙事需要

这份品类经验随后也同步到 `memory/craft-patterns/AI生成视频.md`。

---

### 伊卡洛斯改写（2026-04-24）

**原 prompt**：孙悟空战斗 prompt（盔甲、金箍棒、击杀天兵、云中宫殿）
**目标**：改成希腊神话伊卡洛斯

**关键决策**：不是机械替换「人物+武器+敌人」，而是重新识别**叙事核心动作**。

- 孙悟空的核心动作 = **战斗**（击杀）
- 伊卡洛斯的核心动作 = **坠落**

整个 prompt 的动作骨架从「战斗场面」重构为「坠落瞬间」：

| 原（战斗叙事） | 新（坠落叙事） |
|---|---|
| `in mid-combat` | `in mid-fall` |
| `fiercely strikes down enemies` | `plunges downward, arms outstretched, face contorted in anguish` |
| `glowing golden staff`（武器） | `melting wax drips and scattering feathers`（正在失败的东西） |
| `flying sparks, shattered debris` | `cascading feathers, streaming wax droplets` |
| `heavenly realm with pillars` | `blazing sun above, Aegean Sea below, distant silhouette of Daedalus` |

**保留的关键元素**：`distant silhouette of Daedalus still flying`——没有父亲的伊卡洛斯只是「飞太高的傻子」，有父亲才是悲剧。画面里必须有他。

**学到的方法论：神话/IP 改写公式**
1. 先问「这个主题的核心动作是什么」——不是外观、不是人物，是动作
2. 保留原 prompt 的技术骨架（镜头语言 / 光线 / 构图词汇）
3. 替换叙事元素（主体 + 敌手/对抗物 + 环境 + 粒子特效）
4. 保留「电影感词汇」，换「文化语义」

**变体技巧**：提供 pose 的多种情绪版本——狂妄版（defiant ecstasy）/ 觉醒版（sudden realization）/ 绝望版（curled inward）。让用户选情绪，不要替他做最终决定。

---

### 德国女孩跨文化改写（2026-04-22）

**原 prompt**：东亚女孩自拍（浅紫短发、涂鸦墙、街头风）
**目标**：改成 19 岁德国女孩

**关键改动**：

不能只改国籍词。AI 看到 `German woman` 但没有**骨相和肤质描述**时，会生成「东亚脸 + 金发」的怪物。

必须补充：
```
Sharp European features with a defined jawline, high cheekbones,
cool fair skin with a light rose undertone, and a few subtle freckles
```

**肤色温度**：东亚肤色偏暖（黄底），欧洲肤色偏冷（粉底/玫瑰底）。少一句 `cool undertone` AI 就容易出错。

**发色默认值选择**：`light purple` → `ash blonde`（冷灰调，不是加州阳光金）。

**风格锚点本土化**：`urban streetwear aesthetic` → `Berlin-inspired urban streetwear aesthetic`。加「Berlin」一词 AI 会调用对应的视觉记忆（粗粝、反精致）。

**学到的方法论：跨人种改写 checklist**
1. 骨相描述（jawline / cheekbone / nose bridge）
2. 肤色冷暖底（warm/cool undertone）
3. 头发材质 + 颜色调性（不是只改颜色词）
4. 面部细节（freckles / moles / eye shape）
5. 文化语境本土化（地名、品牌、视觉符号）

**否则的结果**：AI 生成「换了发色的东亚脸」——这是最常见的跨文化 prompt 失败模式。

---

### 拟人化自拍改写：布偶/德文卷毛（2026-04-24）

**原 prompt**：年轻男子在麦当劳自拍，T 恤 + 眼镜 + 手撑下巴 + 饮料杯 + 4 块菜单板 + 2 个路人
**目标**：改成布偶猫 → 再改成黑白开脸的德文卷毛猫

**关键决策 1：保留自拍构图物理**

猫不能自拍，但**构图逻辑要保留**——「手撑下巴」→「前爪放桌边」。这样画面有拟人的喜感而不是「随便拍了只猫」。

**关键决策 2：品种词要精确**

- ❌ `white fluffy cat` → AI 会生成波斯猫或缅因猫
- ✅ `Ragdoll cat with classic seal point coloring`
- ✅ `Devon Rex cat`（蝠耳 + 小脸 + 卷毛）

**花色术语对照**：

| 中文 | 英文术语 |
|---|---|
| 奶牛/黑白开脸 | `bi-color tuxedo with split facial mask` |
| 海豹色重点色 | `seal point coloring` |
| 橘猫 | `orange tabby with "M" marking on forehead` |
| 三花 | `calico` |
| 英短蓝 | `British Shorthair blue-gray` |

**关键决策 3：喜感细节 = 梗的来源**

- `eyeglass frames perched slightly crooked, half-sliding down`
- `T-shirt draped loosely over the shoulders as if playfully dressed`
- `deadpan, slightly judgmental expression`

删掉这些，AI 给你出「正经的宠物照片」而不是「会爆红的 meme」。

**关键决策 4：删掉只对人类有意义的设定**

原 prompt 里有 `face fully obscured by blur block`（保护隐私）。猫不需要打码——反而要让脸清晰，因为蓝眼睛/卷毛/杏仁眼这些品种标志是识别度核心。

**学到的方法论：拟人化换主体 checklist**
1. 保留原构图的物理骨架（姿势、机位、前景元素）
2. 用精确品种术语替换泛化词
3. 保留「梗的生成机制」（衣服歪、眼镜滑、表情 deadpan）
4. 删掉只对人类有意义的设定（打码、身份隐私）
5. 替换为品种特有的视觉 icon

---

## 元方法论：同结构换主题的 prompt 改写

2026-04-22 至 24 反复在做同一件事——用户给一个原 prompt，要求改成另一个主题但保留结构。标准流程：

### Step 1：感受先行

开口第一句必须是「这个主题要让人感觉到什么」——不是技术分析。

例：
- 孙悟空战斗 → 伊卡洛斯：先说「伊卡洛斯的核心不是战斗，是坠落」，再谈改写
- 蜘蛛侠 → 黑人英雄：先说「黑人英雄的文化内核不是 Uncle Ben 的训诫」，再谈改写

没有这步，prompt 就是机械替换，生成结果永远平庸。

### Step 2：识别原 prompt 的骨架

骨架包括：
- **结构骨架**（几个模块、几行 text_boxes、JSON 字段嵌套层）
- **叙事节奏骨架**（动作序列、情绪弧）
- **镜头/光线骨架**（机位、光比、调色）

骨架保留不动。

### Step 3：识别必须换的文化内核

问三个问题：
- 原主题的**文化母题**是什么？（盎格鲁中产道德 / 东亚集体审美 / 希腊悲剧）
- 新主题的**文化母题**是什么？
- 两者在**结构骨架的哪些节点**冲突？

例：
- 蜘蛛侠的「Uncle Ben 遗言」节点 → 黑人英雄必须换成「grandmother in church pew」
- 女装设计的「team collaboration 8 人」节点 → 爱马仕必须换成「single artisan」

### Step 4：术语精确化

泛化词会被 AI 降级：
- `fluffy cat` → `Ragdoll cat with seal point coloring`
- `superhero suit` → `matte navy and gold tactical suit with minimalist emblem`
- `European woman` → `cool fair skin with rose undertone, defined jawline, high cheekbones`

**术语精确度 = 生成质量上限**。

### Step 5：保留梗的生成机制

如果原 prompt 有喜剧/叙事张力细节（眼镜歪、杯子半满、光线从上而下），**一定要保留或对应翻译**。这些是图像的灵魂。

### Step 6：可选变体

给用户 3 种情绪 / 姿势 / 场景变体，让他自己选——不要替他做最终决定。

---

**沉淀教训（2026-04-24）**：这份元方法论以前只存在对话里，没进 skill。下次遇到 prompt 改写请求直接按这 6 步走，不要每次从零想。
