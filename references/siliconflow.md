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
