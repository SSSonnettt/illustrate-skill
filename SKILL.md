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
- **配置文件**：`references/types.yml`、`references/styles.yml`

## 工作流

严格按 Parse → Generate → Upload → Writeback 顺序。

### Step 1: Parse — 扫描占位符，分析语境

1. **定位 Markdown 文件**：用户指定路径 > 搜索当前目录 `.md` 文件 > 询问用户
2. **扫描 `[img:...]` 标记**：正则 `\[img:\s*([^\]]+)\]`
3. **加载配置文件**：读取 `references/types.yml` 和 `references/styles.yml`
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
references/types.yml → type.prompt_hint     "A structured diagram showing..."
    +
references/styles.yml → style.prompt_prefix "Clean 3D isometric illustration..."
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

1. 微服务请求链路图 → ![](https://cdn.xxx.com/abc.png)
2. 深夜调试场景     → ![](https://cdn.xxx.com/def.png)
3. 数据库索引结构   → ![](https://cdn.xxx.com/ghi.png)

Markdown 已更新，可直接分发或发布。
```

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 缺少环境变量 | 提示用户设置，给出具体变量名和获取方式 |
| API 返回错误 | 重试一次（间隔 3s），仍失败则跳过该图并告知用户 |
| R2 上传失败 | 检查 boto3 是否安装、凭证是否正确，给出诊断 |
| references/types.yml 或 references/styles.yml 不存在 | 使用内置默认值（tech-3d + scene） |
| [img] 标记语法错误 | 展示原文，请用户修正 |

## 性能说明

- 每张图 API 调用约 15-60 秒（SD 3.5 Medium 约 15s，Flux 约 60s）
- 多张图可并行调用
- 成本约 ¥0.12-0.30/张（取决于模型选择）
- R2 存储免费额度 10GB，配图场景几乎不会超额
