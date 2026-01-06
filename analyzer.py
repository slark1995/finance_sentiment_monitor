import jieba
import numpy as np
from datetime import datetime

class SentimentAnalyzer:
    def __init__(self, positive_words, negative_words):
        self.positive_words = set(positive_words)
        self.negative_words = set(negative_words)

    def analyze_sentiment(self, text):
        """
        计算情绪得分和标签
        """
        words = list(jieba.cut(text))
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        
        # 计算得分: (pos - neg) / (pos + neg + 1)
        score = (pos_count - neg_count) / (pos_count + neg_count + 1)
        
        if score > 0.1:
            label = "正面"
        elif score < -0.1:
            label = "负面"
        else:
            label = "中性"
            
        return score, label, pos_count, neg_count

    def calculate_heat(self, row):
        """
        计算热度指标
        Heat = log(comments + 1) + 0.5 * log(likes + 1)
        """
        likes = row.get('likes', 0)
        comments = row.get('comments', 0)
        heat = np.log1p(comments) + 0.5 * np.log1p(likes)
        return round(heat, 2)

    def analyze_dataframe(self, df):
        """
        对DataFrame进行批量分析
        """
        results = df.apply(lambda row: self.analyze_sentiment(row['cleaned_content']), axis=1)
        df['sentiment_score'] = [r[0] for r in results]
        df['sentiment_label'] = [r[1] for r in results]
        df['pos_words'] = [r[2] for r in results]
        df['neg_words'] = [r[3] for r in results]
        df['heat_index'] = df.apply(self.calculate_heat, axis=1)
        return df

if __name__ == "__main__":
    pos = ["利好", "大涨", "爆发", "超预期", "走强"]
    neg = ["下跌", "利空", "承压", "回调"]
    analyzer = SentimentAnalyzer(pos, neg)
    import pandas as pd
    df = pd.DataFrame([{"cleaned_content": "今天利好消息大涨，超预期", "likes": 100, "comments": 20}])
    df = analyzer.analyze_dataframe(df)
    print(df)
