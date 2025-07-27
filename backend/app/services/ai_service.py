from google import genai
import os
import json
import re
import time
import random
from typing import List, Dict, Optional

class AIService:
    def __init__(self):
        self.client = genai.Client()
        # 多个备选模型，按配额可用性排序（基于测试结果）
        self.models = [
            "gemini-2.5-flash-lite-preview-06-17",  # 最具成本效益且支持高吞吐量 ⭐
            "gemini-2.5-flash",                      # 适应性思维，成本效益 ⭐
            "gemini-1.5-flash",                      # 快速而多样的性能 ⭐
            "gemini-2.0-flash-lite",                 # 成本效益和低延迟（备用）
            "gemini-1.5-pro",                        # 复杂推理任务（最后备用，配额限制）
        ]
        self.current_model_index = 0

    def _get_current_model(self):
        """获取当前模型"""
        return self.models[self.current_model_index]

    def _switch_to_next_model(self):
        """切换到下一个模型"""
        self.current_model_index = (self.current_model_index + 1) % len(self.models)
        print(f"🔄 切换到模型: {self._get_current_model()}")
        return self._get_current_model()

    async def parse_scene(self, description: str) -> List[Dict]:
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
            {{"name": "rain", "volume": 0.7, "position": "background", "duration": 180.0}},
            {{"name": "cafe_chatter", "volume": 0.5, "position": "foreground", "duration": 180.0}}
        ]
        """
        try:
            response = self.client.models.generate_content(
                model=self._get_current_model(),
                contents=prompt
            )
            raw_response_text = response.text or ""
            json_match = re.search(r'```json\n([\s\S]*?)\n```', raw_response_text)
            if json_match:
                json_string = json_match.group(1).strip()
            else:
                start = raw_response_text.find('[')
                end = raw_response_text.rfind(']')
                if start != -1 and end != -1 and end > start:
                    json_string = raw_response_text[start:end+1].strip()
                else:
                    json_string = raw_response_text.strip()
            elements = json.loads(json_string)
            return elements
        except Exception as e:
            print(f"Error in parse_scene: {str(e)}")
            print(f"ORIGINAL RAW: >>>{raw_response_text if 'raw_response_text' in locals() else ''}<<<")
            raise

    async def generate_options(self, mode: str, user_input: str, stage: str) -> List[str]:
        # 合并后的 soundscape description prompt
        fallback_options = {
            'audio_atmosphere': ["In a large empty warehouse", "Deep in a lush rainforest", "Urban street corner at night", "Inside a cozy cafe", "On a snowy mountain peak"],
            'audio_elements': ["Rain", "Footsteps", "Birds chirping", "Thunder", "Wind blowing"],
            'audio_style': ["Natural", "Synthetic", "Mixed", "Organic", "Electronic"],
            'music_genre': ["Ambient", "Classical", "Jazz", "Electronic", "Folk"],
            'music_instruments': ["Piano", "Strings", "Synth", "Guitar", "Drums"],
            'music_tempo': ["Slow", "Medium", "Fast", "Variable", "Steady"],
            'music_usage': ["Background", "Focus", "Relaxation", "Study", "Sleep"]
        }
        if stage in ['mood', 'audio_mood', 'mood']:
            if mode == 'asmr':
                prompt = f"""
List 5 ASMR-specific feelings or triggers suitable for AI sound generation. 80% should be classic ASMR triggers (e.g. Tapping, Brushing, Page turning, Ear cleaning, Crinkling, Hand movements, Water sounds, Glove sounds, Typing, Spray sounds, Personal attention, Hair brushing, Face touching, Light triggers, Scalp massage, Whispering, Scratching, Plastic crinkling, Mic brushing, Roleplay: doctor, Roleplay: haircut, Roleplay: spa). 20% can be gentle, relaxing environmental sounds (e.g. Gentle rain, Soft wind, Distant thunder, Footsteps on carpet, Water dripping, Fire crackling, Pages turning in a quiet library). Do not generate poetic lines, abstract moods, or pure nature scenes without a tactile or ASMR element. Only return a JSON array of strings.
Examples: ["Tapping", "Brushing", "Page turning", "Ear cleaning", "Gentle rain"]
- mode: {mode}
- user input: {user_input}
"""
            else:
                prompt = f"""
