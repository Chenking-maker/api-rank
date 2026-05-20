# AI API 中转站站点信息汇总

---

## 1. yunwu.ai (New API)

| 项目 | 信息 |
|------|------|
| **站点名称** | New API (yunwu.ai) |
| **网站地址** | https://yunwu.ai |
| **站点描述** | AI 大模型 API 中转聚合平台，提供统一接口调用多家主流 AI 模型，支持按量计费。 |

### 支持的模型（共计 479 个模型，部分列举）

**OpenAI 系列：**
- gpt-5.5、gpt-5.5-pro、gpt-5.4-mini、gpt-chat-latest
- gpt-image-2（图像生成）、dall-e-3（图像生成）

**Anthropic Claude 系列：**
- claude-opus-4-7（支持 100 万 token 上下文窗口、128k 最大输出）

**Google Gemini 系列：**
- gemini-3.1-flash-lite、gemini-3.1-flash-tts-preview

**xAI Grok 系列：**
- grok-4.2-fast、grok-4-20-non-reasoning、grok-4-20-reasoning

**DeepSeek 系列：**
- deepseek-v4-flash、deepseek-v4-pro

**阿里通义千问系列：**
- qwen3.6-max-preview

**字节豆包系列：**
- doubao-seed-2-0-lite-260428、doubao-seed-2-0-mini-260428

**视频生成系列：**
- happyhorse-1.0-t2v（文生视频）、happyhorse-1.0-i2v（图生视频）、happyhorse-1.0-r2v（参考生视频）、happyhorse-1.0-video-edit（视频编辑）

### 特色功能
- **模型数量丰富**：共计 479 个模型，覆盖文本对话、图像生成、视频生成、语音合成等多模态场景
- **按量计费**：支持按量付费和阶梯计费两种模式，价格透明公开
- **多模态支持**：涵盖文本、图像、音频、视频生成与理解
- **免费注册**：提供注册页面，新用户可注册使用
- **代理分销**：提供 Agent to join（代理加盟）计划
- **需要登录**：查看完整模型列表和价格需要注册登录

---

## 2. web.apiplus.org

| 项目 | 信息 |
|------|------|
| **站点名称** | New API (web.apiplus.org) |
| **网站地址** | https://web.apiplus.org |
| **站点描述** | AI 聊天与绘画平台，提供在线对话和 AI 绘图功能，默认使用 gpt-3.5-turbo 模型。 |

### 支持的模型
- **gpt-3.5-turbo**（页面默认显示的对话模型）
- 支持 AI Drawing（AI 绘图）功能

> **注意**：该站点首页展示为聊天界面，未公开完整的模型列表。大部分功能页面（/login、/register、/about、/pricing）均返回 "Cannot GET" 错误，表明该站点可能：
> - 仅提供 Web 聊天界面而非 API 中转服务
> - 需要特定访问权限或邀请码
> - 站点功能有限或处于维护状态

### 特色功能
- **在线聊天**：提供 Web 端 AI 对话功能
- **AI 绘图**：支持 AI Drawing 绘画功能
- **免费额度**：页面显示 "Remain:0/4k"，暗示提供免费额度（4000 次请求）
- **访问受限**：多个页面无法访问，功能较为有限

---

## 3. n1n.ai

| 项目 | 信息 |
|------|------|
| **站点名称** | n1n AI (n1n.ai) |
| **网站地址** | https://n1n.ai |
| **API 地址** | https://api.n1n.ai/v1 |
| **文档地址** | https://docs.n1n.ai |
| **站点描述** | 企业级统一 LLM API 网关，一个 API Key 即可连接全球 500+ 大模型，面向开发者提供低延迟、高可用的 AI API 聚合服务。 |

### 支持的模型（共计 500+ 个模型，按类别列举）

**OpenAI GPT 系列：**
- GPT-5、GPT-5.5、GPT-5.4-mini、GPT-5.5-pro
- gpt-image-1、gpt-image-1.5、gpt-image-2（图像生成）
- whisper-1、gpt-4o-transcribe（语音转文字）
- gpt-4o-mini-tts（语音合成）

