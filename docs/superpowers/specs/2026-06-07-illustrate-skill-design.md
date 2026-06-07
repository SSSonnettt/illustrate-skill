# illustrate — 文章自动配图 Skill 设计文档

**日期**: 2026-06-07
**状态**: 设计完成，待实现
**类型**: Claude Code Skill

---

## 一、目标

为 AI 写作的文章自动配图。作者在 Markdown 中用简洁标记声明配图位置、类型和风格，触发 `/illustrate` 后自动生成图片、上传 CDN、回写 Markdown，产出可直接发布或分发的完整文章。

## 二、管线位置

```
AI 写作 → Markdown([img]标记) → /illustrate → Markdown(CDN图片) → [自由选择下一步]
```

`/illustrate` 的边界到**输出含真实图片 URL 的 Markdown 文件**为止。不捆绑分发或发布链路。

## 三、核心决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| **形态** | Claude Code Skill | 配图核心是语义理解→视觉翻译，Claude 天然擅长 |
| **交互模式** | 混合模式 | 描述充足→直出；描述模糊→先确认再生成 |
| **风格系统** | 类型×风格二维矩阵 | 类型(画什么结构)和风格(画成什么样子)独立定义，自由组合 |
| **占位符语法** | `[img: 场景, 类型, 风格]` 位置标签 | 简洁，两个维度可独立省略，Claude 自动补全 |
| **生图后端** | 硅基流动 API（SD 3.5 Medium/Flux/通义万相） | 性价比最高，国内快，兼容 OpenAI 格式 |
| **CDN** | Cloudflare R2 | 免费额度足，公网直链 |
| **API Key** | 用户本地 .env 维护 | 不进 Git，代码只读环境变量 |

## 四、Skill 内部流程

```
/illustrate 触发
    │
    ├─ Phase 1: 解析
    │   ├─ 扫描 Markdown 中所有 [img:...] 标记
    │   ├─ 读取 types.yml + styles.yml
    │   ├─ 提取每个标记前后段落的语境
    │   ├─ 补全缺失的类型/风格字段（Claude 根据上下文推断）
    │   ├─ 校验组合有效性（标记不推荐的组合并建议替代）
    │   └─ 判定完整度：详细→Phase2a / 模糊→Phase2b
    │
    ├─ Phase 2a: 直接生成（描述充足）
    │   ├─ 合并四源：type.prompt_hint + style.prompt_prefix + 场景描述 + 文章语境
    │   ├─ 生成精准英文 prompt
    │   ├─ 使用 style.model 调硅基流动 API 生图
    │   └─ 上传 Cloudflare R2 → 获得 CDN URL
    │
    ├─ Phase 2b: 确认后生成（描述模糊）
    │   ├─ 向用户展示推断的类型、风格和建议 prompt
    │   ├─ 用户确认或修改（可调整类型/风格/prompt）
    │   └─ 调 API → 上传 → 获得 URL
    │
    └─ Phase 3: 回写
        ├─ 用 CDN URL 替换原 [img] 标记
        ├─ 输出最终 Markdown ✅
        └─ 本次配图简要总结（N张图，总耗时）
```

## 五、文件结构

```
illustrate-skill/
├── SKILL.md                   # 核心：Skill 定义 + Claude 运行时指令
├── types.yml                  # 图片类型定义（scene/diagram/infographic/...）
├── styles.yml                 # 视觉风格定义（tech-3d/ink/film/...）
├── references/
│   ├── siliconflow.md         # 硅基流动 API 参考
│   ├── cloudflare-r2.md       # R2 存储桶配置和上传指南
│   └── style-guide.md         # 类型和风格定义指南
└── scripts/
    └── upload-r2.py           # R2 上传辅助脚本
```

## 六、类型 × 风格矩阵设计

### 类型定义（types.yml）

```yaml
# 每个类型定义"画什么结构"
scene:
  label: "氛围场景"
  prompt_hint: >
    A standalone visual scene that captures the mood of the text.
    No text or labels in the image. Evocative composition.
  best_styles: [tech-3d, ink, japanese-film, watercolor, editorial]

diagram:
  label: "架构/流程图"
  prompt_hint: >
    A structured technical diagram showing relationships or flows.
    Clean layout, clear hierarchy, logical grouping.
  best_styles: [tech-3d, blueprint, editorial]

infographic:
  label: "数据信息图"
  prompt_hint: >
    Data visualization with visual metaphors. Colorful, engaging,
    easy to understand at a glance.
  best_styles: [tech-3d, blueprint, watercolor, editorial]

comparison:
  label: "对比示意图"
  prompt_hint: >
    Side-by-side or split comparison showing differences between
    two concepts. Visual parallel structure.
  best_styles: [tech-3d, blueprint, editorial]

timeline:
  label: "时间线"
  prompt_hint: >
    Chronological visualization showing progression or evolution.
    Clear temporal flow with milestones.
  best_styles: [tech-3d, ink, blueprint, editorial]

cover:
  label: "封面图"
  prompt_hint: >
    A striking title image that summarizes the article theme.
    Bold composition, eye-catching, suitable as hero image.
  best_styles: [tech-3d, ink, japanese-film, watercolor, editorial]
```

