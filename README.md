# 语音关键词检测服务

一个基于Python的离线语音关键词检测服务，使用Vosk作为语音识别引擎，可以在后台运行并检测特定关键词。

## 功能特点

- 实时语音采集和识别
- 离线语音识别，无需网络连接
- 可配置的关键词和触发动作
- 低资源占用，适合后台运行
- 完整的日志记录系统

## 安装说明

1. 确保已安装Python 3.12或更高版本
2. 安装uv包管理工具：
   ```bash
   pip install uv
   ```
3. 克隆项目并安装依赖：
   ```bash
   uv pip install .
   ```
4. 下载Vosk模型：
   - 从[Vosk模型库](https://alphacephei.com/vosk/models)下载中文模型
   - 解压模型文件到应用目录下的`data/model`目录

## 配置说明

配置文件位于应用目录下的`data/config.yaml`，包含以下配置项：

```yaml
audio:
  device: 0            # 音频输入设备ID
  sample_rate: 16000   # 采样率
  channels: 1          # 声道数
  dtype: float32       # 数据类型
  blocksize: 8000      # 音频块大小

keyword:
  trigger_word: 你好小艺  # 触发词
  confidence_threshold: 0.5  # 置信度阈值
```

## 使用示例

```python
from kws.service import KeywordService

def my_action():
    print('检测到关键词！')

# 创建服务实例
service = KeywordService()

# 注册关键词动作
service.register_action('你好小艺', my_action)

# 运行服务
service.run_forever()
```

## 日志

服务日志保存在应用目录下的`data/logs`目录下，默认保留7天的日志记录。

## 注意事项

- 首次运行前请确保已下载并配置Vosk模型
- 确保系统有可用的音频输入设备
- 可以通过配置文件调整音频参数和关键词设置