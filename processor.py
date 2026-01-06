import re
import pandas as pd

class DataProcessor:
    def __init__(self, sector_keywords):
        self.sector_keywords = sector_keywords

    def clean_text(self, text):
        """
        清洗文本：去除HTML标签、特殊字符、多余空格等
        """
        if not text:
            return ""
        # 去除HTML标签
        text = re.sub(r'<.*?>', '', text)
        # 去除URL
        text = re.sub(r'http[s]?://\S+', '', text)
        # 去除特殊字符，保留中英文和数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
        # 合并多个空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def match_sectors(self, text):
        """
        根据关键词匹配板块
        """
        matched = []
        for sector, keywords in self.sector_keywords.items():
            for kw in keywords:
                if kw.lower() in text.lower():
                    matched.append(sector)
                    break
        return matched

    def process(self, raw_data):
        """
        处理原始数据列表
        """
        processed_data = []
        for item in raw_data:
            full_text = (item.get('title', '') + " " + item.get('content', '')).strip()
            cleaned_text = self.clean_text(full_text)
            sectors = self.match_sectors(cleaned_text)
            
            # 如果没有匹配到任何板块，默认标记为"其他"
            if not sectors:
                sectors = ["其他"]
                
            processed_item = item.copy()
            processed_item['cleaned_content'] = cleaned_text
            processed_item['matched_sectors'] = sectors
            processed_data.append(processed_item)
            
        return pd.DataFrame(processed_data)

if __name__ == "__main__":
    SECTOR_KEYWORDS = {
        "人工智能": ["AI", "算力", "大模型", "服务器", "芯片"],
        "新能源": ["光伏", "锂电", "储能", "新能源"],
        "半导体": ["芯片", "制程", "国产替代"],
        "军工": ["军工", "装备", "国防"]
    }
    processor = DataProcessor(SECTOR_KEYWORDS)
    test_data = [{"title": "AI大模型发布", "content": "这次算力提升很大"}]
    df = processor.process(test_data)
    print(df)
