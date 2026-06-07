# illustrate-skill 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个 Claude Code Skill `/illustrate`，从 Markdown 文章中的 `[img]` 占位符自动生成配图并上传到 Cloudflare R2 CDN。

**Architecture:** 纯 Claude Code Skill 项目——SKILL.md 是核心运行时指令，types.yml/styles.yml 定义类型×风格二维矩阵，references/ 提供平台 API 参考，scripts/ 提供 R2 上传辅助脚本。无前端、无数据库、无独立服务。

**Tech Stack:** Claude Code Skill 规范（SKILL.md frontmatter + 正文）、YAML 配置、Python 3（辅助脚本）、硅基流动 API、Cloudflare R2 S3 API。

**设计文档:** `docs/superpowers/specs/2026-06-07-illustrate-skill-design.md`

---

## 文件结构映射

```
illustrate-skill/
├── SKILL.md                   # Task 7: 核心 Skill 指令
├── types.yml                  # Task 2: 类型定义
├── styles.yml                 # Task 3: 风格定义
├── references/
│   ├── siliconflow.md         # Task 4: 硅基流动 API 参考
│   ├── cloudflare-r2.md       # Task 5: R2 配置和上传指南
│   └── style-guide.md         # Task 6: 风格定义指南
└── scripts/
    └── upload-r2.py           # Task 8: R2 上传脚本
```

---

### Task 1: 创建项目骨架

**Files:**
- Create: `illustrate-skill/.gitignore`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p /Users/wuji/workspace/illustrate-skill/references
mkdir -p /Users/wuji/workspace/illustrate-skill/scripts
```

- [ ] **Step 2: 创建 .gitignore**

```gitignore
# .env
.env

# Python
__pycache__/
*.pyc
.venv/

# IDE
.idea/
.vscode/

# Superpowers
.superpowers/
```

- [ ] **Step 3: 初始化 Git 仓库并提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git init && git add -A && git commit -m "chore: init illustrate-skill project skeleton"
```

---

### Task 2: 创建 types.yml — 图片类型定义

**Files:**
- Create: `illustrate-skill/types.yml`

- [ ] **Step 1: 写入 types.yml 完整内容**

```yaml
# types.yml — 图片类型定义（"画什么结构"）
# 每个类型定义 prompt_hint 和推荐风格组合

scene:
  label: "氛围场景"
  prompt_hint: >
    A standalone visual scene that captures the mood of the text.
    No text or labels in the image. Evocative composition,
    atmospheric lighting, immersive setting.
  best_styles: [tech-3d, ink, japanese-film, watercolor, editorial]

diagram:
  label: "架构/流程图"
  prompt_hint: >
    A structured technical diagram showing relationships, flows,
    or system architecture. Clean layout, clear hierarchy, logical
    grouping of components. White or light background preferred.
  best_styles: [tech-3d, blueprint, editorial]

infographic:
  label: "数据信息图"
  prompt_hint: >
    Data visualization with visual metaphors and comparisons.
    Colorful and engaging, easy to understand at a glance.
    Numbers and proportions shown visually.
  best_styles: [tech-3d, blueprint, watercolor, editorial]

comparison:
  label: "对比示意图"
  prompt_hint: >
    Side-by-side or split comparison showing differences between
    two or more concepts, approaches, or options. Visual parallel
    structure, clear differentiation between sides.
  best_styles: [tech-3d, blueprint, editorial]

timeline:
  label: "时间线"
  prompt_hint: >
    Chronological visualization showing progression, evolution,
    or historical sequence. Clear temporal flow with distinct
    milestones or phases labeled.
  best_styles: [tech-3d, ink, blueprint, editorial]

cover:
  label: "封面图"
  prompt_hint: >
    A striking hero/title image that captures the essence of
    the entire article. Bold composition, eye-catching, suitable
    as a social media preview card. May include the article title
    area but text should be minimal.
  best_styles: [tech-3d, ink, japanese-film, watercolor, editorial]
```

- [ ] **Step 2: 提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git add types.yml && git commit -m "feat: add image type definitions (types.yml)"
```

---

### Task 3: 创建 styles.yml — 视觉风格定义

**Files:**
- Create: `illustrate-skill/styles.yml`

- [ ] **Step 1: 写入 styles.yml 完整内容**

```yaml
# styles.yml — 视觉风格定义（"画成什么样子"）
# 每个风格包含模型配置、prompt 前缀、参数

