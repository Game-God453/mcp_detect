# 角色场景模板案例库（Character Scene Templates — Raw Data）

> Neal 投喂的 9 条 GPT-Image-2 / Nano Banana prompt（2026-05-09 收录）。
>
> **本质**：不是审美流派,是**给同一个角色 ID 套不同场景皮的可复用模板**。
> 每条模板的核心价值是「舞台 + 光线 + 姿势 + 服装」的组合,人物 ID 用参考图/留白/文字三种方式注入。

---

## 场景索引

| # | 场景标签 | 机位/视角 | 角色 ID 注入方式 | 画幅 |
|---|---|---|---|---|
| 1 | 夜拍自拍 Lo-fi Night Selfie | 平视极近景 | 留白(低质退化隐式) | 9:16 |
| 2 | 泳池俯拍 Abstract Pool Overhead | 正俯视 | 留白(matte rectangle) | 3:1 |
| 3 | 花田躺卧 Daisy Field Dream | 微俯视 | 留白(skin-tone blur) | 9:16 |
| 4 | 街头蹲姿 Lattice Fence Crouch | 平视全身 | 留白(mosaic blur) | 4:3 |
| 5 | 混凝土倚靠 Minimalist Interior Lean | 平视全身 | 留白(soft rect blur) | 4:5 |
| 6 | 厕所涂口红 Gritty Restroom Glamour | 平视半身 | **文字描述** | 未指定 |
| 7 | 沙漠西部 Western Desert Editorial | 平视全身 | **文字描述** + JSON | 2:3 |
| 8 | 日本校园漫画遮 Schoolroom Overhead | 正俯视 | **道具遮挡**(manga book) | 未指定 |
| 9 | 都市自拍 UGC Street Selfie | 手机高举下俯 | **参考图锁定**(uploaded portrait) | 9:16 |

---

## 案例 1 — 夜拍自拍 / Lo-fi Night Selfie

**场景特征**:夜晚、极近景、风格化柔焦、单一光源从侧打
**角色 ID 注入**:无参数化、无参考图、用 "soft-focus perfection + low quality night selfie" 做风格化退化,让面部隐式去识别
**参数化变量**:无(全文字描述)
**画幅**:9:16 vertical
**关键字段**:
- 开头风格三连触发词:`Super close up, extra details, low quality night selfie`
- 环境:`deep obsidian void of the night`
- 光线:`warm golden light from the side, left side in soft cinematic shadow`
- 氛围:`nocturnal beauty / reverie / intimate`

**原始 prompt**:
```
Super close up, extra details, low quality night selfie. In a vertical 9:16 reverie, the canvas is dominated by the luminous presence of a young woman in her early twenties, her features a study in ethereal symmetry and porcelain grace characteristic of Northern European frost. Her face is framed by a cascading veil of long, platinum blonde hair that catches a warm, golden light from the side, creating a halo of delicate, stray wisps that dance against the deep, obsidian void of the night. Her eyes, deep and captivating with a subtle feline tilt, are accentuated by soft, winged eyeliner and a hint of shimmer at the inner corners, gazing forward with a tranquil, mesmerizing depth. The skin of her face is flawless and radiant, possessing a soft-focus perfection that highlights high, elegant cheekbones and a straight, refined nose. Her lips, full and naturally flushed with a dusty rose hue, are set in a soft, enigmatic expression that enhances her supermodel-like allure. She is dressed in a simple white top layered under a heather gray zip-up hoodie, the metallic teeth of the zipper catching the light and adding a tactile contrast to the softness of her hair and skin. Her build appears lithe and delicate, posed with a natural poise that commands the frame even in this intimate close-up. The light source, positioned to her right, casts a gentle gradient of warmth across her features while leaving the left side in a soft, cinematic shadow, rooting the composition in a moment of quiet, nocturnal beauty.
```

---

## 案例 2 — 泳池俯拍 / Abstract Pool Overhead

**场景特征**:正俯视,水下漂浮,水纹铺满画面,极端留白
**角色 ID 注入**:留白(matte rectangular square 遮脸),色块颜色可参数化匹配皮肤色或服装色
**参数化变量**:`subject`, `hair color`, `face cover color`
**画幅**:3:1 ultra-wide
**关键字段**:
- 机位:`directly above` + `floating just beneath the surface`
- 环境填充:`bright sun-caustic ripples covering the entire frame`
- 色调:`deep teal and turquoise, soft green-blue color grading`
- 构图:`slightly left of center, upper half` + `Leave large areas of open rippling pool water to the right and left`

