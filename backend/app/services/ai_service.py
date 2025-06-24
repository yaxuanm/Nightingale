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
        mood 阶段强制只输出通用短选项。
        """
        # For mood, always return a fixed set of generic moods
        if stage in ['mood', 'audio_mood']:
            return [
                "Calm",
                "Focused",
                "Relaxed",
                "Uplifting",
                "Dreamy",
                "Inspired",
                "Peaceful",
                "Energetic",
                "Melancholic",
                "Motivated"
            ]
        # Otherwise, use LLM as before
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

    def analyze_music_prompt_layers(self, user_text: str = '', extra_fields: dict = None) -> dict:
        """
        使用 LLM 分析用户输入，分解为 genre, style, mood, feeling, instrumentation, tempo, bpm, production_quality, artist_style。
        优先合并前端传来的结构化字段（如 genre, instruments, tempo, usage），在 LLM prompt 分析时将这些字段拼接到 userInput 前面。
        """
        extra_fields = extra_fields or {}
        # 拼接结构化字段为前缀
        prefix_parts = []
        if extra_fields.get('genre'):
            prefix_parts.append(f"Genre: {extra_fields['genre']}")
        if extra_fields.get('instruments'):
            prefix_parts.append(f"Instruments: {', '.join(extra_fields['instruments'])}")
        if extra_fields.get('tempo'):
            prefix_parts.append(f"Tempo: {extra_fields['tempo']}")
        if extra_fields.get('usage'):
            prefix_parts.append(f"Usage: {extra_fields['usage']}")
        prefix = '. '.join(prefix_parts)
        # 拼接到 user_text 前面
        full_text = (prefix + '. ' if prefix else '') + (user_text or '')
        prompt = '''
你是一位顶级的音乐理论家和Meta MusicGen模型的Prompt工程师。
请将以下文本解构为音乐生成的核心元素，输出JSON：
- genre: 类型（如 ambient, rock, cinematic, jazz 等，英文）
- style: 风格（如 90s alternative, lo-fi, synthwave 等，英文）
- mood: 情绪（如 melancholy, peaceful, energetic, epic 等，英文）
- feeling: 细腻感觉（如 lonely, nostalgic, reflective, dreamy 等，英文）
- instrumentation: 乐器（如 acoustic guitar, synth pads, string orchestra 等，英文，数组）
- tempo: 速度描述（如 slow tempo, fast tempo, driving beat 等，英文）
- bpm: BPM数值（如 120, 95 等，数字）
- production_quality: 制作质量（如 high-quality production, vintage recording, clean mix 等，英文）
- artist_style: 艺术家风格（如 in the style of Taylor Swift, inspired by Hans Zimmer 等，英文）
只返回JSON，无需解释。
文本：''' + full_text
        try:
            response = self.model.generate_content(prompt)
            raw = response.text
            # 尝试提取JSON
            json_match = re.search(r'```json\n([\s\S]*?)\n```', raw)
            if json_match:
                json_string = json_match.group(1).strip()
            else:
                start = raw.find('{')
                end = raw.rfind('}')
                if start != -1 and end != -1 and end > start:
                    json_string = raw[start:end+1].strip()
                else:
                    json_string = raw.strip()
            result = json.loads(json_string)
            # 用结构化字段补全/覆盖 LLM 结果
            if extra_fields.get('genre'):
                result['genre'] = extra_fields['genre']
            if extra_fields.get('instruments'):
                result['instrumentation'] = extra_fields['instruments']
            if extra_fields.get('tempo'):
                result['tempo'] = extra_fields['tempo']
            if extra_fields.get('usage'):
                result['usage'] = extra_fields['usage']
            return result
        except Exception as e:
            print(f"Error in analyze_music_prompt_layers: {e}")
            print(f"RAW: >>>{raw if 'raw' in locals() else ''}<<<")
            return {}

    def build_high_fidelity_musicgen_prompt(self, genre: str = None, style: str = None, mood: str = None, feeling: str = None, instrumentation: list = None, tempo: str = None, bpm: int = None, production_quality: str = None, artist_style: str = None) -> str:
        """
        构建高保真 MusicGen Prompt，分层输出，逗号分隔。
        """
        parts = []
        # 第一层：类型与风格
        if genre:
            parts.append(genre)
        if style:
            parts.append(style)
        # 第二层：情绪与感觉
        if mood:
            parts.append(mood)
        if feeling:
            parts.append(feeling)
        # 第三层：配器
        if instrumentation:
            parts.extend(instrumentation)
        # 第四层：速度与节奏
        if tempo:
            parts.append(tempo)
        if bpm:
            parts.append(f"{bpm} BPM")
        # 第五层：制作质量与艺术家风格
        if production_quality:
            parts.append(production_quality)
        if artist_style:
            parts.append(artist_style)
        # 结尾补充
        parts.append("high-quality, rich, layered, immersive music")
        return ", ".join([str(p) for p in parts if p])

    def analyze_audiogen_prompt_layers(self, user_text: str = '', extra_fields: dict = None) -> dict:
        """
        使用 LLM 分析用户输入，分解为 AudioGen 五大支柱：pitch, pattern, intensity, acoustic, location。
        优先合并前端传来的结构化字段，在 LLM prompt 分析时将这些字段拼接到 user_text 前面。
        """
        extra_fields = extra_fields or {}
        prefix_parts = []
        if extra_fields.get('pitch'):
            prefix_parts.append(f"Pitch: {extra_fields['pitch']}")
        if extra_fields.get('pattern'):
            prefix_parts.append(f"Pattern: {extra_fields['pattern']}")
        if extra_fields.get('intensity'):
            prefix_parts.append(f"Intensity: {extra_fields['intensity']}")
        if extra_fields.get('acoustic'):
            prefix_parts.append(f"Acoustic: {extra_fields['acoustic']}")
        if extra_fields.get('location'):
            prefix_parts.append(f"Location: {extra_fields['location']}")
        prefix = '. '.join(prefix_parts)
        full_text = (prefix + '. ' if prefix else '') + (user_text or '')
        prompt = '''
你是一位世界顶级的音效提示词工程师，专为Meta AudioGen服务。请将以下文本解构为五大支柱：
- pitch: 声音的频率（如 high-pitched, deep rumble, low growl 等，英文）
- pattern: 节奏/重复性（如 intermittent beeping, continuous hum, rhythmic tapping 等，英文）
- intensity: 音量/力度（如 faint, distant explosion, deafening roar, gradually increasing in volume 等，英文）
- acoustic: 声学特性（如 muffled sound, crisp and clear, metallic echo, hollow wooden knock 等，英文）
- location: 位置/环境（如 in a vast, empty cavern, on a busy city street, inside a small wooden box 等，英文）
只返回JSON，无需解释。
文本：''' + full_text
        try:
            response = self.model.generate_content(prompt)
            raw = response.text
            json_match = re.search(r'```json\n([\s\S]*?)\n```', raw)
            if json_match:
                json_string = json_match.group(1).strip()
            else:
                start = raw.find('{')
                end = raw.rfind('}')
                if start != -1 and end != -1 and end > start:
                    json_string = raw[start:end+1].strip()
                else:
                    json_string = raw.strip()
            result = json.loads(json_string)
            # 用结构化字段补全/覆盖 LLM 结果
            for k in ['pitch','pattern','intensity','acoustic','location']:
                if extra_fields.get(k):
                    result[k] = extra_fields[k]
            return result
        except Exception as e:
            print(f"Error in analyze_audiogen_prompt_layers: {e}")
            print(f"RAW: >>>{raw if 'raw' in locals() else ''}<<<")
            return {}

    def build_high_fidelity_audiogen_prompt(
        self,
        pitch: str = None,
        pattern: str = None,
        intensity: str = None,
        acoustic: str = None,
        location: str = None,
        extra: str = None
    ) -> str:
        """
        构建高保真 AudioGen Prompt，分层输出，逗号分隔。
        """
        parts = []
        if pitch:
            parts.append(pitch)
        if pattern:
            parts.append(pattern)
        if intensity:
            parts.append(intensity)
        if acoustic:
            parts.append(acoustic)
        if location:
            parts.append(location)
        if extra:
            parts.append(extra)
        return ', '.join([str(p) for p in parts if p])

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