tech-3d:
  label: "科技3D插画"
  model: SD35
  prompt_prefix: >
    Clean 3D isometric illustration style, soft lighting, flat
    design, modern tech aesthetic, smooth gradients, vibrant but
    not oversaturated colors, rounded geometry
  negative: "photorealistic, dark and moody, cluttered composition, sketch lines, hand-drawn, messy"
  steps: 28
  ratio: "16:9"

ink:
  label: "水墨画"
  model: Tongyi
  prompt_prefix: >
    Chinese ink wash painting style (水墨画), misty atmosphere,
    poetic composition, traditional aesthetic, visible brush
    strokes, negative space, monochrome with subtle color accents
  negative: "oil painting, 3D render, photographic, digital art, oversaturated, western painting style"
  steps: 20
  ratio: "3:4"

japanese-film:
  label: "日系胶片"
  model: Flux
  prompt_prefix: >
    Japanese film photography style, fujifilm simulation, soft
    organic grain, natural window light, muted pastel colors,
    contemplative mood, shallow depth of field
  negative: "digital art, 3D render, oversaturated, HDR, harsh lighting, artificial, cartoon"
  steps: 30
  ratio: "16:9"

blueprint:
  label: "蓝图线稿"
  model: SD35
  prompt_prefix: >
    Blueprint style technical drawing, white lines and annotations
    on dark blue background, architectural sketch aesthetic,
    precise linework, grid overlay, measurement marks
  negative: "colorful, photorealistic, organic shapes, hand-drawn rough sketch, messy"
  steps: 25
  ratio: "16:9"

watercolor:
  label: "水彩手绘"
  model: SD35
  prompt_prefix: >
    Watercolor painting style, soft color washes bleeding into
    each other, artistic illustration, hand-painted feel, gentle
    paper texture visible
  negative: "digital art, 3D render, sharp precise lines, photorealistic, vector graphics"
  steps: 25
  ratio: "16:9"

editorial:
  label: "杂志插画"
  model: Flux
  prompt_prefix: >
    Editorial illustration style, sophisticated composition, bold
    graphic elements, contemporary magazine aesthetic, conceptual
    visual metaphor, clean and striking
  negative: "photorealistic, cartoon style, childish, cluttered, amateur"
  steps: 30
  ratio: "16:9"
```

- [ ] **Step 2: 提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git add styles.yml && git commit -m "feat: add visual style definitions (styles.yml)"
```

---

### Task 4: 创建 references/siliconflow.md — 硅基流动 API 参考

**Files:**
- Create: `illustrate-skill/references/siliconflow.md`

- [ ] **Step 1: 写入 siliconflow.md**

写入 `illustrate-skill/references/siliconflow.md`，内容：

```markdown
# 硅基流动 (SiliconFlow) API 参考

## 获取 API Key

1. 访问 [siliconflow.cn](https://siliconflow.cn) 注册账号
2. 进入控制台 → API Key → 创建新 Key
3. 将 Key 写入 `~/.bashrc` 或项目 `.env`：

```bash
export SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## 可用模型

| 模型 ID | 说明 | 分辨率 | 每张参考价 |
|---------|------|--------|:--:|
| `stabilityai/stable-diffusion-3-5-medium` | SD 3.5 Medium，通用场景 | 1024×1024 | ¥0.15 |
| `stabilityai/stable-diffusion-3-5-large` | SD 3.5 Large，高质量 | 1024×1024 | ¥0.25 |
| `black-forest-labs/flux-1-dev` | Flux Dev，极致质量 | 1024×1024 | ¥0.30 |
| `black-forest-labs/flux-1-schnell` | Flux Schnell，快速 | 1024×1024 | ¥0.20 |
| `stabilityai/stable-diffusion-xl-base-1.0` | SDXL，生态成熟 | 1024×1024 | ¥0.12 |

## 生成图片 API

兼容 OpenAI Images API 格式。

### 请求

```python
import requests

resp = requests.post(
    "https://api.siliconflow.cn/v1/images/generations",
    headers={
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "stabilityai/stable-diffusion-3-5-medium",
        "prompt": "Clean 3D isometric illustration of...",
        "negative_prompt": "photorealistic, dark, cluttered",
        "n": 1,
        "size": "1024x1024"
    },
    timeout=120
)

result = resp.json()
# {"data": [{"url": "https://...", "b64_json": "..."}]}
```

