---
name: illustrate
description: >-
  Use when the user wants to add AI-generated images to a Markdown article — 配图、插图、
  生成图片、封面图、illustrate. The article should contain [img] placeholder markers;
  if it doesn't, help the user insert them first.
license: MIT
compatibility: >-
  Requires Python 3.9+ with boto3 for R2 upload. Requires SILICONFLOW_API_KEY,
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME,
  R2_PUBLIC_URL environment variables.
metadata:
  author: wuji
  version: "1.1.0"
  category: content-creation
  models: sd35,sdxl,flux,tongyi
  cdn: cloudflare-r2
---

# illustrate — 文章自动配图

根据文章的 `[img]` 占位符自动生成配图，上传到 Cloudflare R2 CDN，回写 Markdown。

**核心理念**：类型（画什么结构）× 风格（画成什么样子）二维矩阵，混合模式交互。

**铁律（宪法级规则）**

以下规则在用户请求"配图"这件事时**自动生效**。不可跳过，不可绕过。

**确认铁律**：`[img]` 标记描述不完整时，必须向用户展示推断结果和建议 prompt，等待用户明确确认后才能生成。**禁止擅自脑补 prompt 后直接生成。** 即使用户说"直接帮我配图""你看着办""我相信你的判断"，模糊标记仍需确认。

**环境检查铁律**：在解析任何 [img] 标记之前，必须先检查 6 个环境变量。缺少任何一个 → 立即停止，列出缺失项并告诉用户获取方式。不得先扫描标记再回头检查环境。

---

## 快速参考

| 用户说 | 你做什么 |
|--------|---------|
| `/illustrate`，文章有 `[img]` | Step 0 环境检查 → Step 1 解析 → Step 2 生成 → Step 3 上传 → Step 4 回写 |
| `/illustrate`，文章没有 `[img]` | 教用户标记语法，等用户添加后再触发生成 |
| `[img: 场景, diagram, tech-3d]` | 类型和风格都匹配到 → 可直出，展示 prompt 摘要后生成 |
| `[img: 场景]` 仅主体 | 缺类型/风格 → 从全文语境推断 → **必须先确认** |
| `[img: 场景, 赛博朋克]` 未匹配 | "赛博朋克"不在 styles.yml → 列出可用风格供选择 |
| 加新风格 | 编辑 `references/styles.yml` + `references/types.yml` |
| API 调用失败 | 重试一次（间隔 3s），仍失败则跳过该图 |
| 想改某张图的 prompt | 确认阶段直接修改，Claude 使用修改后的版本 |

---

## 何时适用 / 不适用

**适用**：文章已写完、Markdown 中已有 `[img:...]` 标记、需要配图后发布。
**不适用**：文章还没写、需要自己设计图片内容（非 AI 生成）、视频/GIF、文章没有任何配图标记且用户拒绝添加。

---

## 工作流

严格按 Step 0 → Step 1 → Step 2 → Step 3 → Step 4 顺序。**不可跳步。**

### Step 0: 环境检查（必须先执行）

在接触任何文章内容之前——

```python
import os

REQUIRED_VARS = {
    "SILICONFLOW_API_KEY": "硅基流动 → https://siliconflow.cn → 控制台 → API Key",
    "R2_ACCOUNT_ID":       "Cloudflare Dashboard 首页 URL 中的 account-id",
    "R2_ACCESS_KEY_ID":    "Cloudflare → R2 → Manage API Tokens → 创建 Token",
    "R2_SECRET_ACCESS_KEY":"同上，创建 Token 时生成",
    "R2_BUCKET_NAME":      "Cloudflare → R2 → 存储桶名称（如 illustrate-images）",
    "R2_PUBLIC_URL":       "R2 存储桶 → Settings → Public Access → r2.dev 子域名或自定义域名",
}

missing = [f"{k} — {v}" for k, v in REQUIRED_VARS.items() if not os.environ.get(k)]
if missing:
    # 立即停止，列出缺失项，不可继续
    print("缺少以下环境变量，请配置后重试：")
    for m in missing:
        print(f"  • {m}")
    # 回到等待用户输入状态
```

**全部就绪后才进入 Step 1。**

### Step 1: Parse — 扫描标记，分析语境

1. **定位 Markdown 文件**：用户指定路径 > 搜索当前目录 `.md` > 询问用户
2. **扫描 `[img:...]` 标记**：

```python
import re
pattern = r'\[img:\s*([^\]]+)\]'
markers = [(m.group(0), m.group(1)) for m in re.finditer(pattern, text)]
```

3. **加载配置文件**：读取 `references/types.yml` 和 `references/styles.yml`。不存在则用内置默认值。

4. **结构化解析每个标记**（这是核心——不能当自然语言随意理解）：

```
输入:  "[img: 单体架构拆分为微服务模块的过程图, diagram, tech-3d]"
主体:  "单体架构拆分为微服务模块的过程图"
剩余:  ["diagram", "tech-3d"]
```

**解析算法**（必须严格按此顺序执行）：

```
以第一个逗号为界，左侧 = 主体描述，右侧 = 逗号分隔的标签列表
对每个标签（去除首尾空格后）：
  1. 在 types.yml 的 key 中精确匹配 → 标记为"类型"
  2. 在 styles.yml 的 key 中精确匹配 → 标记为"风格"
  3. 在 types.yml 的 label 中模糊匹配 → 标记为"类型"
  4. 在 styles.yml 的 label 中模糊匹配 → 标记为"风格"  
  5. 以上都不匹配 → 保留为"额外描述"（附加到场景描述中）
```

**示例**：

