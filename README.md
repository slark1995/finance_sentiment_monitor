# 财经舆情监控系统 (Finance Sentiment Monitor)

这是一个集成了爬虫、数据清洗、板块匹配、情绪分析及热度评估的财经舆情监控系统。

## 1. 功能特性
- **多平台支持**：支持从小红书、微博、东方财富、雪球等平台获取舆情数据。
- **智能清洗**：自动去除HTML标签、特殊字符，提取核心文本。
- **板块匹配**：基于自定义关键词库，自动将舆情归类至“人工智能”、“半导体”、“新能源”、“军工”等板块。
- **情绪分析**：利用词典法计算情绪得分，识别“正面”、“中性”、“负面”情绪。
- **热度评估**：综合点赞、评论等互动数据计算热度指标。
- **结构化报告**：自动生成CSV详细结果表及Markdown汇总报告。

## 2. 快速开始

### 环境准备
确保已安装 Python 3.11+，并安装依赖：
```bash
pip install requests pandas jieba beautifulsoup4 lxml tabulate
```

### 运行系统
直接运行主程序：
```bash
python main.py
```

## 3. 项目结构
- `main.py`: 主程序，负责模块集成与报告生成。
- `crawler.py`: 爬虫模块，定义各平台的抓取逻辑。
- `processor.py`: 数据处理模块，负责清洗与板块匹配。
- `analyzer.py`: 分析模块，负责情绪得分与热度计算。
- `DESIGN.md`: 系统设计文档。

## 4. 自定义配置
您可以在 `main.py` 中修改以下配置：
- `SECTOR_KEYWORDS`: 板块及其对应的关键词。
- `POSITIVE_WORDS` / `NEGATIVE_WORDS`: 情绪分析词典。
- `SEARCH_KEYWORDS`: 爬虫搜索的初始关键词。

## 5. 输出结果
- `sentiment_analysis_result.csv`: 包含所有字段的详细分析结果表。
- `RESULT_SUMMARY.md`: 包含板块汇总统计和详细舆情列表的精简报告。