### 响应处理

```python
import base64

data = result["data"][0]

# 方式一：从 URL 下载（URL 有效期有限，建议立即下载）
if data.get("url"):
    img_resp = requests.get(data["url"])
    image_bytes = img_resp.content

# 方式二：从 base64 解码
if data.get("b64_json"):
    image_bytes = base64.b64decode(data["b64_json"])
```

### 错误处理

```python
if resp.status_code != 200:
    error = resp.json()
    # {"error": {"message": "...", "code": "..."}}
    print(f"Error {resp.status_code}: {error}")
```

## 在 SKILL.md 中的模型选择规则

Claude 执行 `/illustrate` 时，根据 styles.yml 中的 `model` 字段选择对应模型 ID：

| styles.yml model | 硅基流动 model ID |
|:--|:--|
| SD35 | `stabilityai/stable-diffusion-3-5-medium` |
| SD35-L | `stabilityai/stable-diffusion-3-5-large` |
| SDXL | `stabilityai/stable-diffusion-xl-base-1.0` |
| Flux | `black-forest-labs/flux-1-dev` |
| Flux-Fast | `black-forest-labs/flux-1-schnell` |
| Tongyi | `alibaba/tongyi-wanxiang-v1` |

## 最佳实践

1. **prompt 用英文**：硅基流动的 SD/Flux 模型对英文 prompt 响应最好
2. **negative prompt 精简**：5-8 个关键词即可，太长反而降低效果
3. **steps 20-30**：低于 20 质量下降明显，高于 30 收益递减
4. **超时设 120s**：SD 3.5 通常 15-30s，Flux 可能 60-90s
```

- [ ] **Step 2: 提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git add references/siliconflow.md && git commit -m "feat: add SiliconFlow API reference"
```

---

### Task 5: 创建 references/cloudflare-r2.md — R2 配置指南

**Files:**
- Create: `illustrate-skill/references/cloudflare-r2.md`

- [ ] **Step 1: 写入 cloudflare-r2.md**

写入 `illustrate-skill/references/cloudflare-r2.md`，内容：

```markdown
# Cloudflare R2 配置和上传指南

## 为什么选 R2

- **零出站流量费**：Cloudflare R2 不收取出站带宽费（与 S3 最大区别）
- **10GB 免费存储**：个人博客配图绰绰有余
- **公网直链**：文件直接通过 `https://cdn.yourdomain.com/file.jpg` 访问
- **S3 兼容 API**：任何 S3 SDK 都能直接用

## 初始化流程

### 1. 创建 R2 存储桶

```bash
# 通过 Cloudflare Dashboard → R2 → Create bucket
# 名称：illustrate-images
# 位置：选择最近的区域（APAC）
```

### 2. 配置公开访问

在存储桶 Settings → Public Access：
- 启用 "R2.dev subdomain"（获得 `https://pub-xxx.r2.dev` 格式的公开 URL）
- 或绑定自定义域名（推荐）：在存储桶 Settings → Custom Domains 中绑定 `cdn.yourdomain.com`

### 3. 创建 API Token

R2 → Manage R2 API Tokens → Create API Token：
- 权限：`Object Read & Write`
- 范围：指定到 `illustrate-images` 存储桶
- 记录生成的 Access Key ID 和 Secret Access Key

### 4. 配置环境变量

```bash
export R2_ACCOUNT_ID="your-cloudflare-account-id"
export R2_ACCESS_KEY_ID="your-access-key-id"
export R2_SECRET_ACCESS_KEY="your-secret-access-key"
export R2_BUCKET_NAME="illustrate-images"
export R2_PUBLIC_URL="https://pub-xxx.r2.dev"  # 或自定义域名
```

Cloudflare Account ID 从 Dashboard 首页 URL 获取：`https://dash.cloudflare.com/<account-id>`

## 上传文件

使用 `scripts/upload-r2.py` 或直接调 S3 API：

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4"),
)

# 上传
key = f"illustrations/2026/06/07/abc123.png"
s3.put_object(
    Bucket=R2_BUCKET_NAME,
    Key=key,
    Body=image_bytes,
    ContentType="image/png",
)

