# 财经舆情监控系统设计文档

## 1. 项目目标
开发一个财经舆情监控系统，能够从主流社交网络和财经论坛（如小红书、微博、东方财富、雪球）爬取新闻和讨论数据，经过清洗、板块匹配、情绪分析和热度评估后，生成结构化的分析报告。

## 2. 核心功能与模块划分

系统将采用模块化设计，分为四个主要模块：爬虫模块（Crawler）、数据处理模块（DataProcessor）、分析模块（Analyzer）和报告模块（Reporter）。

| 模块名称 | 职责描述 | 关键技术/依赖 |
| :--- | :--- | :--- |
| **Crawler** | 负责从指定平台抓取原始数据（标题、正文、时间、URL等）。 | Python Requests, BeautifulSoup, Playwright/Selenium (用于动态内容和登录) |
| **DataProcessor** | 负责数据清洗、标准化和板块匹配。 | Python re, Pandas, 用户定义的板块关键词字典 |
| **Analyzer** | 负责计算情绪得分和热度指标。 | Python NLTK/Jieba (中文分词), 用户定义的情绪词典 |
| **Reporter** | 负责将最终分析结果整理成结构化表格并输出。 | Python Pandas, Markdown/CSV格式输出 |

## 3. 数据模型（Data Schema）

所有抓取和处理后的数据将统一存储为以下结构，方便后续的分析和报告生成。

| 字段名称 | 数据类型 | 描述 | 来源/计算方式 |
| :--- | :--- | :--- | :--- |
| `post_id` | `str` | 帖子/新闻的唯一标识符 | Crawler |
| `platform` | `str` | 来源平台（e.g., 'Weibo', 'Xueqiu'） | Crawler |
| `title` | `str` | 帖子标题 | Crawler |
| `content` | `str` | 帖子正文/内容 | Crawler |
| `publish_time` | `datetime` | 发布时间 | Crawler |
| `raw_url` | `str` | 原始链接 | Crawler |
| `cleaned_content` | `str` | 清洗后的内容（用于分析） | DataProcessor |
| `matched_sectors` | `list[str]` | 匹配到的板块列表（e.g., ['人工智能', '半导体']） | DataProcessor |
| `sentiment_score` | `float` | 情绪得分（-1.0 到 1.0） | Analyzer |
| `sentiment_label` | `str` | 情绪标签（'Positive', 'Neutral', 'Negative'） | Analyzer |
| `heat_index` | `float` | 热度指标（基于评论数、点赞数等） | Analyzer |
| `positive_word_count` | `int` | 发现的积极词汇数量 | Analyzer |
| `negative_word_count` | `int` | 发现的消极词汇数量 | Analyzer |

## 4. 核心逻辑实现细节

### 4.1. 板块匹配逻辑
用户提供的板块关键词字典如下：
```python
SECTOR_KEYWORDS = {
    "人工智能": ["AI", "算力", "大模型", "服务器", "芯片"],
    "新能源": ["光伏", "锂电", "储能", "新能源"],
    "半导体": ["芯片", "制程", "国产替代"],
    "军工": ["军工", "装备", "国防"]
}
```
**匹配规则：** 遍历 `SECTOR_KEYWORDS`，如果帖子的 `title` 或 `content` 中包含任一关键词，则将对应的板块名称加入 `matched_sectors` 列表。

### 4.2. 情绪分析逻辑
用户提供的情绪词典如下：
```python
SENTIMENT_WORDS = {
    "positive": ["利好", "大涨", "爆发", "超预期", "走强"],
    "negative": ["下跌", "利空", "承压", "回调"]
}
```
**情绪得分计算：**
1.  对 `cleaned_content` 进行中文分词（使用 `jieba` 库）。
2.  统计积极词汇 (`P`) 和消极词汇 (`N`) 的出现次数。
3.  **情绪得分 (Sentiment Score)** 计算公式：
    $$
    \text{Score} = \frac{P - N}{P + N + \epsilon}
    $$
    其中 $\epsilon$ 是一个极小的常数（如 1），用于防止分母为零。得分范围在 $[-1, 1]$ 之间。
4.  **情绪标签 (Sentiment Label)** 划分：
    *   $\text{Score} > 0.2$: 'Positive'
    *   $-0.2 \le \text{Score} \le 0.2$: 'Neutral'
    *   $\text{Score} < -0.2$: 'Negative'

### 4.3. 热度指标逻辑
**热度指标 (Heat Index)** 计算公式：
$$
\text{Heat Index} = \log(\text{Comments} + 1) + 0.5 \times \log(\text{Likes} + 1) + \text{Time Decay Factor}
$$
*   **Comments/Likes:** 爬虫模块需尽可能获取帖子的评论数、点赞数等互动数据。
*   **Time Decay Factor:** 考虑到时效性，较新的帖子应有更高的权重。
    $$
    \text{Time Decay Factor} = e^{-\lambda \times \text{Hours Since Publication}}
    $$
    其中 $\lambda$ 为衰减系数（如 0.05），用于控制热度随时间衰减的速度。

## 5. 爬虫策略（Phase 3 重点）
考虑到反爬机制，将采取以下策略：
1.  **东方财富/雪球：** 优先使用 `requests` 库进行 HTTP 请求，结合 `BeautifulSoup` 或正则表达式解析 HTML/JSON 数据。
2.  **微博/小红书：** 优先尝试使用成熟的开源爬虫库（如 `weibo-spider`），若失败则退回使用 `Playwright` 或 `Selenium` 模拟浏览器行为。
3.  **数据获取范围：** 重点获取标题、正文、发布时间、评论数、点赞数。
