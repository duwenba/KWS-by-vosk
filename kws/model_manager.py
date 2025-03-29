import os
import shutil
import requests
from pathlib import Path
from tqdm import tqdm
from loguru import logger

class ModelManager:
    VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"
    
    def __init__(self):
        self.app_dir = Path(__file__).parent.parent
        self.model_dir = self.app_dir / 'data' / 'model'
        self.download_dir = self.app_dir / 'data' / 'downloads'
    
    def ensure_model_exists(self) -> str:
        """确保模型存在，如果不存在则下载"""
        if not self._check_model_exists():
            logger.info('模型不存在，开始下载...')
            self._download_model()
            self._extract_model()
        return str(self.model_dir)
    
    def _check_model_exists(self) -> bool:
        """检查模型是否存在"""
        if not self.model_dir.exists():
            return False
        # 检查模型文件夹是否包含必要文件
        required_files = ['am', 'conf', 'graph', 'ivector']
        return all((self.model_dir / file).exists() for file in required_files)
    
    def _download_model(self) -> None:
        """下载模型文件"""
        self.download_dir.mkdir(parents=True, exist_ok=True)
        zip_path = self.download_dir / 'model.zip'
        
        response = requests.get(self.VOSK_MODEL_URL, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as f, tqdm(
            desc='下载模型',
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                pbar.update(size)
    
    def _extract_model(self) -> None:
        """解压模型文件"""
        zip_path = self.download_dir / 'model.zip'
        extract_path = self.download_dir / 'temp'
        
        # 清理旧文件
        if self.model_dir.exists():
            shutil.rmtree(self.model_dir)
        if extract_path.exists():
            shutil.rmtree(extract_path)
        
        # 解压文件
        logger.info('正在解压模型文件...')
        shutil.unpack_archive(zip_path, extract_path)
        
        # 移动文件到模型目录
        model_folder = next(extract_path.iterdir())  # 获取解压后的文件夹
        shutil.move(str(model_folder), str(self.model_dir))
        
        # 清理临时文件
        shutil.rmtree(extract_path)
        zip_path.unlink()
        logger.info('模型文件解压完成')