# 拼接公开 URL
public_url = f"{R2_PUBLIC_URL}/{key}"
# 或自定义域名: f"https://cdn.yourdomain.com/{key}"
```

## 文件命名规范

```
illustrations/{YYYY}/{MM}/{DD}/{uuid}.png
```

- 按日期分目录，方便管理
- UUID（前8位即可）保证文件名唯一
- 扩展名根据实际格式：.png / .jpg / .webp

## 关于跨域（CORS）

如果图片需要在前端 Canvas 中操作，需配置 CORS：

在 R2 存储桶 Settings → CORS Policy 中添加：

```json
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

仅作直链引用（`![]()` 或 `<img>`）则无需配置 CORS。
```

- [ ] **Step 2: 提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git add references/cloudflare-r2.md && git commit -m "feat: add Cloudflare R2 setup guide"
```

---

### Task 6: 创建 references/style-guide.md — 风格定义指南

**Files:**
- Create: `illustrate-skill/references/style-guide.md`

- [ ] **Step 1: 写入 style-guide.md**

写入 `illustrate-skill/references/style-guide.md`，内容：

```markdown
# 风格定义指南

## 设计哲学

`types.yml` 和 `styles.yml` 分离的核心理念：

- **类型（Type）** = 画什么结构：信息图？场景图？流程图？
- **风格（Style）** = 画成什么样子：水墨？3D？胶片？

两者独立定义、自由组合。你新增一个风格时，它自动与所有兼容类型组合生效。

## 如何新增一个风格

### 1. 在 styles.yml 添加条目

```yaml
my-style:
  label: "我的风格"           # 中文名，Claude 确认时会展示
  model: SD35                 # 模型: SD35 / SDXL / Flux / Tongyi
  prompt_prefix: >            # 风格描述（英文），拼接在场景描述之前
    A concise yet specific description of the visual style,
    including color palette, lighting, texture, and overall feel.
  negative: "list of things to avoid, comma separated"
  steps: 25                   # 采样步数 (15-35)，越高质量越好但越慢
  ratio: "16:9"               # 默认宽高比: "16:9" / "3:4" / "1:1"
```

### 2. 在 types.yml 的 best_styles 中注册

找到与新风格兼容的类型，将 `my-style` 加入其 `best_styles` 列表。不在列表中的组合 Claude 会避开。

```yaml
scene:
  best_styles: [tech-3d, ink, japanese-film, watercolor, editorial, my-style]  # 添加
```

### 3. 风格设计原则

**prompt_prefix 写法指南：**

- ✅ 用英文写，SD/Flux 对英文 prompt 响应最好
- ✅ 描述视觉特征：颜色、光线、材质、构图
- ✅ 3-5 句足够，不需要长篇大论
- ✅ 用形容词群描述风格方向："soft, dreamy, warm"
- ❌ 不要在 prompt_prefix 中写具体内容（具体内容来自场景描述）
- ❌ 不要用"beautiful"、"amazing"等空洞形容词（AI 忽略它们）

### 4. 模型选择建议

| 模型 | 适合风格 | 不适合 |
|------|---------|--------|
| SD35 (SD 3.5 Medium) | 插画、图表、通用 | 极致写实 |
| SDXL | 写实、成熟生态 | 文字渲染 |
| Flux | 照片级写实、文字渲染 | 预算敏感 |
| Tongyi | 国风、水墨、亚洲审美 | 西方风格 |
```

- [ ] **Step 2: 提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git add references/style-guide.md && git commit -m "feat: add style creation guide"
```

---

### Task 7: 创建 scripts/upload-r2.py — R2 上传辅助脚本

**Files:**
- Create: `illustrate-skill/scripts/upload-r2.py`

- [ ] **Step 1: 写入 upload-r2.py**

写入 `illustrate-skill/scripts/upload-r2.py`，内容：

```python
#!/usr/bin/env python3
"""Upload image bytes to Cloudflare R2 and return public URL.

Usage:
    python3 upload-r2.py <image_path>        # 上传文件，输出 URL
    python3 upload-r2.py - <url>             # 从 stdin 读取（暂未实现）

Environment variables:
    R2_ACCOUNT_ID         Cloudflare Account ID
    R2_ACCESS_KEY_ID      R2 API Token Access Key
    R2_SECRET_ACCESS_KEY  R2 API Token Secret
    R2_BUCKET_NAME        R2 bucket name (default: illustrate-images)
    R2_PUBLIC_URL         Public-facing URL prefix (e.g. https://cdn.example.com)
"""

