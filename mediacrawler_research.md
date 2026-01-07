# MediaCrawler 核心实现调研笔记

## 1. 技术架构
MediaCrawler 采用 **Playwright + API 协议** 的混合模式：
- **Playwright**：主要用于登录、获取 Cookie 以及在浏览器上下文中执行 JS 表达式来生成签名（如小红书的 `X-S`）。
- **API 协议**：一旦获取到有效的 Cookie 和签名生成逻辑，就直接通过 `requests` 或 `httpx` 发送原生 API 请求，效率极高。

## 2. 小红书 (XHS) 核心逻辑
- **签名机制**：小红书的请求头包含 `X-S` 和 `X-T`。`X-S` 是通过特定的算法对请求路径、参数和内容进行加密生成的。
- **实现方式**：MediaCrawler 并没有完全逆向 JS，而是通过 Playwright 启动一个浏览器，将签名算法注入到浏览器中，然后通过 `page.evaluate` 调用 JS 函数来生成签名。
- **数据接口**：使用 `https://edith.xiaohongshu.com/api/sns/web/v1/search/notes` 进行搜索。

## 3. 微博 (Weibo) 核心逻辑
- **接口选择**：优先使用微博移动端接口 (`m.weibo.cn`) 或特定的搜索接口。
- **Cookie 管理**：微博对 Cookie 的依赖较强，MediaCrawler 实现了自动化的 Cookie 获取和维持逻辑。

## 4. 改进建议
参考 MediaCrawler，我们的 `crawler.py` 可以进行如下优化：
1. **引入签名生成器**：对于小红书，不再尝试简单模拟，而是使用 Playwright 注入签名脚本。
2. **结构化提取器**：参考其 `extractor.py`，编写更健壮的字段提取逻辑，处理各种边界情况。
3. **统一客户端**：实现一个 `BaseClient` 类，统一处理 Header、Cookie 和代理。
