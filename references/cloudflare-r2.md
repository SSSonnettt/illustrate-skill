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
