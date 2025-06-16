from pydub import AudioSegment
import pydub.effects
import numpy as np
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AudioEffectsService:
    def __init__(self):
        self.effects = {
            'reverb': self.apply_reverb,
            'echo': self.apply_echo,
            'fade': self.apply_fade,
            'volume': self.adjust_volume
        }

    def apply_reverb(self, audio: AudioSegment, params: Dict[str, Any]) -> AudioSegment:
        """
        应用混响效果
        params:
            - room_size: 混响房间大小 (0.0-1.0)
            - damping: 阻尼系数 (0.0-1.0)
            - wet_level: 湿信号电平 (0.0-1.0)
            - dry_level: 干信号电平 (0.0-1.0)
        """
        try:
            room_size = params.get('room_size', 0.5)
            damping = params.get('damping', 0.5)
            wet_level = params.get('wet_level', 0.3)
            dry_level = params.get('dry_level', 0.7)
            
            # 使用pydub的reverb效果
            return pydub.effects.reverb(audio, room_size=room_size, damping=damping, 
                         wet_level=wet_level, dry_level=dry_level)
        except Exception as e:
            logger.error(f"应用混响效果失败: {str(e)}")
            return audio

    def apply_echo(self, audio: AudioSegment, params: Dict[str, Any]) -> AudioSegment:
        """
        应用回声效果
        params:
            - delay: 延迟时间(毫秒)
            - decay: 衰减系数 (0.0-1.0)
            - repeats: 重复次数
        """
        try:
            delay = params.get('delay', 300)
            decay = params.get('decay', 0.5)
            repeats = params.get('repeats', 3)
            
            # 使用pydub的echo效果
            return pydub.effects.echo(audio, delay=delay, decay=decay, repeats=repeats)
        except Exception as e:
            logger.error(f"应用回声效果失败: {str(e)}")
            return audio

    def apply_fade(self, audio: AudioSegment, params: Dict[str, Any]) -> AudioSegment:
        """
        应用淡入淡出效果
        params:
            - fade_in: 淡入时长(毫秒)
            - fade_out: 淡出时长(毫秒)
        """
        try:
            fade_in = params.get('fade_in', 1000)
            fade_out = params.get('fade_out', 1000)
            
            # 应用淡入淡出
            return audio.fade_in(fade_in).fade_out(fade_out)
        except Exception as e:
            logger.error(f"应用淡入淡出效果失败: {str(e)}")
            return audio

    def adjust_volume(self, audio: AudioSegment, params: Dict[str, Any]) -> AudioSegment:
        """
        调整音量
        params:
            - volume_db: 音量调整值(dB)
        """
        try:
            volume_db = params.get('volume_db', 0)
            return audio + volume_db
        except Exception as e:
            logger.error(f"调整音量失败: {str(e)}")
            return audio

    def process_audio(self, audio: AudioSegment, effects_config: Dict[str, Dict[str, Any]]) -> AudioSegment:
        """
        处理音频，应用多个效果
        effects_config: {
            'effect_name': {
                'param1': value1,
                'param2': value2
            }
        }
        """
        try:
            processed_audio = audio
            
            for effect_name, params in effects_config.items():
                if effect_name in self.effects:
                    processed_audio = self.effects[effect_name](processed_audio, params)
                    
            return processed_audio
        except Exception as e:
            logger.error(f"音频处理失败: {str(e)}")
            return audio 