List 5 moods for a soundscape. Each should be a single English word or a short phrase (max 2 words), e.g. "Calm", "Mysterious", "Uplifting", "Bittersweet", "Suspenseful". Do not include any scene, sound, or environment words.
Examples: ["Calm", "Dreamy", "Energetic", "Peaceful", "Tense"]
Only return a JSON array of strings.
- mode: {mode}
- user input: {user_input}
"""
        elif stage in ['audio_atmosphere']:
            prompt = f"""
Based on the user's input and mode, generate 5 atmosphere options. The first option should be a concise, standardized version of the user's idea. The remaining options should be closely related variations, each with a slight change or added detail. Do not simply repeat the original input. Do not include any specific sound elements (like rain, footsteps, birds, etc.), only describe the overall scene or environment.

User input: "A cozy cafe on a rainy afternoon"
Examples: [
  "Cozy cafe, rainy afternoon",
  "Warm cafe, rain on windows",
  "Cafe, soft jazz, rainy day",
  "Cafe, fresh coffee aroma, rain",
  "Quiet cafe, foggy windows"
]

Now, for the following user input, generate 5 atmosphere options as above.
User input: {user_input}
Only return a JSON array of strings.
- mode: {mode}
"""
        elif stage in ['audio_elements', 'elements']:
            if mode == 'asmr':
                prompt = f"""
For 'asmr' and audio_elements stage:
- Generate 5 ASMR sound element options.
- At least 2-3 options should be classic ASMR triggers unrelated to the user's input, such as: Tapping, Brushing, Ear cleaning, Crinkling, Hand movements, Water sounds, Glove sounds, Typing, Spray sounds, Personal attention, Hair brushing, Face touching, Light triggers, Scalp massage, Whispering, Scratching, Plastic crinkling, Mic brushing, Roleplay: doctor, Roleplay: haircut, Roleplay: spa.
- The remaining options can be related to the user's input (e.g. paper/page), but do not make all options the same category.
- Do not simply repeat or paraphrase the user's input. Each option should be a distinct ASMR sound type or gentle environmental sound.
- Example chips: Tapping, Brushing, Page turning, Ear cleaning, Crinkling, Whispering, Gentle rain, Soft wind
User input: {user_input}
Only return a JSON array of 5 strings.
"""
            else:
                prompt = f"""
Generate 5 distinct sound elements that could be used to create a soundscape based on the user's input. These should be specific, concrete sounds that can be generated by AI audio models, not scene descriptions or emotional states.

**CRITICAL GUIDELINES:**
- Focus on actual sound elements: footsteps, rain, wind, birds, machinery, voices, etc.
- Avoid abstract descriptions or emotional states
- Do not repeat or paraphrase the user's input
- Each element should be a distinct, generatable sound
- Use concrete nouns and clear sound descriptions
- Consider the context but provide diverse sound options

**Examples of good sound elements:**
- "Footsteps on carpet"
- "Distant thunder"
- "Birds chirping"
- "Coffee machine steaming"
- "Pages turning"
- "Wind through trees"
- "Distant conversation"
- "Water dripping"
- "Fire crackling"
- "Traffic sounds"

**Examples of what NOT to generate:**
- "Joyful atmosphere" (too abstract)
- "Christmas morning excitement" (scene description)
- "Child's pure delight" (emotional state)
- "Excited squeal" (repeating user input)

User input: {user_input}
Mode: {mode}

Generate 5 distinct sound elements that could complement this scene:
"""
        else:
            prompt = f"""