**原始 prompt**:
```
Create an ultra-wide 3:1 cinematic photograph shot from directly above a {argument name="subject" default="single swimmer"} floating just beneath the surface of a clear swimming pool. The water is deep teal and turquoise with bright sun-caustic ripples covering the entire frame. Place the swimmer slightly left of center near the upper half of the composition, with curly {argument name="hair color" default="brown hair"} spreading in the water, one long arm arcing upward and across the right side, and the body fading into darker shadow below the surface. The face is obscured by a centered matte {argument name="face cover color" default="beige"} rectangular square, creating an anonymized editorial look. Use natural midday sunlight, realistic underwater refraction, soft green-blue color grading, subtle film grain, high detail, and a calm isolated mood. Leave large areas of open rippling pool water to the right and left, no text, no borders, no extra people.
```

---

## 案例 3 — 花田躺卧 / Daisy Field Dream

**场景特征**:金色时分花田,侧卧蜷曲,skin-tone 柔边方形模糊
**角色 ID 注入**:留白(soft-edged square blur in warm brown skin tones),柔和融入不破坏画面
**参数化变量**:`character description`, `dress description`
**画幅**:vertical
**关键字段**:
- 机位:`from above at a slight angle with an intimate close composition`
- 环境填充:`countless white daisy petals with yellow centers and tall stems in the foreground and background`
- 光线:`warm natural sunlight, soft highlights, gentle shadows from grass and flowers`
- 相机:`85mm lens look, f/1.8, dreamy shallow depth of field, creamy bokeh, 35mm film photography style`
- 风格:`realistic film photography style, natural color grading, soft contrast`

**原始 prompt**:
```
Ultra-realistic cinematic vertical photo of {argument name="character description" default="a young Korean woman"} lying on her side in a lush field of white daisies and tall green grass during golden hour. She wears {argument name="dress description" default="a soft light gray sleeveless dress with delicate ruffled neckline and a gently flowing skirt"}. Her long straight dark brown hair is spread naturally through the grass and slightly lifted by the breeze. Her body is curled in a relaxed pose, one arm bent near her head and the other resting in front of her, with bare legs partly visible among the flowers. The face is intentionally obscured by a centered soft-edged square blur in warm brown skin tones, hiding all facial details while leaving the hair, neck, shoulders, and body visible. Shoot from above at a slight angle with an intimate close composition, surrounded by countless white daisy petals with yellow centers and tall stems in the foreground and background. Use warm natural sunlight, soft highlights on skin and fabric, gentle shadows from grass and flowers, dreamy shallow depth of field, creamy bokeh, realistic film photography style, natural color grading, soft contrast, 85mm lens look, f/1.8, high detail, 4k, ultra realistic.
```

---

## 案例 4 — 街头蹲姿 / Lattice Fence Crouch

**场景特征**:瓷砖步道 + 白色格子围栏透视延伸,蹲姿捧脸,街拍感
**角色 ID 注入**:留白(soft square mosaic blur)
**参数化变量**:`subject age and gender`, `hair color`, `sweater color`, `skirt color`, `watermark text`
**画幅**:4:3 vertical
**关键字段**:
- 姿势:`crouching low, both elbows on knees, hands cupping her cheeks in a shy, pensive pose`
- 环境引导线:`white geometric fence receding into the background on the right`
- 风格:`candid street-photography feel, muted neutral colors`
- **水印参数化**:`semi-transparent watermark reading {watermark text} in the lower-left corner`

**原始 prompt**:
```
Create a photorealistic full-body outdoor fashion portrait of an {argument name="subject age and gender" default="adult young woman"} crouching low on a pale tiled walkway beside a white lattice fence. She has long straight {argument name="hair color" default="dark brown hair"} falling over her shoulders, her face intentionally obscured by a soft square mosaic blur, and she rests both elbows on her knees with her hands cupping her cheeks in a shy, pensive pose. She wears a fitted {argument name="sweater color" default="navy blue"} knit sweater with ribbed cuffs, a short {argument name="skirt color" default="beige"} skirt, sheer black tights, and black platform high-heel pumps. Use a shallow depth of field with the background softly blurred, natural daylight, muted neutral colors, realistic skin and fabric texture, a candid street-photography feel, vertical 4:3 composition, subject positioned slightly left of center, white geometric fence receding into the background on the right, and a subtle semi-transparent watermark reading {argument name="watermark text" default="YOUR BRAND"} in the lower-left corner.
```

