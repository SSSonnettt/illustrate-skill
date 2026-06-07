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
  version: "1.0.0"
  category: content-creation
  models: sd35,sdxl,flux,tongyi
  cdn: cloudflare-r2
---

# illustrate — 文章自动配图

根据文章的 `[img]` 占位符自动生成配图，上传到 Cloudflare R2 CDN，回写 Markdown。

**核心理念**：类型（画什么结构）× 风格（画成什么样子）二维矩阵，混合模式交互。

---

## 快速参考

| 用户说 | 你做什么 |
|--------|---------|
| `/illustrate`，文章有 `[img]` | 扫描标记 → 生成 → 上传 → 替换 |
| `/illustrate`，文章没有 `[img]` | 教用户标记语法，等用户添加后再触发生成 |
| `[img: 场景, diagram, tech-3d]` | 完整指定 → 直接生成，不确认 |
| `[img: 场景]` | 缺类型/风格 → 从全文语境推断 → 先确认再生成 |
| 加新风格 | 编辑 `references/styles.yml` + `references/types.yml` |
| API 调用失败 | 重试一次（间隔 3s），仍失败则跳过该图 |
| 想改某张图的 prompt | 确认阶段直接修改，Claude 使用修改后的版本 |

---

## 何时适用 / 不适用

**适用**：文章已写完、Markdown 中已有 `[img:...]` 标记、需要配图后发布。
**不适用**：文章还没写、需要自己设计图片内容（非 AI 生成）、视频/GIF、文章没有任何配图标记且用户拒绝添加。

---

## 工作流

严格按 Parse → Generate → Upload → Writeback。

### Step 1: Parse — 扫描标记，分析语境

1. 定位 Markdown 文件（用户指定路径 > 搜索 `.md` > 询问）
2. 扫描 `[img:...]` 标记：正则 `\[img:\s*([^\]]+)\]`
3. 加载 `references/types.yml` 和 `references/styles.yml`
4. 解析每个标记：

```
[img: 场景描述, 位置1?, 位置2?]
```

位置参数按以下规则推断：匹配到 types.yml → 类型；匹配到 styles.yml → 风格；都不匹配 → 当作描述的一部分。两个都缺失 → 从文章全文语境推断推荐值。

5. 提取每个标记前后各一段落（约 200 字）作为语境
6. 按完整度分类：**描述充足 → Step 2a** / **模糊 → Step 2b**
7. 模糊标记先向用户展示推断结果和建议 prompt，等确认再继续

### Step 2a: 直接生成（描述充足）

合并四源生成英文 prompt：

```
type.prompt_hint + style.prompt_prefix + 场景描述 + 文章语境 → 最终 prompt
```

根据 `style.model` 映射到硅基流动 model ID（映射表见 `references/siliconflow.md`），调 API 生图，获取 base64 图片。保存到 `/tmp/illustrate-{uuid}.png`。

### Step 2b: 确认后生成（描述模糊）

向用户展示：推断的类型、推荐风格、建议的英文 prompt。用户可修改任何字段。确认后同 Step 2a 执行。

### Step 3: Upload — 上传 CDN

```bash
python3 scripts/upload-r2.py /tmp/illustrate-{uuid}.png
```

脚本不可用时直调 S3 API（见 `references/cloudflare-r2.md`）。上传完成后清理临时文件。

### Step 4: Writeback — 回写

```
[img: 微服务请求链路图, diagram, tech-3d]
  → ![微服务请求链路图](https://cdn.example.com/illustrations/2026/06/07/abc.png)
```

展示完成摘要：每张图的原标记和 CDN URL。

---

## 并行生成

多张图默认全部并行调用（API 相互独立），除非用户指定顺序。
Flux 模型超时设 120s，SD35 设 60s。

---

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 缺少环境变量 | 列出缺失的变量名，告诉用户在哪个平台获取 |
| API 返回错误 | 重试一次（间隔 3s），仍失败则跳过该图，继续处理其余 |
| R2 上传失败 | 诊断：boto3 是否安装、凭证是否正确、桶名是否存在 |
| types.yml / styles.yml 缺失 | 回退到内置默认值：`tech-3d + scene` |
| [img] 语法无法解析 | 展示原文，请用户修正 |

---

## 常见错误

| 错误 | 为什么发生 | 正确做法 |
|------|-----------|---------|
| 文章没有 `[img]` 标记就触发 | 用户不知道需要标记 | 展示语法示例，等用户添加后再执行 |
| 风格名拼错，匹配不到 styles.yml | 用户记错名称 | 列出可用的风格列表供选择 |
| `.env` 未配置就执行 | 用户跳过了配置步骤 | 逐个检查环境变量，缺什么指向对应平台的获取链接 |
| 生成完不检查就提交 | 用户信任 AI 输出 | 配图完成后提醒用户 review 每张图 |
| 直接串行等每张图 | 不熟悉并行能力 | 并行生图可以节省时间 |
| API 失败后放弃整批 | 没看到重试策略 | 单张失败不影响其余，失败的重试一次 |
| 用中文 prompt 调 SD/Flux | 不知道模型偏好英文 | prompt 始终用英文，由 Claude 从中文场景翻译 |

---

## 性能参考

- SD 3.5 Medium：约 15s/张，¥0.15
- Flux Dev：约 60s/张，¥0.30
- R2 免费 10GB，配图几乎不超额
