import pandas as pd
from crawler import FinanceCrawler
from processor import DataProcessor
from analyzer import SentimentAnalyzer
from clusterer import TopicClusterer
import os

def main():
    # 1. 配置参数
    SECTOR_KEYWORDS = {
        "人工智能": ["AI", "算力", "大模型", "服务器", "芯片"],
        "新能源": ["光伏", "锂电", "储能", "新能源"],
        "半导体": ["芯片", "制程", "国产替代"],
        "军工": ["军工", "装备", "国防"]
    }
    
    POSITIVE_WORDS = ["利好", "大涨", "爆发", "超预期", "走强", "突破", "强势"]
    NEGATIVE_WORDS = ["下跌", "利空", "承压", "回调", "惨淡", "风险", "走弱"]
    
    SEARCH_KEYWORDS = ["人工智能", "半导体", "新能源", "军工"]

    print("=== 财经舆情监控系统启动 ===")

    # 2. 爬取数据
    crawler = FinanceCrawler()
    raw_data = crawler.run(SEARCH_KEYWORDS)
    print(f"[+] 原始数据抓取完成，共 {len(raw_data)} 条记录")

    # 3. 数据清洗与板块匹配
    processor = DataProcessor(SECTOR_KEYWORDS)
    df_processed = processor.process(raw_data)
    print("[+] 数据清洗与板块匹配完成")

    # 4. 情绪分析与热度评估
    analyzer = SentimentAnalyzer(POSITIVE_WORDS, NEGATIVE_WORDS)
    df_final = analyzer.analyze_dataframe(df_processed)
    print("[+] 情绪分析与热度评估完成")

    # 5. NLP 主题聚类与交易风向分析
    print("[*] 正在进行 NLP 主题聚类分析...")
    clusterer = TopicClusterer(n_topics=4) # 假设发现4个主要主题
    df_final, trend_summary = clusterer.analyze_trends(df_final)
    print("[+] 主题聚类与风向分析完成")

    # 6. 结果整理与输出
    # 展开板块列表，方便按板块统计
    df_exploded = df_final.explode('matched_sectors')
    
    # 按板块汇总统计
    sector_summary = df_exploded.groupby('matched_sectors').agg({
        'sentiment_score': 'mean',
        'heat_index': 'sum',
        'title': 'count'
    }).rename(columns={'title': '文章数量', 'sentiment_score': '平均情绪得分', 'heat_index': '总热度'})
    
    # 保存结果
    output_file = "sentiment_analysis_result.csv"
    df_final.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n=== 分析结果摘要 ===")
    print(sector_summary)
    print(f"\n[!] 详细结果已保存至: {output_file}")

    # 生成Markdown格式的结果表供展示
    display_cols = ['platform', 'matched_sectors', 'sentiment_label', 'sentiment_score', 'heat_index', 'title']
    # 限制标题长度用于展示
    df_display = df_final[display_cols].copy()
    df_display['title'] = df_display['title'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
    
    with open("RESULT_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write("# 财经舆情分析与交易风向报告\n\n")
        
        f.write("## 1. 自动发现的交易风向 (NLP 主题聚类)\n\n")
        if trend_summary:
            f.write(pd.DataFrame(trend_summary).to_markdown(index=False) + "\n\n")
        else:
            f.write("数据量不足，未生成自动聚类主题。\n\n")

        f.write("## 2. 预定义板块汇总统计\n\n")
        f.write(sector_summary.to_markdown() + "\n\n")
        
        f.write("## 3. 详细舆情列表\n\n")
        # 增加主题ID列
        display_cols_with_topic = ['platform', 'topic_id', 'matched_sectors', 'sentiment_label', 'sentiment_score', 'heat_index', 'title']
        df_display_final = df_final[display_cols_with_topic].copy()
        df_display_final['title'] = df_display_final['title'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
        f.write(df_display_final.to_markdown(index=False) + "\n")

if __name__ == "__main__":
    main()
