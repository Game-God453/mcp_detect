# Scene Composite & Style Transfer Patterns

## 什么时候用

- 跨风格拼贴（如"Counter-Strike 风格的 Terraria 截图"）
- 名人置入虚构场景（如"Sam Altman 拍的熊自拍"）
- 游戏引擎风格截图仿制（Minecraft/Rust/Among Us）
- 史诗叙事向海报（剪影 + 宏大场景）
- 多概念战斗海报集（角色群像 + 背景叙事）

## 核心理念：**反差即戏剧**

这类 prompt 的威力在于**组合两个不应出现在一起的元素**，产生新鲜感和传播力。

### 反差配方

| 元素 A | 元素 B | 产生效果 |
|--------|--------|----------|
| 名人 | 日常/荒谬场景 | 段子传播感 |
| 严肃历史 | 游戏截图风 | Meme 向病毒传播 |
| 游戏 A | 游戏 B 画风 | 粉丝社区热议 |
| 真实新闻 | 戏剧化渲染 | 新闻美学化 |
| 抽象概念 | 超写实场景 | 哲思向艺术 |

---

## 五大模式

### A. 游戏引擎风格伪截图

**Minecraft 风**：
```
realistic Minecraft screenshot of [SCENE],
default Minecraft textures (16x16 pixel blocks),
authentic Minecraft UI: health bar, hotbar at bottom,
coordinates top-left (F3 debug hidden),
[TIME OF DAY] lighting as Minecraft renders it,
blocky voxel aesthetic applied to [SUBJECT],
Minecraft hand holding [ITEM] at bottom-right,
first-person perspective,
authentic Minecraft world generation feel
```

**Rust / Among Us / Terraria**：
- **Rust**: `Rust game screenshot, wasteland aesthetic, rusted metal UI, inventory visible`
- **Among Us**: `Among Us screenshot with realistic 3D rendering, but preserving the iconic bean-shape crewmate silhouettes`
- **Terraria**: `Terraria 2D side-scrolling screenshot, sprite-based but applied to [THEME]`
- **Counter-Strike**: `CS:GO screenshot from first-person, HUD overlay, crosshair, weapon in hand`

**跨引擎混搭经典**：
- `CS:GO × Terraria` — 2D 侧视图游戏用 CS 的 HUD
- `Minecraft × Dark Souls` — 方块世界 + 黑魂的阴郁氛围

### B. 名人置入荒谬场景

**基本结构**：
```
authentic amateur [PHOTOGRAPHY TYPE] of [CELEBRITY NAME] [UNEXPECTED ACTION/LOCATION],
[CELEBRITY]'s recognizable features accurately rendered,
[ENVIRONMENTAL DETAILS that create absurdity],
candid documentary style,
[LIGHTING TYPE],
slightly blurry/grainy for authenticity
```

**案例模板**：
```
authentic amateur iPhone snapshot of Sam Altman skateboarding
at a suburban skatepark at sunset,
Altman wearing casual hoodie and jeans, mid-ollie pose,
concerned expression, slight motion blur on skateboard,
other skaters in background ignoring him,
golden hour warm lighting with long shadows,
candid documentary photograph quality,
shot from low angle through chain-link fence,
amateur composition with slight tilt
```

**效果**：
- 越日常越好笑（踩滑板、吃饭、遛狗）
- 越严肃人物 × 越荒谬动作越有爆发力
- 细节要"对"（衣着合理、环境可信），荒谬感靠情境不靠画质

### C. 叙事向史诗海报

**剪影宇宙海报**：
```
epic silhouette universe narrative poster,
dark foreground silhouette of [MAIN CHARACTER] against
dramatic sky,
in the sky/distance visible: miniature scenes of
[SUPPORTING CHARACTERS] in their respective story moments,
[SEPARATING ELEMENT like mountain range/ocean/city skyline] in middleground,
color gradient sky from [WARM] to [COOL] representing journey,
epic cinematic composition,
matte painting aesthetic reminiscent of [REFERENCE e.g. Lord of the Rings/Dune]
```

**多角色战斗海报**：
```
multi-concept battle poster featuring [N] characters
arranged in dynamic composition,
central conflict: [MAIN CHARACTER] vs [ANTAGONIST] in foreground,
supporting characters in middle zones with signature poses,
flashes of [ELEMENTAL POWERS] connecting characters visually,
background explosion/storm/magical phenomenon,
comic book inking style with digital color,
composition inspired by [REFERENCE e.g. shonen manga cover art]
```

### D. 概念艺术/暗黑幻想场景

