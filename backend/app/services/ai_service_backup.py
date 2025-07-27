��from google import genai
import os
import json
import re
import time
import random
from typing import List, Dict, Optional

class AIService:
    def __init__(self):
        self.client = genai.Client()
        # Y*NY	�!j�W�	cM����S(u'`�c�^��W�NKmՋ�~�g	�
        self.models = [
            "gemini-2.5-flash-lite-preview-06-17",  # gwQb,gHe�vN/ecؚTTϑ P+
            "gemini-2.5-flash",                      # ��^'``�~�b,gHe�v P+
            "gemini-1.5-flash",                      # �_��Y7h�v'`�� P+
            "gemini-2.0-flash-lite",                 # b,gHe�v�TNO�^ߏ�Y(u	�
            "gemini-1.5-pro",                        # YBg�ct�N�R�gTY(u�M���P�6R	�
        ]
        self.current_model_index = 0

    def _get_current_model(self):
        """���SS_MR!j�W"""
        return self.models[self.current_model_index]

    def _switch_to_next_model(self):
        """Rbc0RNN*N!j�W"""
        self.current_model_index = (self.current_model_index + 1) % len(self.models)
        print(f"=�� Rbc0R!j�W: {self._get_current_model()}")
        return self._get_current_model()

    async def parse_scene(self, description: str) -> List[Dict]:
        prompt = f"""
        R�g�NN:Wof�c����c�S@b	g�S���v�X�CQ }�
        {description}
        ���NJSON<h_ԏ�V�S+T�NNW[�k�
        - name: �X�CQ }T�y
        - volume: �ϑ'Y\(0-1)
        - position: MOn("foreground"b"background")
        - duration: c�~�e��(�y)
        :y�O���Q<h_�
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
        # Tv^T�v soundscape description prompt
        fallback_options = {
            'audio_atmosphere': ["In a large empty warehouse", "Deep in a lush rainforest", "Urban street corner at night", "Inside a cozy cafe", "On a snowy mountain peak"],
            'audio_elements': ["Rain", "Footsteps", "Birds chirping", "Thunder", "Wind blowing"],
            'audio_style': ["Natural", "Synthetic", "Mixed", "Organic", "Electronic"],
            'music_genre': ["Ambient", "Classical", "Jazz", "Electronic", "Folk"],
            'music_instruments': ["Piano", "Strings", "Synth", "Guitar", "Drums"],
            'music_tempo': ["Slow", "Medium", "Fast", "Variable", "Steady"],
            'music_usage': ["Background", "Focus", "Relaxation", "Study", "Sleep"]
        }
        if stage in ['mood', 'audio_mood']:
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
        elif stage in ['audio_elements']:
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
Based on the user's input and mode, generate 5 sound element options that are closely related to the user's idea, each with a slight variation or added detail. Do not suggest unrelated sounds or events. Do not simply repeat the original input. Do not include any scene or environment words already mentioned in the atmosphere (such as cafe, rain, afternoon, etc.). Only describe specific sounds or events, not the overall scene or mood.

User input: "A cozy cafe on a rainy afternoon"
Atmosphere: ["Cozy cafe, rainy afternoon", "Warm cafe, rain on windows", "Cafe, soft jazz, rainy day", "Cafe, fresh coffee aroma, rain", "Quiet cafe, foggy windows"]
Examples: [
  "Coffee machine steaming",
  "Pages turning",
  "Barista grinding beans",
  "Distant thunder",
  "Muffled conversation"
]

Now, for the following user input, generate 5 similar sound element options as above.
User input: {user_input}
Only return a JSON array of strings.
- mode: {mode}
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
        
        # \Ջ@b	g�S(u!j�W
        for model_attempt in range(len(self.models)):
            current_model = self._get_current_model()
            print(f"=�'� \Ջ!j�W: {current_model}")
            
            max_retries = 2  # �k*N!j�WgY͑Ջ2!k
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
                        print(f"�&�  API M���P�6R�\ՋNN*N!j�W...")
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) + random.uniform(1, 3)
                            print(f"�# I{�_ {wait_time:.1f} �yT͑Ջ...")
                            time.sleep(wait_time)
                            continue
                        else:
                            # Rbc0RNN*N!j�W
                            self._switch_to_next_model()
                            break
                    else:
                        print(f"L' vQ�N���O(u fallback 	�y�")
                        return fallback_options.get(stage, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])
            # �Y�gS_MR!j�W1Y%���~�~\ՋNN*N!j�W
            if model_attempt < len(self.models) - 1:
                continue
        # @b	g!j�W��1Y%��N�ԏ�V fallback
        print(f"L' @b	g!j�W��1Y%��O(u fallback 	�y�")
        return fallback_options.get(stage, ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"])

    async def generate_musicgen_options(self, stage: str, user_input: str = "") -> List[str]:
        # :N MusicGen �c�O fallback 	�y�
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
        
        # \Ջ@b	g�S(u!j�W
        for model_attempt in range(len(self.models)):
            current_model = self._get_current_model()
            print(f"=�'� \Ջ!j�W: {current_model}")
            
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
        ub��:g�vinspiration chips�(u�NMainScreen�v�c:y	�y�
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
        else:
            prompt = f"""
