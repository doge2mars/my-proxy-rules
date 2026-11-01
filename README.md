# 🚀 my-proxy-rules (专属代理分流规则与订阅转换模板)

本项目为个人定制的 Clash / Mihomo / OpenClash 规则集与 Subconverter 订阅转换模板仓库，旨在实现：
- 🧱 **自建节点彻底隔离**：搬瓦工、RackNerd、香港奈飞、韩国春川独立成组，不与机场混杂；
- ⚖️ **双模自由切换**：所有自建与机场地区分组，均支持 **【♻️ 自动测速】** 与 **【⚖️ 一致性哈希负载均衡】** 自由选配；
- 🛡️ **严格防风控机制**：负载均衡采用 `consistent-hashing`，同网站同会话固定单一 IP，多设备自动并发平摊带宽，永不跳 IP 触发网站风控；
- 🎬 **全业务精准分流**：独立 AI 平台（ChatGPT、Claude、Gemini）、Disney+、Netflix、YouTube、Prime Video 等流媒体专线直达。

---

## 📌 订阅转换配置模板 (INI)

### 1. 双模负载均衡全能版 (当前推荐 ⭐⭐⭐⭐⭐)
> **特性**：自建隔离 + 每个国家/机器支持自动测速与一致性哈希负载均衡自由切换。

- **Raw 直链 (用于 Subconverter / Cloudflare Workers)**：
  ```text
  https://raw.githubusercontent.com/doge2mars/my-proxy-rules/main/ACL4SSR_Online_Full_MultiMode.ini
  ```

---

## 📋 规则集文件 (Rule-Providers / Ruleset)

| 规则文件 | 说明 | 规则类型 | Raw 直链 |
| :--- | :--- | :---: | :--- |
| **`AI.list`** | AI 平台整合规则集 (OpenAI / Claude / Gemini / Copilot 等) | DOMAIN | [点击查看](https://raw.githubusercontent.com/doge2mars/my-proxy-rules/main/AI.list) |
| **`custom_ai.list`** | 个人私有补充 AI 域名列表 | DOMAIN | [点击查看](https://raw.githubusercontent.com/doge2mars/my-proxy-rules/main/custom_ai.list) |

---

## ⚙️ 接入与部署指南

### 1. Cloudflare Workers / Pages 汇聚订阅接入
在 Cloudflare Pages 环境变量中配置：
- **`SUBAPI`**：填写自建后端（如 `sub.dogecoinusd.org`）
- **`SUBCONFIG`**：
  ```text
  https://raw.githubusercontent.com/doge2mars/my-proxy-rules/main/ACL4SSR_Online_Full_MultiMode.ini
  ```

### 2. 软路由 OpenClash 接入
使用带有此模板配置的 Subconverter 链接即可拉取全节点与双模策略组。