---

## 案例 5 — 混凝土倚靠 / Minimalist Interior Lean

**场景特征**:室内混凝土柱/楼梯/窗格几何,全身倚靠站姿,documentary editorial
**角色 ID 注入**:留白(soft rectangular blur)
**参数化变量**:`subject`, `top`, `location`, `watermark text`
**画幅**:4:5 vertical
**关键字段**:
- 姿势:`leaning casually against a large pale concrete pillar, shoulders against the wall, both hands tucked into the front pockets, one leg crossed slightly in front of the other, barefoot`
- 环境:`wide staircase rising on the right, angular concrete railings, geometric window latticework near the top`
- 光线:`soft natural daylight casting long shadows across the floor and wall`
- 色调:`muted gray and blue color palette`
- 风格标签:`documentary editorial photography style`

**原始 prompt**:
```
Create a photorealistic full-body fashion portrait of {argument name="subject" default="a young adult woman"} leaning casually against a large pale concrete pillar in a modern minimalist interior. She has long dark brown wavy hair and an intentionally obscured face covered by a soft rectangular blur, with a relaxed posture, shoulders against the wall, both hands tucked into the front pockets of loose high-waisted wide-leg blue jeans. She wears {argument name="top" default="a plain white short-sleeve T-shirt"} and is barefoot, with one leg crossed slightly in front of the other. The setting is {argument name="location" default="a contemporary concrete stairwell with polished dark floors"}, featuring a wide staircase rising on the right, angular concrete railings, geometric window latticework near the top, and soft natural daylight casting long shadows across the floor and wall. Use realistic proportions, natural skin tones, subtle fabric folds, detailed denim texture, shallow depth of field, muted gray and blue color palette, documentary editorial photography style, vertical composition, 4:5 aspect ratio. Add a semi-transparent white watermark reading {argument name="watermark text" default="YOUR BRAND"} in the bottom-left corner.
```

---

## 案例 6 — 厕所涂口红 / Gritty Restroom Glamour

**场景特征**:脏乱公厕涂鸦 + 粉色荧光灯 + 涂口红动作,光鲜与腐败对撞
**角色 ID 注入**:**文字描述完整**(不挡脸,脸是主角,`confident gaze`、`head slightly turned`)
**参数化变量**:`subject`, `setting`, `outfit`
**画幅**:未指定
**关键字段**:
- 动作:`applying vibrant red lipstick with a lipstick tube in her right hand, left hand rests on the edge of a sink`
- 表情:`head slightly turned to the side with a confident gaze`
- 环境:`peeling light green tiles covered in colorful graffiti and stickers, cracked mirrors with reflections, scattered trash, damaged walls`
- 彩蛋:`a little graffiti written 'Keor' somewhere` — 参数化预留的"小写彩蛋"位
- 光线:`a pink fluorescent light tube on the ceiling casting dramatic pink and warm lighting`
- 氛围:`gritty urban atmosphere, moody cinematic composition`

**原始 prompt**:
```
A highly detailed cinematic photograph of a {argument name="subject" default="beautiful young woman with long wavy fiery blonde hair and fair skin with light freckles"}, standing in a {argument name="setting" default="uncleaned neglected public restroom with peeling light green tiles covered in colorful graffiti and stickers"}. She is wearing a {argument name="outfit" default="sleek white glitter strapless mini dress"} and applying vibrant red lipstick with a lipstick tube in her right hand while her left hand rests on the edge of a sink. Her head is slightly turned to the side with a confident gaze. The environment features cracked mirrors with reflections, scattered trash and paper on the floor and counters, a little graffiti written 'Keor' somewhere, a pink fluorescent light tube on the ceiling casting dramatic pink and warm lighting, damaged walls, and an overall gritty urban atmosphere with high detail, realistic textures, and moody cinematic composition.
```

---

## 案例 7 — 沙漠西部 / Western Desert Editorial

