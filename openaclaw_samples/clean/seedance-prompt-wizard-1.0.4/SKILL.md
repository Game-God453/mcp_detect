---
name: seedance-prompt-wizard
description: >
  Seedance 2.0 提示词生成向导。通过引导式对话，
  逐步收敛用户需求，生成精准的 Seedance 2.0 Prompt。
  不做任何 API 调用，不涉及认证。
  触发词：帮我写提示词、生成视频提示词、Seedance提示词、视频生成提示词，制作提示词
---

# Seedance 2.0 · Prompt Wizard

> 版本：1.0.1
> 定位：纯提示词生成，不做 API 调用

---

## 一句话

通过引导式对话，将用户的模糊想法逐步收敛为精准的 Seedance 2.0 Prompt，直接可用。

---

## 模型选择

| 用户描述 | 判断模型 |
|---------|---------|
| 只有文字描述 | Text-to-Video |
| 有1-2张参考图 | Image-to-Video |
| 有图+视频/音频混用 | Reference-to-Video |

---

## 参数规格（仅供 Prompt 参考）

| 参数 | 默认值 | 可选值 |
|------|--------|--------|
| `duration` | 5秒 | 4-15秒 |
| `quality` | 720p | 480p / 720p |
| `aspect_ratio` | 16:9 | 16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9 |
| `generate_audio` | true | 含音效/配乐 |

---

## 对话流程（5步）

### Step 1：判断模型类型

根据用户描述判断：
- 纯文字 → Text-to-Video
- 1-2张图 → Image-to-Video
- 图+视频/音频 → Reference-to-Video

### Step 2：收集核心信息（每次最多2个问题）

```
① 视频内容是什么？（主体：人物/产品/场景/动物）
② 场景/背景是什么？
③ 有没有参考素材？（图/视频/音频）
④ 想要的风格或氛围？
```

### Step 3：确认输出参数

```
⑤ 时长？（默认5秒，最长15秒）
⑥ 比例？（默认16:9，短视频用9:16）
⑦ 需要音效吗？（默认含音效）
```

### Step 4：生成 Prompt

**Prompt 结构：**
```
[主体] + [场景/背景] + [动作/状态] + [镜头/运动] + [风格/光线/色调]
```

**@素材名 规则：**
```
@image1 = 第1张参考图（主体外观/场景/产品）
@image2 = 第2张参考图（备选）
@video1 = 第1个参考视频（镜头运动/动作）
@video2 = 第2个参考视频（辅助镜头）
@audio1 = 第1个参考音频（背景音乐/音效）
```

### Step 5：输出

---

## 追问话术

**关于素材：**
```
"有参考图/视频/音频吗？上传效果会好很多"
"图片几张？1张（首帧动画）还是2张（首尾过渡）？"
```

**关于风格：**
```
"想要什么氛围？比如：温馨/科技感/电影感/国潮"
"色调偏亮还是暗？暖色还是冷色？"
```

**关于镜头：**
```
"想要什么镜头感觉？比如：特写/全景/缓慢推进/环绕"
"有参考视频吗？镜头运动通过视频参考最稳定"
```

**关于动作：**
```
"画面中有什么动作？比如：人物走路/产品旋转/倒液体"
"动作要快还是慢？"
```

**关于音效：**
```
"需要配音或背景音乐吗？"
```

---

## 输出标准格式

```
━━━━━━━━━━━━━━━━━━━━
📋 精准 Prompt
━━━━━━━━━━━━━━━━━━━━
[完整中文 Prompt]

━━━━━━━━━━━━━━━━━━━━
📡 参考 API 参数
━━━━━━━━━━━━━━━━━━━━
model: [模型名]
duration: [时长]
quality: 720p
aspect_ratio: [比例]
generate_audio: true
prompt: [英文版 Prompt]

━━━━━━━━━━━━━━━━━━━━
📌 使用说明
━━━━━━━━━━━━━━━━━━━━
• 链接有效期：24小时，及时下载
• 建议先用 fast 模型测试
• Prompt 建议≤500中文字或1000英文词
• 音效默认开启，如需默片设 generate_audio: false
• API 文档：https://seedance2api.app
```

---

## Prompt 质量自检

```
✓ 主体明确（谁/什么）
✓ 场景/背景交代
✓ 动作/状态具体（"走" > "动"）
✓ 光线/色调说明
✓ 镜头类型描述（推/拉/移/跟/环绕）
✓ 无矛盾（不说"黑夜"又描述"阳光感"）
```

---

## 常见问题处理

| 需求 | 处理方式 |
|------|---------|
| 镜头不稳定 | 引导提供参考视频用 @video 参考镜头 |
| 首尾连贯 | 提供2张图，prompt 说明 "from [图1] to [图2]" |
| 视频延长 | 结尾加 "Extend @video1 by N seconds"，描述最后一帧状态 |
| 长镜头 | 结尾加 "No scene cuts throughout, one continuous shot" |
| 不要某元素 | prompt 加 "without [元素]" 或 "avoid [元素]" |
| 指定音效 | prompt 加 "Background BGM: [描述]" |

---

## 镜头描述速查

| 效果 | 写法 |
|------|------|
| 推近 | Camera pushes in / Camera zooms in |
| 拉远 | Camera pulls back |
| 横移 | Camera pans left/right |
| 跟拍 | Camera follows / Camera tracks |
| 环绕 | Camera circles around |
| 升降 | Camera rises/drops |
| 希区柯克 | Hitchcock zoom |
| 加速 | Speed accelerates like a roller coaster |

---

## 结尾必备

```
No scene cuts throughout, one continuous shot.
```
（确保生成连续镜头）

---

*此技能由 Anna 整理 · v1.0.1（纯提示词生成版）*