### 风格定义（styles.yml）

```yaml
# 每个风格定义"画成什么样子"
tech-3d:
  label: "科技3D插画"
  model: SD35
  prompt_prefix: >
    Clean 3D isometric illustration, soft lighting, flat design,
    modern tech aesthetic, smooth gradients
  negative: "photorealistic, dark, cluttered, sketch, hand-drawn"
  steps: 28
  ratio: "16:9"

ink:
  label: "水墨画"
  model: Tongyi
  prompt_prefix: >
    Chinese ink wash painting, 水墨画, misty mountains, poetic
    composition, traditional aesthetic, brush strokes visible
  negative: "oil painting, 3D render, photographic, digital art"
  steps: 20
  ratio: "3:4"

japanese-film:
  label: "日系胶片"
  model: Flux
  prompt_prefix: >
    Japanese film photography, fujifilm simulation, soft grain,
    natural window light, muted colors, contemplative mood
  negative: "digital art, 3D render, oversaturated, HDR"
  steps: 30
  ratio: "16:9"

blueprint:
  label: "蓝图线稿"
  model: SD35
  prompt_prefix: >
    Blueprint style technical drawing, white lines on dark blue
    background, architectural sketch aesthetic, precise linework
  negative: "colorful, photorealistic, organic shapes"
  steps: 25
  ratio: "16:9"

watercolor:
  label: "水彩手绘"
  model: SD35
  prompt_prefix: >
    Watercolor painting style, soft color washes, artistic
    illustration, hand-painted feel, gentle texture
  negative: "digital art, 3D render, sharp lines, photorealistic"
  steps: 25
  ratio: "16:9"

editorial:
  label: "杂志插画"
  model: Flux
  prompt_prefix: >
    Editorial illustration style, sophisticated composition,
    bold graphic elements, contemporary magazine aesthetic
  negative: "photorealistic, cartoon, childish"
  steps: 30
  ratio: "16:9"
```

### 组合矩阵

| | tech-3d | ink | film | blueprint | watercolor | editorial |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **scene** | ✅经典 | ✅ | ✅ | — | ✅ | ✅ |
| **diagram** | ✅经典 | — | — | ✅经典 | — | ✅ |
| **infographic** | ✅ | — | — | ✅ | ✅ | ✅经典 |
| **comparison** | ✅ | — | — | ✅ | — | ✅ |
| **timeline** | ✅ | ✅ | — | ✅经典 | — | ✅ |
| **cover** | ✅ | ✅ | ✅经典 | — | ✅ | ✅ |

`✅经典` = 此组合效果优秀，Claude 优先推荐。`—` = 不推荐的组合。

## 七、占位符语法

### 基本格式

```
[img: 场景描述, 类型, 风格]
```

类型和风格是位置参数，可独立省略：

| 写法 | 效果 |
|------|------|
| `[img: 描述, diagram, tech-3d]` | 完整指定，直接生成 |
| `[img: 描述, , tech-3d]` | 只指定风格，Claude 推断类型 |
| `[img: 描述, diagram]` | 只指定类型，Claude 推断风格 |
| `[img: 描述]` | 全部推断，根据全文语境自动匹配 |

### 实际使用示例

```markdown
调试生产环境问题时，需要一层层剥开问题的表象...

[img: 洋葱被层层剥开的剖面结构图, diagram, tech-3d]

这种调试方法论的核心在于：永远不要相信表面的错误信息。
诊断线上故障就像剥洋葱——你永远不知道下一层是解决问题还是让你流泪。

[img: 一位工程师在深夜的屏幕前沉思, scene, japanese-film]

应对这种困境，我总结了三层递进的排查策略...
```

## 八、Prompt 组合逻辑

Claude 将以下四个信息源合并为最终 API prompt：

```
type.prompt_hint    →  "A structured diagram showing relationships..."
    +
style.prompt_prefix →  "Clean 3D isometric illustration, soft lighting..."
    +
[img]场景描述       →  "微服务架构的请求链路图"
    +
文章前后段落语境    →  "这篇文章在讨论后端架构优化..."
    =
最终 API Prompt     →  "A structured diagram of a microservice request chain,
                        showing API gateway, service mesh, and backend services.
                        Clean 3D isometric illustration, soft lighting, flat design..."
```

## 九、环境变量

```
SILICONFLOW_API_KEY=sk-xxx        # 硅基流动 API Key
R2_ACCOUNT_ID=xxx                 # Cloudflare Account ID
R2_ACCESS_KEY_ID=xxx              # R2 Access Key
R2_SECRET_ACCESS_KEY=xxx          # R2 Secret Key
R2_BUCKET_NAME=illustrate-images  # R2 存储桶名称
R2_PUBLIC_URL=https://cdn.xxx.com # CDN 公开域名
```

---

## 十、非目标（YAGNI）

- 不内置图片编辑/裁剪功能
- 不提供前端管理界面
- 不支持视频/GIF 生成
- 不做图片审核/敏感内容过滤（由硅基流动 API 侧处理）
- 不与任何特定发布平台耦合