**场景特征**:金色时分沙漠 + 皮革紧身 + 宽檐牛仔帽,JSON 字段分层结构
**角色 ID 注入**:文字描述(eyes closed 是表情选择不是遮挡)
**参数化变量**:`subject description`, `hair style`, `lighting`
**画幅**:2:3
**关键字段**:
- 表情:`eyes closed with a calm dreamy expression`
- 环境:`sunlit desert landscape with rocky mountains in the background`
- 服装:`dark brown leather corset dress with vintage western details, lace accents, and multiple studded belts`
- 配饰:`translucent amber bangles, a wide-brim dark cowboy hat resting behind her shoulders`
- 光线:`warm golden-hour lighting`
- 相机:`85mm f/1.8 shallow DOF`
- **结构**:用 JSON 把 prompt/negative_prompt/style/lighting/camera/quality/aspect_ratio 字段分层,**工程化最高的一条**

**原始 prompt**:
```json
{
 "prompt": "{argument name=\"subject description\" default=\"A stunning red-haired woman standing in a sunlit desert landscape with rocky mountains in the background. She wears a dark brown leather corset dress with vintage western details, lace accents, and multiple studded belts around her waist.\"} Her {argument name=\"hair style\" default=\"long wavy ginger hair\"} flows naturally in the wind, eyes closed with a calm dreamy expression. Accessories include translucent amber bangles and a wide-brim dark cowboy hat resting behind her shoulders. {argument name=\"lighting\" default=\"Warm golden-hour lighting\"}, cinematic composition, ultra-detailed skin texture, soft shadows, shallow depth of field, fashion editorial style, realistic photography, earthy desert tones, high detail, 85mm lens look.",
 "negative_prompt": "blurry, low quality, extra limbs, deformed hands, duplicate accessories, cartoon, anime, overexposed, distorted face, cropped head, unrealistic proportions, noisy image",
 "style": "cinematic western fashion editorial",
 "lighting": "golden hour natural sunlight",
 "camera": {
 "lens": "85mm",
 "aperture": "f/1.8",
 "depth_of_field": "shallow"
 },
 "quality": "ultra detailed",
 "aspect_ratio": "2:3"
}
```

---

## 案例 8 — 日本校园漫画遮 / Schoolroom Overhead

**场景特征**:榻榻米房间 + 漫画书 + 复古相机,正俯视,午后阳光条纹
**角色 ID 注入**:**道具遮挡**(manga book 遮住嘴和下巴,只露眼睛和鼻子一部分) — 第 6 种挡脸方式,最自然最有叙事感
**参数化变量**:无(全文字)
**画幅**:未指定
**关键字段**:
- 机位:`Overhead top-down camera angle directly above her`
- 姿势:`lying on a floor, staring directly at the camera while holding a manga book in front of her face`
- 遮挡:`covering her mouth and chin so that only her eyes and part of her nose are visible`
- 环境:`surrounded by vintage analog cameras, a retro cassette tape recorder, disposable camera, Japanese soda can`
- 光线:`warm afternoon sunlight streaming through a window, creating dramatic striped shadows`
- 风格:`nostalgic Japanese youth aesthetic, cozy retro Japanese room, 35mm film look`
- Negative prompt:包含 `anime, cartoon, CGI` 防止走动漫风

**原始 prompt**:
```
A Japanese teenage girl wearing a white sailor school uniform with a navy blue collar, lying on a floor, staring directly at the camera while holding a manga book in front of her face, covering her mouth and chin so that only her eyes and part of her nose are visible. Overhead top-down camera angle directly above her. Long black hair naturally spread across the tatami mat. Surrounded by vintage analog cameras, a retro cassette tape recorder, disposable camera, Japanese soda can, and small aesthetic accessories. Warm afternoon sunlight streaming through a window, creating dramatic striped shadows. Cinematic lighting, nostalgic Japanese youth aesthetic, moody atmosphere, soft shadows, photorealistic, realistic skin texture, ultra detailed, editorial photography style, 35mm film look, cozy retro Japanese room, authentic tatami texture, shallow depth of field, high realism.

Negative prompt: blurry, low quality, extra fingers, bad anatomy, distorted hands, duplicate objects, deformed face, extra limbs, overexposed, watermark, text artifacts, anime, cartoon, CGI
```

---

## 案例 9 — 都市自拍 / UGC Street Selfie