You are an expert in soundscape and music design. The user may input in Chinese or English. Your task is:
1. Understand the user's intent and context from the following mode and input.
2. For the stage: {stage}, generate a list of 5 concise, relevant, diverse, and high-quality options in ENGLISH only (even if the user input is in Chinese).
3. Each option should be a short phrase, no more than 10 English words.
4. If the user input is in Chinese, you must first understand it, then output the options in English, not Chinese.
5. Only return a JSON array of strings, e.g. ["option1", "option2", ...]. No extra text.
- mode: {mode}
- user input: {user_input}
"""
        
        # 尝试所有可用模型
        for model_attempt in range(len(self.models)):
            current_model = self._get_current_model()
            print(f"🔧 尝试模型: {current_model}")
            
            max_retries = 2  # 每个模型最多重试2次
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=current_model,
                        contents=prompt
                    )
                    raw_response_text = response.text or ""
                    json_match = re.search(r'```json\\n([\s\S]*?)\\n```', raw_response_text)
                    if json_match:
                        json_string = json_match.group(1).strip()
                    else:
                        start = raw_response_text.find('[')
                        end = raw_response_text.rfind(']')
                        if start != -1 and end != -1 and end > start:
                            json_string = raw_response_text[start:end+1].strip()
                        else:
                            json_string = raw_response_text.strip()
                    options = json.loads(json_string)
                    if isinstance(options, list) and all(isinstance(opt, str) for opt in options):
                        return options
                    return fallback_options.get(stage, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
                except Exception as e:
                    print(f"Error in generate_options (model: {current_model}, attempt {attempt + 1}): {str(e)}")
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        print(f"⚠️  API 配额限制，尝试下一个模型...")
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) + random.uniform(1, 3)
                            print(f"⏳ 等待 {wait_time:.1f} 秒后重试...")
                            time.sleep(wait_time)
                            continue
                        else:
                            # 切换到下一个模型
                            self._switch_to_next_model()
                            break
                    else:
                        print(f"❌ 其他错误，使用 fallback 选项")
                        return fallback_options.get(stage, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
            # 如果当前模型失败，继续尝试下一个模型
            if model_attempt < len(self.models) - 1:
                continue
        # 所有模型都失败了，返回 fallback
        print(f"❌ 所有模型都失败，使用 fallback 选项")
        return fallback_options.get(stage, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])

    async def generate_musicgen_options(self, stage: str, user_input: str = "") -> List[str]:
        # 为 MusicGen 提供 fallback 选项
        fallback_options = {
            'genre': ["Ambient", "Classical", "Jazz", "Electronic", "Folk"],
            'instruments': ["Piano", "Strings", "Synth", "Guitar", "Drums"],
            'tempo': ["Slow", "Medium", "Fast", "Variable", "Steady"],
            'usage': ["Background", "Focus", "Relaxation", "Study", "Sleep"]
        }
        
        prompt = f"""
You are an expert in music generation. Generate 5 diverse and creative options for the {stage} stage of music generation.
Each option should be a single English word or short phrase (max 3 words).
Only return a JSON array of strings, e.g. ["option1", "option2", ...].
User input: {user_input}
"""
        
        # 尝试所有可用模型
        for model_attempt in range(len(self.models)):
            current_model = self._get_current_model()
            print(f"🔧 尝试模型: {current_model}")
            
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=current_model,
                        contents=prompt
                    )
                    raw_response_text = response.text or ""
                    json_match = re.search(r'```json\\n([\s\S]*?)\\n```', raw_response_text)
                    if json_match:
                        json_string = json_match.group(1).strip()
                    else:
                        start = raw_response_text.find('[')
                        end = raw_response_text.rfind(']')
                        if start != -1 and end != -1 and end > start:
                            json_string = raw_response_text[start:end+1].strip()
                        else:
                            json_string = raw_response_text.strip()
                    options = json.loads(json_string)
                    if isinstance(options, list) and all(isinstance(opt, str) for opt in options):
                        return options
                    return fallback_options.get(stage, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
                except Exception as e:
                    print(f"Error in generate_musicgen_options (model: {current_model}, attempt {attempt + 1}): {str(e)}")
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) + random.uniform(1, 3)
                            time.sleep(wait_time)
                            continue
                        else:
                            self._switch_to_next_model()
                            break
                    else:
                        return fallback_options.get(stage, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
            if model_attempt < len(self.models) - 1:
                continue
        return fallback_options.get(stage, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])

    async def generate_inspiration_chips(self, mode: str, user_input: str = "") -> List[str]:
        """
        生成随机的inspiration chips，用于MainScreen的提示选项
        """
        if mode == 'asmr':
            prompt = f"""
