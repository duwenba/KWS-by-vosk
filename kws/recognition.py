import json
from pathlib import Path
from typing import Optional
from vosk import Model, KaldiRecognizer
from loguru import logger
from .config import config

class SpeechRecognizer:
    def __init__(self, model_path: Optional[str] = None):
        # 默认模型路径为应用目录下的data/model
        if model_path:
            self.model_path = model_path
        else:
            app_dir = Path(__file__).parent.parent
            self.model_path = str(app_dir / 'data' / 'model')
        self.model: Optional[Model] = None
        self.recognizer: Optional[KaldiRecognizer] = None
        self._initialize()

    def _initialize(self) -> None:
        """初始化语音识别模型"""
        try:
            if not Path(self.model_path).exists():
                raise FileNotFoundError(f'模型文件夹不存在: {self.model_path}')

            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, config.audio.sample_rate)
            logger.info('语音识别模型已加载')
        except Exception as e:
            logger.error(f'初始化语音识别模型失败: {e}')
            raise

    def process_audio(self, audio_data) -> Optional[str]:
        """处理音频数据并返回识别结果"""
        if self.recognizer is None:
            return None

        try:
            # 确保音频数据是字节格式
            if isinstance(audio_data, float):
                audio_data = (audio_data * 32767)
            elif not isinstance(audio_data, bytes):
                audio_data = (audio_data * 32767).astype('int16').tobytes()

            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').strip()
                if text:
                    return text
            else:
                # 部分结果，用于实时反馈
                result = json.loads(self.recognizer.PartialResult())
                text = result.get('partial', '').strip()
                if text:
                    return text
        except Exception as e:
            logger.error(f'处理音频数据失败: {e}')

        return None

    def reset(self) -> None:
        """重置识别器状态"""
        if self.recognizer is not None:
            self.recognizer.Reset()