**场景特征**:红砖公寓街道 + 手机自拍向下俯角 + girl-next-door 真实感
**角色 ID 注入**:**参考图锁定**(`Use the uploaded portrait as the facial identity reference`) — 最高级的注入方式
**参数化变量**:`subject`, `hair style`, `outfit`
**画幅**:9:16
**关键字段**:
- 多模态 ID 指令(第一句):`Use the uploaded portrait as the facial identity reference`
- 机位:`phone is raised high, shooting from a downward selfie angle` — 手机自拍物理视角工程化
- 表情:`looks up naturally at the camera with a soft, fresh, girl-next-door expression`
- 环境:`red brick apartment buildings, balconies, air conditioners, roadside greenery, trees, a clean road extending into the distance` — 具体到空调外机这种"真实日常元素"
- 光线:`bright soft natural daylight, casual summer vibe`
- 风格:`photorealistic phone selfie`(明确反 cinematic)
- **Negative 防小错**:`cropped feet, missing shoes, unnatural body proportions`

**原始 prompt**:
```
Use the uploaded portrait as the facial identity reference. Create a highly realistic 9:16 smartphone selfie of a {argument name="subject" default="young woman"} standing on a quiet residential street. The phone is raised high, shooting from a downward selfie angle. She looks up naturally at the camera with a soft, fresh, girl-next-door expression. She has {argument name="hair style" default="long dark twin ponytails, loose wispy hair strands"}, fair smooth skin, natural makeup, and a slim natural figure.
She wears a {argument name="outfit" default="white spaghetti-strap camisole, light pink shorts, white socks, and white Crocs-style clogs"}. Show her upper body, shorts, legs, socks, and shoes clearly. The background features red brick apartment buildings, balconies, air conditioners, roadside greenery, trees, and a clean road extending into the distance. Bright soft natural daylight, realistic skin texture, casual summer vibe, photorealistic phone selfie, no text, no watermark

Negative Prompt:
low quality, blurry, overexposed, distorted face, bad anatomy, extra fingers, deformed hands, unnatural body proportions, plastic skin, heavy makeup, cartoon, anime, CGI, fake background, messy composition, cropped feet, missing shoes, text, logo, watermark
```

---

## 九条横向对比表（按场景/机位/风格分类）

| # | 场景 | 机位 | 姿势类 | 服装风格 | 光线 | 画幅 | ID 注入 | 风格标签 |
|---|------|------|--------|----------|------|------|---------|----------|
| 1 | 夜空 | 平视极近景 | 正面凝视 | hoodie+白T | 夜色单侧暖光 | 9:16 | 留白(退化) | low quality night selfie |
| 2 | 泳池水下 | 正俯视 | 漂浮+arcing arm | 泳装(暗) | 中午阳光水纹 | 3:1 | 留白(色块) | cinematic underwater |
| 3 | 花田 | 微俯视 | 侧卧蜷曲 | 灰色连衣裙 | 金色时分 | 9:16 | 留白(柔边) | film photography dreamy |
| 4 | 瓷砖步道+围栏 | 平视全身 | 蹲姿捧脸 | 针织+短裙+高跟 | 自然日光柔 | 4:3 | 留白(马赛克) | candid street |
| 5 | 混凝土室内 | 平视全身 | 倚靠插袋 | 白T+牛仔+赤脚 | 室内柔光 | 4:5 | 留白(软模糊) | documentary editorial |
| 6 | 脏乱公厕 | 平视半身 | 涂口红 | 亮片迷你裙 | 粉色荧光灯 | — | 文字描述 | gritty urban |
| 7 | 沙漠 | 平视全身 | 闭眼吹风 | 皮革紧身+牛仔帽 | 金色时分 | 2:3 | 文字 + JSON | western fashion editorial |
| 8 | 榻榻米房间 | 正俯视 | 躺姿漫画遮 | 水手服 | 窗外阳光条纹 | — | 道具遮挡 | Japanese youth aesthetic |
| 9 | 红砖住宅街 | 手机高举下俯 | 站姿自拍 | 吊带+短裤+Crocs | 明亮自然日光 | 9:16 | **参考图锁定** | photorealistic phone selfie |

---

## 角色 ID 注入机制总览(三路)

| 方式 | 子变体 | 适合 | 缺点 |
|---|---|---|---|
| **留白**(模糊/色块/道具/退化) | rectangular / soft blur / mosaic / object occlusion / style degradation | 需要后期贴脸、或先批量出片再选 | 要多一步后期 |
| **文字完全描述** | 正面/侧面/闭眼等表情具体写 | 模板独立可用、不依赖外部素材 | 同一角色跨多模板一致性差 |
| **参考图锁定** | `Use the uploaded portrait as the facial identity reference` | 同一角色批量跨场景出图,一致性最高 | 需要 GPT-Image-2 / Nano Banana 支持多模态输入 |
