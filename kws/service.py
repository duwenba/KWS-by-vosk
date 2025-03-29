import time
from pathlib import Path
from typing import Optional, Dict, Callable
from loguru import logger
from .audio import AudioStream
from .recognition import SpeechRecognizer
from .model_manager import ModelManager

class KeywordService:
    def __init__(self, model_path: Optional[str] = None):
        self._setup_logger()
        self.model_manager = ModelManager()
        model_path = model_path or self.model_manager.ensure_model_exists()
        self.audio_stream = AudioStream()
        self.recognizer = SpeechRecognizer(model_path)
        self.actions: Dict[str, Callable] = {}
        self.is_running = True

    def _setup_logger(self) -> None:
        """配置日志记录"""
        log_path = Path.cwd() / 'data' / 'logs'
        log_path.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_path / 'kws.log'),
            rotation='1 day',
            retention='7 days',
            level='INFO'
        )

    def register_action(self, keyword: str, action: Callable) -> None:
        """注册关键词触发动作"""
        keyword = keyword.replace(' ', '')  # 去除所有空格
        self.actions[keyword] = action
        logger.info(f'注册关键词动作: {keyword}')

    def _process_recognition(self, audio_data) -> None:
        """处理语音识别结果"""
        text = self.recognizer.process_audio(audio_data)
        if text:
            text = text.replace(' ', '')  # 去除所有空格
            logger.debug(f'识别结果: {text}')
            # 遍历所有注册的关键词进行匹配
            for keyword, action in self.actions.items():
                if keyword in text:
                    logger.info(f'检测到关键词: {keyword}')
                    try:
                        action()
                        logger.info('成功执行关键词动作')
                    except Exception as e:
                        logger.error(f'执行关键词动作失败: {e}')
                    break  # 找到匹配的关键词后就退出循环

    def start(self) -> None:
        """启动关键词检测服务"""
        logger.info('启动关键词检测服务')
        self.audio_stream.start(self._process_recognition)

    def stop(self) -> None:
        """停止关键词检测服务"""
        logger.info('停止关键词检测服务')
        self.is_running = False
        self.audio_stream.stop()

    def run_forever(self) -> None:
        """持续运行服务"""
        try:
            self.start()
            # 保持主线程运行
            while self.is_running:
                time.sleep(1)  # 可以根据需要调整休眠时间
        except KeyboardInterrupt:
            logger.info('被用户中断')
        finally:
            self.stop()