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
