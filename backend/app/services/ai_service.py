import google.generativeai as genai
import os
from typing import List, Dict, Optional
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

    async def generate_options(self, mode: str, user_input: str, stage: str) -> List[str]:
        """
        根据 mode、user_input、stage 用 Gemini 生成 atmosphere/mood/elements 选项。
        优化：支持中英文输入，LLM 必须输出高质量英文选项，必要时自动翻译。每个选项不超过 10 个英文单词。
        """
        prompt = f"""
        You are an expert in soundscape and music design. The user may input in Chinese or English. Your task is:
        1. Understand the user's intent and context from the following mode and input.
        2. For the stage: {stage}, generate a list of 5 concise, relevant, diverse, and high-quality options in ENGLISH only (even if the user input is in Chinese).
        3. Each option should be a short phrase, no more than 10 English words.
        4. If the user input is in Chinese, you must first understand it, then output the options in English, not Chinese.
        5. Only return a JSON array of strings, e.g. [\"option1\", \"option2\", ...]. No extra text.
        - mode: {mode}
        - user input: {user_input}
        """
        try:
            response = self.model.generate_content(prompt)
            raw_response_text = response.text
            print(f"DEBUG: Raw Gemini response for generate_options: {raw_response_text}")
            # Use regex to find the JSON part, handling markdown code blocks
            json_match = re.search(r'```json\\n([\s\S]*?)\\n```', raw_response_text)
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
            print(f"DEBUG: Cleaned JSON string for options: >>>{json_string}<<< (length={len(json_string)})")
            options = json.loads(json_string)
            if isinstance(options, list) and all(isinstance(opt, str) for opt in options):
                return options
            return None
        except Exception as e:
            print(f"Error in generate_options: {str(e)}")
            print(f"ORIGINAL RAW: >>>{raw_response_text if 'raw_response_text' in locals() else ''}<<<")
            return None

    async def generate_musicgen_options(self, stage: str, user_input: str = "") -> List[str]:
        """
        动态生成 MusicGen 分支的多级选项（genre, instruments, tempo, usage），支持中英文输入，输出高质量英文选项。
        """
        prompt = f"""
        You are an expert in music composition and production. The user may input in Chinese or English. Your task is:
        1. Understand the user's intent and context from the following input.
        2. For the stage: {stage} (one of 'genre', 'instruments', 'tempo', 'usage'), generate a list of 5 concise, relevant, diverse, and high-quality options in ENGLISH only (even if the user input is in Chinese).
        3. If the user input is in Chinese, you must first understand it, then output the options in English, not Chinese.
        4. Only return a JSON array of strings, e.g. ["option1", "option2", ...]. No extra text.
        - user input: {user_input}
        """
        try:
            response = self.model.generate_content(prompt)
            raw_response_text = response.text
            print(f"DEBUG: Raw Gemini response for generate_musicgen_options: {raw_response_text}")
            # Use regex to find the JSON part, handling markdown code blocks
            json_match = re.search(r'```json\\n([\s\S]*?)\\n```', raw_response_text)
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
            print(f"DEBUG: Cleaned JSON string for musicgen options: >>>{json_string}<<< (length={len(json_string)})")
            options = json.loads(json_string)
            if isinstance(options, list) and all(isinstance(opt, str) for opt in options):
                return options
            return None
        except Exception as e:
            print(f"Error in generate_musicgen_options: {str(e)}")
            print(f"ORIGINAL RAW: >>>{raw_response_text if 'raw_response_text' in locals() else ''}<<<")
            return None

def get_instruments_from_ai(atmosphere: Optional[str], mood: Optional[str], elements: Optional[List[str]], user_input: Optional[str], reference_era: Optional[str]) -> List[str]:
    """
    调用 AI 补全乐器（此处为 mock，可对接 Gemini/GPT/OpenAI）。
    """
    # TODO: 实际可用 OpenAI/Gemini API 调用
    # prompt = f"""
    # Given the following user preferences for a music generation model:
    # - Atmosphere: {atmosphere}
    # - Mood: {mood}
    # - Elements: {', '.join(elements or [])}
    # - User input: {user_input}
    # - Reference era: {reference_era}
    # Suggest a suitable combination of 2-4 musical instruments (in English, comma separated, no extra words).
    # """
    # ...
    # return instruments_list
    return ["acoustic guitar", "piano", "soft synth pad"]

def build_musicgen_prompt(
    atmosphere: Optional[str],
    mood: Optional[str],
    elements: Optional[List[str]],
    user_input: Optional[str],
    instruments: Optional[List[str]],
    tempo: Optional[str] = None,
    reference_era: Optional[str] = None
) -> str:
    parts = []
    if atmosphere:
        parts.append(atmosphere)
    if mood:
        parts.append(mood)
    if elements:
        parts.append("with elements like " + ", ".join(elements))
    if instruments:
        parts.append("featuring " + ", ".join(instruments))
    if tempo:
        parts.append(f"tempo: {tempo}")
    if reference_era:
        parts.append(f"in the style of {reference_era}")
    if user_input:
        parts.append(user_input)
    parts.append("high-quality, rich, layered, immersive music")
    return ", ".join(parts)

def build_audiogen_prompt(
    subject: str,
    action: str,
    details: str = "",
    environment: str = "",
    extra: str = ""
) -> str:
    """
    结构化拼接 AudioGen prompt，适用于音效/环境音生成。
    """
    prompt = ""
    if details:
        prompt += f"{details} "
    prompt += f"{subject} {action}"
    if environment:
        prompt += f" {environment}"
    if extra:
        prompt += f", {extra}"
    prompt = prompt.strip().capitalize() + "."
    return prompt

# Create singleton instance
ai_service = AIService() 