You are an expert in creating atmospheric and emotional soundscapes. Generate 6 diverse and inspiring prompts that users can click to get started with sound generation. These should be a mix of different types of inspiration:

**Types of inspiration to include:**
1. **Poetic verses** - Short, evocative lines from poetry or literature that capture a mood
2. **Memory fragments** - Personal, nostalgic moments that evoke specific atmospheres
3. **Atmospheric descriptions** - Rich, sensory descriptions of environments
4. **Emotional states** - Abstract feelings and moods
5. **Imaginary scenes** - Creative, fantastical settings
6. **Sensory experiences** - Multi-sensory descriptions

**Requirements:**
- Mix different styles: some poetic, some descriptive, some abstract
- Each prompt should be 5-20 words long
- Make them creative, inspiring, and diverse
- Consider the mode: {mode}
- If user_input is provided, make some prompts related to it
- Avoid generic phrases, be specific and evocative
- Each time you are called, generate a new, diverse set of chips. Avoid repeating the same chips as previous calls.

**Mode-specific considerations:**
- For 'focus': Include concentration, productivity, clarity themes
- For 'relax': Include peace, calm, soothing themes  
- For 'story': Include narrative, dramatic, cinematic themes
- For 'music': Include rhythmic, melodic, harmonic themes
- For 'asmr': See above for triggers and environmental sounds.

User input: {user_input}

