# illustrate — 文章自动配图

Claude Code Skill。在 Markdown 中用 `[img: 场景, 类型, 风格]` 标记配图位置，`/illustrate` 自动生成图片并上传到 Cloudflare R2 CDN。

## 安装

```bash
# skills.sh 安装（推荐）
npx skills add wuji/illustrate-skill

# 本地开发安装
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

编辑 `references/types.yml` 和 `references/styles.yml` 添加你自己的类型和风格。详见 `references/style-guide.md`。

## 依赖

- Python 3.9+
- `boto3`：`pip install boto3`
- 硅基流动 API Key
- Cloudflare R2 存储桶

## 许可证

MIT
