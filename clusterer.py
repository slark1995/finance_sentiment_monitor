import jieba
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
import numpy as np

class TopicClusterer:
    def __init__(self, n_topics=5, n_top_words=10):
        self.n_topics = n_topics
        self.n_top_words = n_top_words
        # 停用词列表（简单示例，实际可扩展）
        self.stop_words = set(["的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"])

    def _tokenize(self, text):
        """
        分词并去除停用词
        """
        words = jieba.cut(text)
        return " ".join([w for w in words if w not in self.stop_words and len(w) > 1])

    def fit_topics(self, texts):
        """
        对文本列表进行LDA主题聚类
        """
        if len(texts) < self.n_topics:
            return None, "数据量太少，无法进行主题聚类"

        # 1. 预处理：分词
        processed_texts = [self._tokenize(t) for t in texts]

        # 2. 向量化：使用词频矩阵
        tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2)
        try:
            tf = tf_vectorizer.fit_transform(processed_texts)
        except ValueError:
            # 如果词频太低无法构建矩阵
            return None, "有效词汇不足，无法构建主题模型"

        # 3. 训练LDA模型
        lda = LatentDirichletAllocation(
            n_components=self.n_topics, 
            max_iter=10,
            learning_method='online',
            random_state=42
        )
        lda.fit(tf)

        # 4. 提取主题关键词
        feature_names = tf_vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[:-self.n_top_words - 1:-1]]
            topics.append({
                "topic_id": topic_idx + 1,
                "keywords": top_words,
                "description": f"主题 {topic_idx + 1}: " + ", ".join(top_words[:3])
            })
        
        # 5. 预测每条文本所属的主题
        topic_distributions = lda.transform(tf)
        dominant_topics = np.argmax(topic_distributions, axis=1) + 1
        
        return topics, dominant_topics

    def analyze_trends(self, df):
        """
        分析交易风向：结合主题、情绪和热度
        """
        texts = df['cleaned_content'].tolist()
        topics_info, dominant_topics = self.fit_topics(texts)
        
        if topics_info is None:
            print(f"[!] 主题聚类失败: {dominant_topics}")
            df['topic_id'] = 0
            return df, []

        df['topic_id'] = dominant_topics
        
        # 按主题汇总情绪和热度
        trend_summary = []
        for topic in topics_info:
            topic_df = df[df['topic_id'] == topic['topic_id']]
            if topic_df.empty:
                continue
                
            avg_sentiment = topic_df['sentiment_score'].mean()
            total_heat = topic_df['heat_index'].sum()
            count = len(topic_df)
            
            # 判断交易风向
            if avg_sentiment > 0.2:
                direction = "看多 / 积极布局"
            elif avg_sentiment < -0.2:
                direction = "看空 / 谨慎观望"
            else:
                direction = "震荡 / 趋势不明"
                
            trend_summary.append({
                "主题ID": topic['topic_id'],
                "核心关键词": ", ".join(topic['keywords'][:5]),
                "文章数": count,
                "平均情绪": round(avg_sentiment, 3),
                "总热度": round(total_heat, 2),
                "建议交易风向": direction
            })
            
        return df, trend_summary

if __name__ == "__main__":
    # 测试代码
    test_texts = [
        "AI大模型算力芯片爆发，国产替代进程加快",
        "人工智能服务器需求激增，芯片制程突破",
        "新能源光伏锂电储能走强，政策利好不断",
        "军工装备国防现代化建设，订单超预期",
        "半导体芯片国产化率提升，制程工艺优化",
        "大模型算力中心建设提速，AI芯片供不应求",
        "光伏组件价格回调，新能源长期趋势不变",
        "国防军工板块走强，装备升级换代"
    ]
    df_test = pd.DataFrame({"cleaned_content": test_texts, "sentiment_score": [0.5, 0.6, 0.4, 0.3, 0.5, 0.7, -0.1, 0.4], "heat_index": [10, 12, 8, 7, 9, 15, 5, 8]})
    clusterer = TopicClusterer(n_topics=3)
    df_res, summary = clusterer.analyze_trends(df_test)
    print(pd.DataFrame(summary))
