import google.generativeai as genai
import os
from typing import List, Dict
import json

class AIService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def parse_scene(self, description: str) -> List[Dict]:
        """解析场景描述，提取音频元素"""
        prompt = f"""
        分析以下场景描述，提取所有可能的声音元素：
        {description}
        
        请以JSON格式返回，包含以下字段：
        - name: 声音元素名称
        - volume: 音量大小(0-1)
        - position: 位置("foreground"或"background")
        - duration: 持续时间(秒)
        
        示例输出格式：
        [
            {{
                "name": "rain",
                "volume": 0.7,
                "position": "background",
                "duration": 180.0
            }},
            {{
                "name": "cafe_chatter",
                "volume": 0.5,
                "position": "foreground",
                "duration": 180.0
            }}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # 解析返回的JSON字符串
            elements = json.loads(response.text)
            return elements
            
        except Exception as e:
            print(f"Error in parse_scene: {str(e)}")
            raise 