import os
import sys
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

import boto3
from botocore.config import Config


def get_env(key: str) -> str:
    value = os.environ.get(key, "")
    if not value:
        print(f"Error: ${key} is not set", file=sys.stderr)
        sys.exit(1)
    return value


def content_type_from_path(path: str) -> str:
    ext = Path(path).suffix.lower()
    mapping = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    return mapping.get(ext, "image/png")


def generate_key(path: str) -> str:
    """Generate R2 object key with date-based prefix and content hash."""
    now = datetime.now()
    date_prefix = now.strftime("illustrations/%Y/%m/%d")

    # Use file content hash for dedup + short uuid for uniqueness
    with open(path, "rb") as f:
        content_hash = hashlib.md5(f.read()).hexdigest()[:8]

    short_id = str(uuid.uuid4())[:8]
    ext = Path(path).suffix or ".png"
    filename = f"{content_hash}-{short_id}{ext}"

    return f"{date_prefix}/{filename}"


def upload(path: str) -> str:
    """Upload file to R2 and return public URL."""
    account_id = get_env("R2_ACCOUNT_ID")
    access_key = get_env("R2_ACCESS_KEY_ID")
    secret_key = get_env("R2_SECRET_ACCESS_KEY")
    bucket = os.environ.get("R2_BUCKET_NAME", "illustrate-images")
    public_url = get_env("R2_PUBLIC_URL")

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
    )

    key = generate_key(path)
    content_type = content_type_from_path(path)

    with open(path, "rb") as f:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=f.read(),
            ContentType=content_type,
        )

    url = f"{public_url.rstrip('/')}/{key}"
    return url


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    url = upload(path)
    print(url)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 验证脚本语法**

```bash
python3 -c "import ast; ast.parse(open('/Users/wuji/workspace/illustrate-skill/scripts/upload-r2.py').read()); print('Syntax OK')"
```

- [ ] **Step 3: 提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git add scripts/upload-r2.py && git commit -m "feat: add R2 upload helper script"
```

---

### Task 8: 创建 SKILL.md — 核心 Skill 定义

**Files:**
- Create: `illustrate-skill/SKILL.md`

- [ ] **Step 1: 写入 SKILL.md**

写入 `illustrate-skill/SKILL.md`，内容：

```markdown
---
name: illustrate
description: >-
  Use when user asks to generate or add illustrations, images, or cover art to an article,
  post, or Markdown document. Triggers on "配图", "生成图片", "加张图", "配个图",
  "illustrate", "插图", "封面图", "add image". Works with [img] placeholders in Markdown.
license: MIT
compatibility: >-
  Requires Python 3.9+ with boto3 for R2 upload. Requires SILICONFLOW_API_KEY,
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME,
  R2_PUBLIC_URL environment variables.
metadata:
  author: wuji
  version: "1.0.0"
  category: content-creation
  models: sd35,sdxl,flux,tongyi
  cdn: cloudflare-r2
---

# illustrate — 文章自动配图

根据文章的 `[img]` 占位符自动生成配图：分析语境 → 生成 prompt → 调 API 出图 → 上传 CDN → 回写 Markdown。

**适用**：Markdown 文章中已有 `[img:...]` 标记，需要自动生成配图。
**不适用**：文章还没有写、需要设计图片内容（而非 AI 生成）、需要视频/GIF。

## 核心理念

- **混合模式**：`[img]` 描述足够详细→直接生成；描述模糊→先和用户确认再生成
- **类型×风格矩阵**：类型（画什么结构）和风格（画成什么样子）分离定义，自由组合
- **Markdown 进出**：输入是含 `[img]` 的 Markdown，输出是含 CDN URL 的 Markdown
- **不做分发**：边界到输出 Markdown 为止，后续发布由其他 Skill/工具处理

## 运行时依赖

- **环境变量**：`SILICONFLOW_API_KEY`、`R2_ACCOUNT_ID`、`R2_ACCESS_KEY_ID`、`R2_SECRET_ACCESS_KEY`、`R2_BUCKET_NAME`、`R2_PUBLIC_URL`
- **Python 脚本**：`scripts/upload-r2.py`（需 `boto3`：`pip install boto3`）
- **配置文件**：`types.yml`、`styles.yml`（Skill 同级目录）

