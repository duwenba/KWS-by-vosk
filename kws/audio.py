import queue
import threading
import numpy as np
import sounddevice as sd
from loguru import logger
from typing import Optional, Callable
from .config import config

class AudioStream:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_running = False
        self._stream: Optional[sd.InputStream] = None
        self._thread: Optional[threading.Thread] = None

    def start(self, callback: Callable[[np.ndarray], None]) -> None:
        """启动音频流"""
        if self.is_running:
            return

        def audio_callback(indata: np.ndarray, frames: int, time: dict, status: sd.CallbackFlags) -> None:
            """音频回调函数"""
            if status:
                logger.warning(f'音频回调状态: {status}')
            # 将音频数据放入队列
            self.audio_queue.put(indata.copy())

        try:
            self._stream = sd.InputStream(
                device=config.audio.device,
                channels=config.audio.channels,
                samplerate=config.audio.sample_rate,
                dtype=config.audio.dtype,
                blocksize=config.audio.blocksize,
                callback=audio_callback
            )
            self._stream.start()
            self.is_running = True

            # 启动处理线程
            self._thread = threading.Thread(target=self._process_audio, args=(callback,))
            self._thread.daemon = True
            self._thread.start()
            
            logger.info('音频流已启动')
        except Exception as e:
            logger.error(f'启动音频流失败: {e}')
            self.stop()

    def _process_audio(self, callback: Callable[[np.ndarray], None]) -> None:
        """处理音频数据"""
        while self.is_running:
            try:
                # 从队列获取音频数据
                audio_data = self.audio_queue.get(timeout=1)
                # 调用回调函数处理音频数据
                callback(audio_data)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f'处理音频数据失败: {e}')

    def stop(self) -> None:
        """停止音频流"""
        self.is_running = False
        # 清空音频队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        # 停止并关闭音频流
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                logger.error(f'关闭音频流时发生错误: {e}')
            finally:
                self._stream = None
        # 等待处理线程结束
        if self._thread is not None:
            if self._thread is not threading.current_thread():
                self._thread.join(timeout=2)
            self._thread = None
        logger.info('音频流已停止')