For 'asmr':
- Generate 6 inspiration chips for ASMR soundscape creation.
- At least 5 out of 6 must be classic ASMR triggers or sound types, such as: Tapping, Brushing, Page turning, Ear cleaning, Crinkling, Hand movements, Water sounds, Glove sounds, Typing, Spray sounds, Personal attention, Hair brushing, Face touching, Light triggers, Scalp massage, Whispering, Scratching, Plastic crinkling, Mic brushing, Roleplay: doctor, Roleplay: haircut, Roleplay: spa.
- At most 1 chip can be a gentle, tactile environmental sound (e.g. Gentle rain tapping, Soft wind, Distant thunder, Footsteps on carpet, Water dripping, Fire crackling, Pages turning in a quiet library).
- Do not generate poetic lines, scenes, or abstract moods. Each chip must be a concrete ASMR sound or trigger, 1-3 words only.
- Each time you are called, generate a new, diverse set of chips. Avoid repeating the same chips as previous calls.
- Example chips: Tapping, Brushing, Page turning, Ear cleaning, Crinkling, Whispering
User input: {user_input}
Only return a JSON array of 6 strings.
"""
        elif mode == 'story':
            prompt = f"""
For 'story':
- Generate 6 inspiration chips for story-based soundscape creation.
- Each chip should be a vivid, evocative memory fragment, scene, or narrative starter, such as: "The first snowfall you remember", "Grandma’s kitchen on Sunday morning", "Laughter echoing in a sunlit park", "A rainy night in a small town", "The day you met your best friend", "A quiet library at dusk", "The sound of waves on a childhood beach", "A summer afternoon, cicadas singing", "The last day of school", "A secret hideout in the woods".
- Avoid abstract moods, pure nature scenes, or generic phrases. Each chip should be a specific, story-like moment or memory, 5-12 words.
- Each chip must be unique and cover different types of scenes (e.g. family, childhood, adventure, friendship, seasons, city, countryside, school, holidays, etc.).
- Do not repeat the same theme or setting in more than one chip.
- If user_input is provided, make at least 2 chips inspired by it, but do not simply paraphrase it.
- Example chips: The first snowfall you remember, Grandma’s kitchen on Sunday morning, Laughter echoing in a sunlit park, A rainy night in a small town, The day you met your best friend, A quiet library at dusk
User input: {user_input}
Only return a JSON array of 6 strings.
"""
        else:
            prompt = f"""
You are an expert in creating practical soundscapes for audio generation. Generate 6 diverse and inspiring prompts that users can click to get started with sound generation. Focus on concrete, generatable sounds rather than abstract concepts.

**CRITICAL GUIDELINES FOR STABLE AUDIO MODEL:**
- Use only 2-3 core sound elements maximum to avoid compositional failure
- Focus on concrete, physical sounds that the model can actually generate
- Avoid abstract emotional or atmospheric descriptions
- Use specific, clear sound descriptions rather than poetic language
- Emphasize steady, continuous sounds rather than complex interactions

**Types of inspiration to include:**
1. **Natural environments** - Rain, wind, ocean waves, forest sounds, thunder
2. **Urban environments** - City traffic, cafe sounds, office ambience, street sounds
3. **Domestic spaces** - Kitchen sounds, home ambience, household activities
4. **Mechanical sounds** - Machinery, engines, tools, industrial sounds
5. **Simple interactions** - Footsteps, door sounds, paper rustling, water dripping
6. **Steady background sounds** - Humming, buzzing, flowing water, steady wind

**Requirements:**
- Each prompt should be 5-15 words long
- Focus on 2-3 specific sound elements maximum
- Use concrete nouns and clear descriptions
- Avoid abstract modifiers like "gentle", "soft", "distant" - use "steady", "smooth", "background" instead
- Make them practical and generatable
- Consider the mode: {mode}
- If user_input is provided, make some prompts related to it
- Each time you are called, generate a new, diverse set of chips