**暗黑神话场景**（Lion Camel Ridge / 狮驼岭）：
```
dark mythical scene of [CHINESE/GLOBAL MYTH LOCATION],
horror reinterpretation of classical tale,
[MAIN SUBJECT - creature/deity] in imposing pose,
overgrown ruins of ancient [ARCHITECTURE TYPE],
bones and artifacts scattered in foreground,
bioluminescent fog, twin moons/eclipse overhead,
deep indigo and blood crimson color palette,
painterly digital art, [ARTIST INFLUENCE e.g. Zdzisław Beksiński, Yoshitaka Amano]
```

**高维投影场景**：
```
impossible 14th-dimension projection scene,
non-euclidean geometry with multiple perspectives overlapping,
recursive fractal architecture extending in all directions,
figure[s] experiencing temporal distortion,
color palette inspired by [PATTERN e.g. oil on water],
vertiginous sense of scale, M.C. Escher + Hans Bellmer influence,
hyperreal texture details at every zoom level
```

### E. 伪造杰作 / 风格混搭测试

**伪造大师杰作**（Forged Masterpiece）：
```
fake rediscovered painting attributed to [CLASSICAL ARTIST],
authentic period materials and techniques,
[SUBJECT] depicted with [ARTIST]'s characteristic brushwork,
oil on canvas texture, visible aged craquelure,
authentic period framing,
museum plaque below with fictional provenance,
styled to fool experts at first glance,
but subject is anachronistic: [MODERN SUBJECT]
```

例：
- 伦勃朗画 Gigachad
- 维米尔画 sneaker collection
- 莫奈画 data center

---

## 图像生成工具选择提示

不同模型擅长不同子类：

| 需求 | 推荐模型 | 理由 |
|------|---------|------|
| 名人真实感场景 | GPT-Image-2 / Flux Pro | 人脸识别准确 |
| 游戏截图伪造 | GPT-Image-2 | UI 文字最清晰 |
| 风格迁移 | SDXL + IPAdapter / MJ | 可控性强 |
| 抽象高维场景 | MJ v6+ / Flux | 美术感强 |
| 伪造大师画作 | MJ --stylize 高 | 风格模仿强 |

---

## 完整案例模板

### 名人荒诞场景
```
[PHOTO QUALITY] snapshot of [CELEBRITY FULL NAME] [DOING UNEXPECTED ACTIVITY]
at [SPECIFIC LOCATION],
accurate facial features and recognizable physical traits of [CELEBRITY],
wearing [SPECIFIC OUTFIT contextually appropriate or absurdly inappropriate],
[POSE AND ACTION DETAIL],
[ENVIRONMENT DETAILS - other people, weather, props],
[LIGHTING - time of day, artificial vs natural],
[CAMERA/PHOTO QUALITY - iPhone snapshot/paparazzi/official press photo],
candid unposed quality,
[SMALL ABSURD DETAIL that makes it funnier]
```

### 游戏风格迁移
```
realistic [SOURCE GAME] screenshot applied to [TARGET THEME],
[SOURCE GAME]'s distinctive visual elements perfectly replicated:
- UI overlay (health bar, inventory, minimap details)
- rendering style (pixel/voxel/cel-shaded/realistic)
- signature textures and art direction
but depicting [TARGET THEME]: [SPECIFIC SCENE],
preserving [SOURCE GAME]'s aesthetic while showing [UNEXPECTED CONTENT],
authentic in-game moment quality,
includes believable UI text and numerical values
```

### 史诗剪影海报
```
epic silhouette poster composition, 2:3 vertical format,
foreground: massive dark silhouette of [MAIN FIGURE] facing away,
[DIAGNOSTIC DETAIL that identifies figure within silhouette],
middleground: [ENVIRONMENTAL BARRIER - mountain/wall/sea],
background: dramatic sky containing miniature vignettes of:
- [STORY MOMENT 1] top-left
- [STORY MOMENT 2] center-top
- [STORY MOMENT 3] top-right
gradient from warm [COLOR] at horizon to cool [COLOR] at top,
matte painting cinematic quality,
lone dramatic element (bird/lightning/falling leaves) for movement,
inspired by [REFERENCE e.g. Attack on Titan finale poster]
```

---

## 反面清单

❌ 只说"Sam Altman doing something funny" → 没具体场景
✅ "Sam Altman skateboarding at suburban skatepark at sunset"

❌ "Minecraft style" 就完事 → 细节会不对
✅ 明确 UI 元素、16x16 贴图、默认材质、F3 调试界面等

❌ 试图让 AI 自由创作"有趣的"内容 → 会平庸
✅ 你自己定好荒诞配方（A × B），让 AI 执行

❌ 名人场景不加 "candid / amateur / authentic" → 会产出杂志摆拍感
✅ 强调业余质感、随手拍、不完美构图
