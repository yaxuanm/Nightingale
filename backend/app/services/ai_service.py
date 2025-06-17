import google.generativeai as genai
import os
from typing import List, Dict
import json
import re # Import the re module

class AIService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
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
            
            raw_response_text = response.text
            print(f"DEBUG: Raw Gemini response for parse_scene: {raw_response_text}")

            # Use regex to find the JSON part, handling markdown code blocks
            json_match = re.search(r'```json\n([\s\S]*?)\n```', raw_response_text)
            if json_match:
                json_string = json_match.group(1).strip()
            else:
                # Try to extract between first [ and last ]
                start = raw_response_text.find('[')
                end = raw_response_text.rfind(']')
                if start != -1 and end != -1 and end > start:
                    json_string = raw_response_text[start:end+1].strip()
                else:
                    json_string = raw_response_text.strip()
            print(f"DEBUG: Cleaned JSON string for parsing: >>>{json_string}<<< (length={len(json_string)})")
            elements = json.loads(json_string)
            return elements
        except Exception as e:
            print(f"Error in parse_scene: {str(e)}")
            print(f"ORIGINAL RAW: >>>{raw_response_text}<<<")
            raise

# Create singleton instance
ai_service = AIService() 