**Mode-specific considerations:**
- For 'focus': Include steady, non-distracting sounds like rain, white noise, office ambience
- For 'relax': Include smooth, natural sounds like ocean waves, gentle wind, flowing water
- For 'story': Include atmospheric but concrete sounds like footsteps, door creaks, paper rustling
- For 'music': Include rhythmic, steady sounds like drumming, humming, mechanical rhythms
- For 'asmr': See above for triggers and environmental sounds.

**Examples of good prompts:**
- "Steady rain with distant thunder"
- "Ocean waves with seagull calls"
- "Cafe ambience with coffee machine"
- "Forest sounds with bird songs"
- "City traffic with car horns"
- "Kitchen sounds with water running"

**Examples of bad prompts (avoid these):**
- "The quiet before dawn" (too abstract)
- "Gentle whispers of the wind" (abstract modifier)
- "A steampunk workshop where brass gears whisper secrets" (too complex, poetic)
- "The calm before a thunderstorm" (abstract emotional state)

User input: {user_input}

Only return a JSON array of 6 strings, e.g. ["prompt1", "prompt2", ...].
"""
        # LLM采样参数提升多样性（已移除generationConfig，避免API报错）
        response = self.client.models.generate_content(
            model=self._get_current_model(),
            contents=prompt
        )
        raw_response_text = response.text or ""
        json_match = re.search(r'```json\\n([\s\S]*?)\\n```', raw_response_text)
        if json_match:
            json_string = json_match.group(1).strip()
        else:
            start = raw_response_text.find('[')
            end = raw_response_text.rfind(']')
            if start != -1 and end != -1 and end > start:
                json_string = raw_response_text[start:end+1].strip()
            else:
                json_string = raw_response_text.strip()
        chips = json.loads(json_string)
        if isinstance(chips, list) and all(isinstance(chip, str) for chip in chips):
            return chips
        return self._get_fallback_inspiration_chips()

    def _get_fallback_inspiration_chips(self) -> List[str]:
        """获取fallback的inspiration chips"""
        return [
            "Steady rain with distant thunder",
            "Ocean waves with seagull calls", 
            "Cafe ambience with coffee machine",
            "Forest sounds with bird songs",
            "City traffic with car horns",
            "Kitchen sounds with water running"
        ]

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
            response = self.client.models.generate_content(
                model=self._get_current_model(),
                contents=prompt
            )
            raw = response.text or ""
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
        return ", ".join([str(p) for p in parts if p is not None])

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
            response = self.client.models.generate_content(
                model=self._get_current_model(),
                contents=prompt
            )
            raw = response.text or ""
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

    async def edit_prompt(self, current_prompt: str, edit_instruction: str, mode: str = "default", is_story: bool = False) -> str:
        """
        使用AI编辑prompt或narrative
        """
        try:
            content_type = "narrative" if is_story else "audio description"
            prompt = f"""
You are an expert in {content_type} and storytelling. The user wants to edit their current {content_type} based on their instruction.

Current {content_type}: "{current_prompt}"
User's edit instruction: "{edit_instruction}"
Mode: {mode}

Please edit the {content_type} according to the user's instruction. Keep the core meaning but apply the requested changes. Return only the edited {content_type}, no explanations.

Examples for {content_type} editing:
- If user says "make it shorter", condense the {content_type}
- If user says "add more details", expand with more atmospheric elements
- If user says "make it more poetic", add lyrical language
- If user says "make it more dramatic", add intensity and emotion
- If user says "add more emotion", enhance emotional elements
- If user says "make it more intense", add dramatic tension

Edited {content_type}:"""
            
            response = self.client.models.generate_content(
                model=self._get_current_model(),
                contents=prompt
            )
            
            edited_prompt = response.text.strip() if response and response.text else current_prompt
            return edited_prompt
            
        except Exception as e:
            print(f"Error in edit_prompt: {e}")
            # 如果AI编辑失败，返回原始prompt
            return current_prompt

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