## 工作流

严格按 Parse → Generate → Upload → Writeback 顺序。

### Step 1: Parse — 扫描占位符，分析语境

1. **定位 Markdown 文件**：用户指定路径 > 搜索当前目录 `.md` 文件 > 询问用户
2. **扫描 `[img:...]` 标记**：正则 `\[img:\s*([^\]]+)\]`
3. **加载配置文件**：读取 `types.yml` 和 `styles.yml`
4. **解析每个标记**：

```
[img: 场景描述, 类型?, 风格?]
      ←──────────→  ←──→  ←──→
          主体        位置1  位置2
```

   - **主体（必填）**：场景描述，自然语言
   - **位置1**：如果在 types.yml 中匹配到 → 是类型；如果在 styles.yml 中匹配到 → 是风格；都不匹配 → 当作描述的一部分
   - **位置2**：同理推断
   - 两个都缺失 → Claude 根据文章全文语境自动推荐类型和风格

5. **提取上下文**：每个标记前后各一段落（约 200 字），作为语境
6. **展示解析结果**：

```
检测到 3 个配图标记：

1. [img: 微服务请求链路图, diagram, tech-3d]
   → 描述充足，直接生成 ✅
   → 类型: 架构/流程图 · 风格: 科技3D插画 · 模型: SD35

2. [img: 深夜调试, scene]
   → 缺少风格，Claude 推荐: japanese-film（匹配你文章的散文语气）
   → 等到你确认

3. [img: 数据库索引结构]
   → 缺少类型和风格，Claude 推荐: diagram + tech-3d
   → 等到你确认
```

7. **模糊标记确认**：逐个向用户展示推荐 → 用户确认/修改 → 进入生成

### Step 2: Generate — 生成 prompt，调用 API

1. **Prompt 组合**（四源合并）：

```
types.yml → type.prompt_hint     "A structured diagram showing..."
    +
styles.yml → style.prompt_prefix "Clean 3D isometric illustration..."
    +
[img] 主体 → 场景描述           "微服务请求链路图"
    +
文章语境 → 前后段落             "文章讨论后端架构优化..."
    =
最终英文 prompt
```

2. **模型选择**：根据 styles.yml 中的 `model` 字段映射到硅基流动 model ID（参考 `references/siliconflow.md`）
3. **调用 API**：

```python
import os, requests, base64

resp = requests.post(
    "https://api.siliconflow.cn/v1/images/generations",
    headers={"Authorization": f"Bearer {os.environ['SILICONFLOW_API_KEY']}"},
    json={
        "model": model_id,          # 从 styles.yml 映射
        "prompt": final_prompt,     # 四源合并的英文 prompt
        "negative_prompt": negative, # 从 styles.yml
        "n": 1,
        "size": size_from_ratio     # 从 styles.yml ratio 转换
    },
    timeout=120
)
data = resp.json()["data"][0]
image_bytes = base64.b64decode(data["b64_json"])
```

4. **保存临时文件**：`/tmp/illustrate-{uuid}.png`

### Step 3: Upload — 上传到 Cloudflare R2

1. **调用上传脚本**：

```bash
python3 scripts/upload-r2.py /tmp/illustrate-{uuid}.png
# 输出: https://cdn.example.com/illustrations/2026/06/07/abc123def-456.png
```

2. **如脚本不可用**（缺少 boto3 等），直接用 Python 调 S3 API（参考 `references/cloudflare-r2.md`）
3. **清理临时文件**：`rm /tmp/illustrate-{uuid}.png`

### Step 4: Writeback — 回写 Markdown

1. **替换占位符**：

```
[img: 微服务请求链路图, diagram, tech-3d]
  → ![微服务请求链路图](https://cdn.example.com/illustrations/2026/06/07/abc.png)
```

2. **展示结果**：

```
✅ 配图完成（3/3）

1. 微服务请求链路图 → ![ ](https://cdn.xxx.com/abc.png)
2. 深夜调试场景     → ![ ](https://cdn.xxx.com/def.png)
3. 数据库索引结构   → ![ ](https://cdn.xxx.com/ghi.png)

Markdown 已更新，可直接分发或发布。
```

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 缺少环境变量 | 提示用户设置，给出具体变量名和获取方式 |
| API 返回错误 | 重试一次（间隔 3s），仍失败则跳过该图并告知用户 |
| R2 上传失败 | 检查 boto3 是否安装、凭证是否正确，给出诊断 |
| types.yml/styles.yml 不存在 | 使用内置默认值（tech-3d + scene） |
| [img] 标记语法错误 | 展示原文，请用户修正 |