| 标记 | 解析结果 |
|------|---------|
| `[img: 架构图, diagram, tech-3d]` | 主体=架构图, 类型=diagram, 风格=tech-3d |
| `[img: 架构图, 流程图, 极简]` | 主体=架构图, 类型=diagram(匹配label), 额外描述="极简" |
| `[img: 架构图, 赛博朋克]` | 主体=架构图, 未匹配到风格 → 列出可用风格让用户选 |
| `[img: 深夜排查问题]` | 主体=深夜排查问题, 缺类型和风格 → 从语境推断 → 确认 |

5. **提取上下文**：每个标记前后各一段落（约 200 字）
6. **完整度判定**：

| 条件 | 判定 | 动作 |
|------|------|------|
| 主体 ≥ 15 字 + 类型明确 + 风格明确 | **充足** | 展示 prompt 摘要后生成 |
| 主体 < 15 字 或 类型缺失 或 风格缺失 或 风格未匹配 | **模糊** | **必须确认** |

**严禁**：看到"工作与生活的平衡"这种 5 字描述就自己脑补成 "A person meditating in a garden at sunrise, work-life balance concept"。铁律规定——必须把推断结果展示出来让用户确认。

### Step 2a: 直接生成（描述充足）

1. **Prompt 组合**（四源合并为英文）：

```
types.yml → type.prompt_hint     "A structured diagram showing..."
styles.yml → style.prompt_prefix "Clean 3D isometric illustration..."
[img]主体 + 额外描述              "微服务请求链路图"
文章语境                         "文章讨论后端架构优化..."
──────────────────────────────────────────────────────
最终 prompt（英文，100-200 words）
```

2. **API 选择**：

| style.model | API model ID |
|:--|:--|
| SD35 | `stabilityai/stable-diffusion-3-5-medium` |
| SDXL | `stabilityai/stable-diffusion-xl-base-1.0` |
| Flux | `black-forest-labs/flux-1-dev` |
| Flux-Fast | `black-forest-labs/flux-1-schnell` |
| Tongyi | `alibaba/tongyi-wanxiang-v1` |

3. **调用 API** → 获取 base64 图片 → 保存 `/tmp/illustrate-{uuid}.png`。详细代码见 `references/siliconflow.md`。

### Step 2b: 确认后生成（描述模糊）

向用户展示：

```
📝 标记 2/3: [img: 工作与生活的平衡]

⚠️ 描述较短（5字），Claude 推断如下：

类型: scene（氛围场景）— 从文章语气推断
风格: japanese-film（日系胶片）— 匹配文章的散文风格
建议 prompt: "A person sitting in a home office at twilight,
              the boundary between work desk and living space
              blurred, soft natural light, contemplative mood"

✅ 直接生成  |  ✏️ 修改  |  🔄 换类型/风格
```

用户确认后 → 同 Step 2a 执行。

### Step 3: Upload — 上传 CDN

```bash
python3 scripts/upload-r2.py /tmp/illustrate-{uuid}.png
# 输出: https://cdn.example.com/illustrations/2026/06/07/abc123def-456.png
```

脚本不可用时直调 S3 API（代码见 `references/cloudflare-r2.md`）。上传后清理临时文件。

### Step 4: Writeback — 回写

```
[img: 微服务请求链路图, diagram, tech-3d]
  → ![微服务请求链路图](https://cdn.example.com/illustrations/2026/06/07/abc.png)
```

展示完成摘要：每张图的原标记和 CDN URL。

---

## 并行生成

多张图默认全部并行调用（API 相互独立），除非用户指定顺序。
Flux 超时 120s，SD35 超时 60s，Tongyi 超时 90s。

---

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 缺少环境变量（Step 0） | **立即停止**，列出缺失变量名和获取方式 |
| API 返回错误 | 重试一次（间隔 3s），仍失败则跳过该图，继续其余 |
| R2 上传失败 | 诊断：boto3 是否安装、凭证是否正确、桶名是否存在 |
| types.yml / styles.yml 缺失 | 使用内置默认值：`type: scene` + `style: tech-3d` |
| 风格名匹配不到 styles.yml | 列出可用风格列表（含 label 中文名），让用户选 |
| 类型名匹配不到 types.yml | 列出可用类型列表，让用户选；或从语境自动推断 |
| [img] 语法无法解析 | 展示原文，提示正确语法：`[img: 场景, 类型, 风格]` |

---

## 常见错误

| 错误 | 为什么发生 | 正确做法 |
|------|-----------|---------|
| **模糊标记擅自脑补 prompt** | 想"帮用户省事" | 铁律：必须确认。再模糊也要问 |
| **先扫描标记再检查环境** | 惯性思维 | Step 0 必须先执行，缺变量直接停 |
| 文章没有 `[img]` 标记就触发 | 用户不知道需要标记 | 展示语法示例，等用户添加后再执行 |
| 风格名拼错，匹配不到 styles.yml | 用户记错名称 | 列出可用风格列表供选择 |
| 不检查环境变量直接尝试生图 | 跳过了 Step 0 | 工作流第一件事就是环境检查 |
| `.env` 未配置就执行 | 用户跳过了配置步骤 | Step 0 会拦住 |
| 生成完不提醒 review | 信任 AI 输出 | 配图完成后提醒用户检查每张图 |
| 串行等待每张图 | 不熟悉并行能力 | 默认并行生图（API 调用互不依赖） |
| API 失败后放弃整批 | 没看到重试策略 | 单张失败不影响其余 |
| 用中文 prompt 调 SD/Flux | 不知道模型偏好英文 | prompt 始终用英文，Claude 从中文场景翻译 |
| 把位置标签当自然语言理解 | 没有结构化解析 | 严格按 Step 1 第 4 步的匹配算法执行 |

---

## 性能参考

- SD 3.5 Medium：约 15s/张，¥0.15
- Flux Dev：约 60s/张，¥0.30
- R2 免费 10GB，配图几乎不超额
