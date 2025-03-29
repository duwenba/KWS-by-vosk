import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AudioConfig:
    device: int = 0  # 音频输入设备ID
    sample_rate: int = 16000  # 采样率
    channels: int = 1  # 单声道
    dtype: str = 'float32'  # 数据类型
    blocksize: int = 8000  # 每次读取的音频块大小

# @dataclass
# class KeywordConfig:
#     trigger_word: str = '你好'  # 触发词
#     confidence_threshold: float = 0.5  # 置信度阈值

class Config:
    def __init__(self, config_path: str | None = None):
        if config_path:
            self.config_path = config_path
        else:
            app_dir = Path(__file__).parent.parent
            self.config_path = str(app_dir / 'data' / 'config.yaml')
        self.audio = AudioConfig()
        self._load_config()

    def _load_config(self) -> None:
        """从配置文件加载配置"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                if config_data:
                    audio_config = config_data.get('audio', {})
                    keyword_config = config_data.get('keyword', {})
                    
                    # 更新音频配置
                    for key, value in audio_config.items():
                        if hasattr(self.audio, key):
                            setattr(self.audio, key, value)
                    
                    # # 更新关键词配置
                    # for key, value in keyword_config.items():
                    #     if hasattr(self.keyword, key):
                    #         setattr(self.keyword, key, value)

    def save_config(self) -> None:
        """保存配置到文件"""
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            'audio': {
                'device': self.audio.device,
                'sample_rate': self.audio.sample_rate,
                'channels': self.audio.channels,
                'dtype': self.audio.dtype,
                'blocksize': self.audio.blocksize,
            },
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)

# 全局配置实例
config = Config()