## 性能说明

- 每张图 API 调用约 15-60 秒（SD 3.5 Medium 约 15s，Flux 约 60s）
- 多张图可并行调用
- 成本约 ¥0.12-0.30/张（取决于模型选择）
- R2 存储免费额度 10GB，配图场景几乎不会超额
```

- [ ] **Step 2: 验证 SKILL.md 格式**

检查 frontmatter 字段是否符合 Agent Skills 规范：
- `name`: `illustrate` ✅（小写字母，无连字符开头/结尾）
- `description`: 含触发关键词 ✅
- `license`: SPDX 标识符 ✅
- `compatibility`: 运行时依赖说明 ✅
- `metadata`: 仅 key-value ✅

- [ ] **Step 3: 提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git add SKILL.md && git commit -m "feat: add core SKILL.md definition"
```

---

### Task 9: 最终验证和收尾

**Files:**
- Create: `illustrate-skill/README.md`

- [ ] **Step 1: 创建 README.md**

写入 `illustrate-skill/README.md`，内容：

```markdown
# illustrate — 文章自动配图

Claude Code Skill。在 Markdown 中用 `[img: 场景, 类型, 风格]` 标记配图位置，`/illustrate` 自动生成图片并上传到 Cloudflare R2 CDN。

## 安装

```bash
# 方式一：skills.sh 安装（推荐）
npx skills add wuji/illustrate-skill

# 方式二：本地开发安装
# 将仓库克隆到 ~/.claude/skills/illustrate-skill/
```

## 快速开始

1. **配置环境变量**（`~/.bashrc` 或 `.env`）：

```bash
export SILICONFLOW_API_KEY=sk-xxx
export R2_ACCOUNT_ID=xxx
export R2_ACCESS_KEY_ID=xxx
export R2_SECRET_ACCESS_KEY=xxx
export R2_BUCKET_NAME=illustrate-images
export R2_PUBLIC_URL=https://cdn.yourdomain.com
```

2. **在文章中标记配图位置**：

```markdown
调试生产问题时，需要一层层剥开问题的表象...

[img: 洋葱被层层剥开的剖面结构图, diagram, tech-3d]

这种调试方法论的核心在于...
```

3. **触发配图**：

```
/illustrate
```

## 类型和风格

### 6 种类型

| 类型 | 说明 |
|------|------|
| `scene` | 氛围场景图 |
| `diagram` | 架构/流程图 |
| `infographic` | 数据信息图 |
| `comparison` | 对比示意图 |
| `timeline` | 时间线 |
| `cover` | 封面图 |

### 6 种风格

| 风格 | 说明 | 模型 |
|------|------|------|
| `tech-3d` | 科技3D插画 | SD 3.5 |
| `ink` | 水墨画 | 通义万相 |
| `japanese-film` | 日系胶片 | Flux |
| `blueprint` | 蓝图线稿 | SD 3.5 |
| `watercolor` | 水彩手绘 | SD 3.5 |
| `editorial` | 杂志插画 | Flux |

### 自定义

编辑 `types.yml` 和 `styles.yml` 添加你自己的类型和风格。详见 `references/style-guide.md`。

## 依赖

- Python 3.9+
- `boto3`：`pip install boto3`
- 硅基流动 API Key
- Cloudflare R2 存储桶

## 许可证

MIT
```

- [ ] **Step 2: 浏览完整文件结构，确认无遗漏**

```bash
find /Users/wuji/workspace/illustrate-skill -type f | sort
```

预期输出：
```
illustrate-skill/.gitignore
illustrate-skill/README.md
illustrate-skill/SKILL.md
illustrate-skill/types.yml
illustrate-skill/styles.yml
illustrate-skill/references/siliconflow.md
illustrate-skill/references/cloudflare-r2.md
illustrate-skill/references/style-guide.md
illustrate-skill/scripts/upload-r2.py
```

- [ ] **Step 3: 最终提交**

```bash
cd /Users/wuji/workspace/illustrate-skill && git add -A && git commit -m "feat: complete illustrate-skill v1.0.0"
```