**Anthropic Claude 系列：**
- Claude 4.5、Claude Opus 4.7
- 支持原生格式和 Chat 兼容格式
- 支持思考模式、PDF 解析、联网搜索

**Google Gemini 系列：**
- Gemini 3 Pro、Gemini 3.1 Flash、Gemini 3.1 Pro Preview
- 支持文本生成、图片生成/编辑/理解、视频理解、音频理解、代码执行、TTS

**xAI Grok 系列：**
- Grok Image Create/Edit（图像生成与编辑）
- Grok 视频生成

**DeepSeek 系列：**
- DeepSeek V3.1（支持思考程度控制）
- DeepSeek V4、DeepSeek OCR

**国产模型系列：**
- 豆包 Seedream 3.0/4.0/4.5（图像生成）
- 豆包 Seedance（视频生成）
- 通义千问 Qwen 系列（含 qwen-mt-turbo 翻译）
- 即梦绘画/视频生成
- 腾讯 AIGC（图像/视频生成）

**绘画模型：**
- Midjourney（全功能：Imagine、Blend、Describe、Shorten、Swap Face 等）
- Ideogram 3.0（文生图、编辑、Remix、Reframe、背景替换）
- Stable Diffusion、DALL-E 3
- FLUX 系列（支持 OpenAI 和 Replicate 格式）
- Fal.ai 平台（nano-banana 等）
- Qwen-Image 系列（千问图像生成/编辑）

**视频生成模型：**
- Sora 2 / Sora 2 Pro（OpenAI 官方视频格式）
- Luma、Runway、Veo（Google）
- 可灵 Kling（文生视频、图生视频、视频编辑、数字人、音效等全套功能）
- 海螺 MiniMax（视频/音频生成）
- Vidu（视频/图片/音频生成）
- Wan 万向系列

### 特色功能
- **500+ 模型一键接入**：一个 API Key 通用所有模型，完全兼容 OpenAI 接口规范，零代码修改即可迁移
- **全球 CN2 GIA 加速**：24 个企业级节点覆盖 7 大区域，国内直连无需 VPN，延迟低至 98ms
- **99.99% 高可用 SLA**：冗余网关路由，上游故障自动切换
- **新用户免费额度**：注册即送 $0.2 免费测试额度
- **灵活支付**：支持支付宝、微信、Stripe、USDT 等多种支付方式
- **企业级权限管理**：支持子 Key 分发，可设置配额、有效期、模型权限
- **统一计费**：一个账单汇总所有模型用量，余额永不过期
- **完善文档**：提供中英文文档，包含丰富的 API 示例和 SDK
- **多格式兼容**：支持 OpenAI 格式、Anthropic 原生格式、Gemini 原生格式等多种 API 协议
- **开发者生态**：50,000+ 开发者，日处理 80M+ API 请求

---

## 对比总结

| 对比维度 | yunwu.ai | web.apiplus.org | n1n.ai |
|----------|----------|-----------------|--------|
| **模型数量** | 479 个 | 未知（极少） | 500+ 个 |
| **定位** | API 中转平台 | Web 聊天/绘图工具 | 企业级 API 网关 |
| **免费额度** | 未明确 | 有（4k 次请求） | $0.2 |
| **支付方式** | 未明确 | 不适用 | 支付宝/微信/Stripe/USDT |
| **文档完善度** | 一般 | 无 | 非常完善（中英文） |
| **全球加速** | 未知 | 无 | CN2 GIA 24 节点 |
| **多模态支持** | 文本/图像/视频/音频 | 文本/图像 | 文本/图像/视频/音频（最全） |
| **OpenAI 兼容** | 是 | 不适用 | 是 |
| **企业级功能** | 代理分销 | 无 | 子 Key、权限管理、监控 |
| **可访问性** | 需注册查看详情 | 多页面无法访问 | 完全公开 |

> **数据采集时间**：2026-05-20
> **说明**：以上信息基于各站点公开页面内容提取，实际服务可能随时更新。建议使用前访问各站点确认最新信息。