Only return a JSON array of 6 strings, e.g. ["prompt1", "prompt2", ...].
"""
        # LLMǑ7h�Spe�cGSY7h'`��]�yd�generationConfig��MQAPI�b�	�
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
        """���Sfallback�vinspiration chips"""
        return [
            "The rain falls like silver threads on cobblestone streets",
            "Grandma's kitchen on Sunday morning, cinnamon in the air",
            "A library where time stands still, dust motes dance in sunbeams",
            "The quiet before dawn, when the world holds its breath",
            "A steampunk workshop where brass gears whisper secrets",
            "Fresh snow crunching underfoot, breath visible in cold air",
        ]

    def analyze_music_prompt_layers(self, user_text: str = '', extra_fields: dict = None) -> dict:
        """
        O(u LLM R�g(u7b��eQ�R�:N genre, style, mood, feeling, instrumentation, tempo, bpm, production_quality, artist_style0
        OHQTv^MR�z Oeg�v�~�gSW[�k��Y genre, instruments, tempo, usage	��(W LLM prompt R�g�e\ُ�NW[�k�b�c0R userInput MRb�0
        """
        extra_fields = extra_fields or {}
        # �b�c�~�gSW[�k:NMR
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
        # �b�c0R user_text MRb�
        full_text = (prefix + '. ' if prefix else '') + (user_text or '')
        prompt = '''
`O/fNMOv��~�v�PNt���[�TMeta MusicGen!j�W�vPrompt�]z^0
��\�NN�e,g㉄g:N�PNub�v8h�_CQ }����QJSON�
- genre: {|�W��Y ambient, rock, cinematic, jazz I{��e	�
- style: Θ<h��Y 90s alternative, lo-fi, synthwave I{��e	�
- mood: �`�~��Y melancholy, peaceful, energetic, epic I{��e	�
- feeling: �~{�aɉ��Y lonely, nostalgic, reflective, dreamy I{��e	�
- instrumentation: PNhV��Y acoustic guitar, synth pads, string orchestra I{��e�pe�~	�
- tempo: ��^�c����Y slow tempo, fast tempo, driving beat I{��e	�
- bpm: BPMpe<P��Y 120, 95 I{�peW[	�
- production_quality: 6R\O(�ϑ��Y high-quality production, vintage recording, clean mix I{��e	�
- artist_style: z�/g�[Θ<h��Y in the style of Taylor Swift, inspired by Hans Zimmer I{��e	�
�Sԏ�VJSON��e��ʑ0
�e,g�''' + full_text
        try:
            response = self.client.models.generate_content(
                model=self._get_current_model(),
                contents=prompt
            )
            raw = response.text or ""
            # \Ջ�c�SJSON
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
            # (u�~�gSW[�ke�hQ/���v LLM �~�g
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
        �g�^ؚ�Ow MusicGen Prompt�RB\���Q���SR��0
        """
        parts = []
        # ,{NB\�{|�WNΘ<h
        if genre:
            parts.append(genre)
        if style:
            parts.append(style)
        # ,{�NB\��`�~Naɉ
        if mood:
            parts.append(mood)
        if feeling:
            parts.append(feeling)
        # ,{	NB\�M�hV
        if instrumentation:
            parts.extend(instrumentation)
        # ,{�VB\���^N��OY
        if tempo:
            parts.append(tempo)
        if bpm:
            parts.append(f"{bpm} BPM")
        # ,{�NB\�6R\O(�ϑNz�/g�[Θ<h
        if production_quality:
            parts.append(production_quality)
        if artist_style:
            parts.append(artist_style)
        # �~>\e�EQ
        parts.append("high-quality, rich, layered, immersive music")
        return ", ".join([str(p) for p in parts if p is not None])

    def analyze_audiogen_prompt_layers(self, user_text: str = '', extra_fields: dict = None) -> dict:
        """
        O(u LLM R�g(u7b��eQ�R�:N AudioGen �N'Y/e�g�pitch, pattern, intensity, acoustic, location0
        OHQTv^MR�z Oeg�v�~�gSW[�k�(W LLM prompt R�g�e\ُ�NW[�k�b�c0R user_text MRb�0
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
`O/fNMONLuv��~�v�He�c:y͋�]z^�N:NMeta AudioGeng�R0��\�NN�e,g㉄g:N�N'Y/e�g�
- pitch: �X�v���s��Y high-pitched, deep rumble, low growl I{��e	�
- pattern: ��OY/͑Y'`��Y intermittent beeping, continuous hum, rhythmic tapping I{��e	�
- intensity: �ϑ/�R�^��Y faint, distant explosion, deafening roar, gradually increasing in volume I{��e	�
- acoustic: �Xf[yr'`��Y muffled sound, crisp and clear, metallic echo, hollow wooden knock I{��e	�
- location: MOn/�s�X��Y in a vast, empty cavern, on a busy city street, inside a small wooden box I{��e	�
�Sԏ�VJSON��e��ʑ0
�e,g�''' + full_text
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
            # (u�~�gSW[�ke�hQ/���v LLM �~�g
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
        �g�^ؚ�Ow AudioGen Prompt�RB\���Q���SR��0
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
        O(uAI��promptbnarrative
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
            # �Y�gAI��1Y%��ԏ�V�S�Yprompt
            return current_prompt

def get_instruments_from_ai(atmosphere: Optional[str], mood: Optional[str], elements: Optional[List[str]], user_input: Optional[str], reference_era: Optional[str]) -> List[str]:
    """
    �(u AI e�hQPNhV�dkY:N mock��S�[�c Gemini/GPT/OpenAI	�0
    """
    # TODO: �[E��S(u OpenAI/Gemini API �(u
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
    �~�gS�b�c AudioGen prompt��(u�N�He/�s�X�ub0
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
